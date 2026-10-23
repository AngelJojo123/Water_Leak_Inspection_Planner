# Water Leak Inspection Planner

**AI prototype for SDG 6 and SDG 11**  
A reproducible educational prototype that prioritises synthetic water-leak reports, compares UCS and A* route search, allocates inspection teams using a CSP, and derives urgency conclusions with forward chaining.

## Team details
- Team name: _Replace before submission_
- Member names and roll numbers: _Replace before submission_
- Instructor/repository link: _Add your GitHub repository URL and invite the instructor_

## SDG alignment
- **SDG 6 – Clean Water and Sanitation:** leak inspection prioritisation can support reduced water loss and improved water-use efficiency (relevant to target 6.4).
- **SDG 11 – Sustainable Cities and Communities:** timely inspection can support resilient urban water infrastructure and continuity of essential services.
These are potential contributions; the prototype does not measure real water savings.

## CO mapping
- **CO1:** PEAS, assumptions, workflow and performance measures are in `docs/design_and_methodology.docx` and the app's expandable help sections.
- **CO2:** `src/planner.py` implements uniform-cost search and A* on the same synthetic grid. A* uses Manhattan distance. Results compare path, cost and nodes expanded.
- **CO3:** Backtracking CSP with MRV variable selection and forward checking assigns qualified teams to permitted time slots. Each team can receive at most one task per slot.
- **CO4:** A small fact/rule base uses forward chaining to derive `urgent(X)` and `inspect_first(X)`. The app shows queries and a reasoning trace.
- **Evaluation:** tests cover search optimal cost, valid CSP assignment, constrained CSP failure, inference and ranking.

## Setup
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Run automated tests
From the repository root:

```bash
python -m unittest discover -s tests -v
```

## Repository structure
- `app.py`: Streamlit UI
- `src/planner.py`: search, CSP, ranking, inference algorithms
- `data/sample_data.json`: synthetic data only
- `tests/test_planner.py`: repeatable unit tests
- `results/test_results.md`: test evidence template/results
- `docs/design_and_methodology.docx`: methodology report
- `AI_USE.md`: AI-use record and prompt log

## State-space and search
Grid states are `(x, y)` coordinates. Initial state is `(0, 0)` and goal is `(4, 4)`. Actions move one cell up/down/left/right, avoiding blocked cells. Every action costs 1. UCS orders the frontier by accumulated path cost `g(n)`. A* orders by `f(n)=g(n)+h(n)`, where `h(n)` is Manhattan distance to the goal. Since moves are orthogonal with unit cost and obstacles do not lower cost, Manhattan distance is admissible and consistent.

## CSP definition
- Variables: one variable per leak report.
- Domain: feasible `(team, slot)` pairs where the team has the required skill, is available, and the slot is permitted by the report.
- Constraints: each leak receives one pair; team must possess required skill; team must be available; slot must be allowed; no team can receive two tasks in the same slot.
- Solver: backtracking with Minimum Remaining Values (MRV) and forward checking.

## Knowledge base
Facts are `reported(X)`, `high_severity(X)`, `affects_critical_service(X)`, and `large_leak_rate(X)`.
Rules:
1. `high_severity(X) -> urgent(X)`
2. `affects_critical_service(X) -> urgent(X)`
3. `large_leak_rate(X) AND reported(X) -> urgent(X)`
4. `urgent(X) -> inspect_first(X)`

## Evaluation and limitations
See `results/test_results.md`. All included data is synthetic. The grid is a toy map, not a real GIS road network. Priority weights are illustrative. The CSP does not model travel between jobs or multi-hour workloads. Rule conclusions depend on supplied facts and rules.

## References
- United Nations, Sustainable Development Goal 6: https://sdgs.un.org/goals/goal6
- United Nations, Sustainable Development Goal 11: https://sdgs.un.org/goals/goal11
- Hart, P. E., Nilsson, N. J., Raphael, B. (1968), “A Formal Basis for the Heuristic Determination of Minimum Cost Paths,” IEEE Transactions on Systems Science and Cybernetics, 4(2), 100–107.
- Russell, S. and Norvig, P., *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2021.
