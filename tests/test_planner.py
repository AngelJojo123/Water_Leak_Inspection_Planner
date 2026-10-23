import unittest
from src.planner import (load_sample_data, rank_leaks, solve_csp, validate_assignment,
                         forward_chain, build_grid_problem, ucs, astar)

class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.data = load_sample_data()

    def test_search_algorithms_same_optimal_cost(self):
        start, goals, blocked, width, height = build_grid_problem()
        a = ucs(start, goals, blocked, width, height)
        b = astar(start, goals, blocked, width, height)
        self.assertTrue(a["found"] and b["found"])
        self.assertEqual(a["cost"], b["cost"])
        self.assertEqual(a["path"][0], start)
        self.assertIn(b["path"][-1], goals)

    def test_csp_valid_assignment(self):
        result, trace = solve_csp(self.data["leaks"], self.data["teams"], self.data["slots"])
        self.assertEqual(len(result), len(self.data["leaks"]))
        self.assertTrue(validate_assignment(result, self.data["leaks"], self.data["teams"], self.data["slots"]))

    def test_constrained_csp_failure(self):
        leaks = [dict(self.data["leaks"][0], **{"Required skill":"underwater welding"})]
        result, trace = solve_csp(leaks, self.data["teams"], self.data["slots"])
        self.assertEqual(result, [])
        self.assertTrue(any("No satisfying" in x for x in trace))

    def test_inference_queries(self):
        facts = [("reported","L-1"),("high_severity","L-1")]
        conclusions, trace = forward_chain(facts)
        self.assertIn(("urgent","L-1"), conclusions)
        self.assertIn(("inspect_first","L-1"), conclusions)
        self.assertNotIn(("urgent","L-2"), conclusions)

    def test_priority_ranking(self):
        ranked = rank_leaks(self.data["leaks"])
        self.assertEqual(ranked[0]["Leak ID"], "L-101")

if __name__ == "__main__":
    unittest.main()
