# Design and Methodology — Water Leak Inspection Planner

## 1. Problem and goals
The system is a decision-support prototype for ranking suspected water leaks and assigning inspection teams. It is connected to SDG 6 (Clean Water and Sanitation), especially water-use efficiency (target 6.4), and SDG 11 (Sustainable Cities and Communities), through the potential support it offers for reliable urban infrastructure services. All bundled data is synthetic.

## 2. CO1: Agent and environment (PEAS)
| Element | Specification |
|---|---|
| Performance | Rank urgent reports early; produce valid assignments; minimise route cost; compare nodes expanded; show traceable rule conclusions |
| Environment | Synthetic leak reports, discrete time slots, inspection crews, 5×5 grid with blocked cells |
| Actuators | Display rankings, recommend route, assign team/time slot, export JSON |
| Sensors | Report severity, age, estimated leak rate, critical-service flag, required skill, team skills/availability and grid map |

**Agent:** a planning assistant that recommends inspection priorities, routes, assignments and rule-based urgency conclusions.  
**Goals:** give interpretable prioritisation and feasible crew allocation; compare optimal route-search methods.  
**Inputs:** leak attributes, skills, availability, allowed slots, start/goal and blocked grid cells.  
**Outputs:** ranked reports, route path/cost/nodes expanded, team-slot assignments, inference conclusions and reasoning trace.

### Workflow
1. Load synthetic leak reports and crew data.
2. Calculate a transparent priority score.
3. Compare UCS and A* on an identical grid route task.
4. Allocate inspection reports to team/slot pairs with CSP backtracking and forward checking.
5. Apply forward-chaining rules and answer urgency queries.
6. Display and export results.

**Assumptions:** one team can perform at most one inspection per slot; a team must have the task's required skill and be available; allowed slots are hard constraints; grid moves have unit cost; priority weights are illustrative; no live dispatch occurs.

**Performance measures:** count/fraction of tasks assigned validly; rank order; route solution cost and expanded nodes; correct derivability of conclusions; explicit detection of infeasibility.

## 3. CO2: Search
### State space
A state is a grid coordinate `(x,y)`. The start is `(0,0)`, goal `(4,4)`. Actions move one cell orthogonally, remaining inside a 5×5 grid and avoiding blocked cells. Each action costs 1. The goal test is reaching `(4,4)`.

### Uniform-cost search
UCS expands the frontier node with the smallest accumulated path cost `g(n)`. With unit step costs it finds an optimal path.

### A*
A* expands the node with the smallest `f(n)=g(n)+h(n)`. The heuristic is Manhattan distance `h(n)=|x-x_goal|+|y-y_goal|`. This is admissible and consistent for four-direction unit-cost movement; obstacles can force detours but cannot make the true cost lower than Manhattan distance.

Both algorithms run on the same fixed test map. The application reports path, cost and number of nodes expanded. Exact expanded counts can depend on tie-breaking, which is deterministic in this implementation.

## 4. CO3: CSP
**Variables:** one variable for each leak report.  
**Domains:** feasible `(team ID, time slot)` pairs satisfying required skill, team availability, and report-specific allowed slots.  
**Hard constraints:** assign each report once; use a qualified team; team is available; slot is allowed; no two reports use the same team in the same slot.  
**Algorithm:** recursive backtracking, Minimum Remaining Values (MRV) to select the most constrained unassigned report, and forward checking to remove a chosen team-slot pair from other domains. If any remaining domain becomes empty, the branch is abandoned.  
**Evidence:** the app shows the assignment and a trace. A validator independently checks the constraints. The constrained test with an unavailable skill demonstrates an infeasible instance.

## 5. CO4: Knowledge and inference
**Predicates/facts:** `reported(X)`, `high_severity(X)`, `affects_critical_service(X)`, `large_leak_rate(X)`.  
**Rules:**
1. `high_severity(X) → urgent(X)`
2. `affects_critical_service(X) → urgent(X)`
3. `large_leak_rate(X) ∧ reported(X) → urgent(X)`
4. `urgent(X) → inspect_first(X)`

**Queries:** (Q1) `urgent(L-101)?` and (Q2) `inspect_first(L-101)?`.  
If L-101 is marked critical/high severity or affects a critical service, rule 1 or 2 derives `urgent(L-101)`, then rule 4 derives `inspect_first(L-101)`. The UI displays the actual facts and fired-rule trace. A query for an unrelated ID should remain false unless its facts are supplied.

## 6. Evaluation plan
Five automated tests cover baseline route search, baseline CSP feasibility, an infeasible constrained CSP, inference, and priority ranking. Run them with `python -m unittest discover -s tests -v`. Test results should be rerun and recorded on the submission machine. All data is synthetic.

## 7. Limitations and future work
The grid is not a real road network; route costs are not travel-time estimates. Priority weights need domain validation. The CSP does not model inter-task travel or multi-hour workload. Rules are intentionally small and deterministic. Future work includes GIS integration, uncertainty modelling, richer scheduling, and evaluation against anonymised field data.
