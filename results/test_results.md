# Test results

## Environment
Tests use only bundled synthetic data. Run with:

```bash
python -m unittest discover -s tests -v
```

## Cases
| Test | Type | Expected result | What it verifies |
|---|---|---|---|
| T1 | Baseline search | UCS and A* both find a path with equal optimal cost | Search correctness on same state space |
| T2 | Baseline CSP | Every sample leak receives a qualified available team and permitted slot | Valid assignment and hard constraints |
| T3 | Changed/constrained case | No assignment when a leak requires unavailable “underwater welding” skill | Failure handling and infeasible CSP |
| T4 | Inference | High-severity fact derives `urgent(X)` and then `inspect_first(X)`; unrelated entity is not inferred | Rule correctness |
| T5 | Ranking | Critical report affecting a critical service ranks first in sample data | Priority ordering |

## Observed outcomes
**Executed during package creation:** exit code `0`. Output:

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 718, in _warm_feature_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 509, in _warm_drawing_and_image_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/generated/interface/models.py", line 32861, in bring_to_front
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/remote.py", line 764, in __call__
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/client.py", line 175, in call
artifact_tool.rpc.client.RemoteError: Element ordering requires an owning element collection.
test_constrained_csp_failure (test_planner.PlannerTests.test_constrained_csp_failure) ... ok
test_csp_valid_assignment (test_planner.PlannerTests.test_csp_valid_assignment) ... ok
test_inference_queries (test_planner.PlannerTests.test_inference_queries) ... ok
test_priority_ranking (test_planner.PlannerTests.test_priority_ranking) ... ok
test_search_algorithms_same_optimal_cost (test_planner.PlannerTests.test_search_algorithms_same_optimal_cost) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.001s

OK
```

Re-run in the target environment before submission.

## Failure case
T3 is intentionally infeasible: no team has the required skill, so the solver returns no assignment and a trace indicating failure. This is a correct failure outcome, not a crash.

## Practical limitation
The grid is a small abstraction and does not represent actual street topology, distances, traffic, leak probability, or real team response times. The priority formula is illustrative and should be calibrated before operational use.
