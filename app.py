"""Water Leak Inspection Planner — educational AI prototype."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st

from src.planner import (
    load_sample_data, rank_leaks, solve_csp, forward_chain,
    ucs, astar, build_grid_problem, validate_assignment
)

st.set_page_config(page_title="Water Leak Inspection Planner", page_icon="💧", layout="wide")
st.title("Water Leak Inspection Planner")
st.caption("Synthetic-data prototype | SDG 6: Clean Water and Sanitation | SDG 11: Sustainable Cities and Communities")

st.info("Decision-support demonstration only. Priority scores and route costs are illustrative, not measured water savings or real-world travel times.")

data = load_sample_data()
with st.sidebar:
    st.header("Prototype controls")
    use_sample = st.checkbox("Load synthetic sample data", value=True)
    st.markdown("**AI components**")
    st.write("CO1: PEAS / agent workflow")
    st.write("CO2: Uniform-cost search vs A*")
    st.write("CO3: CSP team scheduling")
    st.write("CO4: Forward-chaining rules")

if not use_sample:
    st.warning("Sample data is disabled. This teaching prototype currently uses its bundled synthetic data for the route-search demo; edit the tables below for scheduling.")
leaks = pd.DataFrame(data["leaks"])
teams = pd.DataFrame(data["teams"])
slots = data["slots"]

st.subheader("1. Synthetic inspection reports")
leaks_edit = st.data_editor(leaks, num_rows="dynamic", use_container_width=True, key="leaks_editor")
st.caption("Severity: Low / Medium / High / Critical. Required skill must match a team's skills.")

st.subheader("2. Inspection teams")
teams_edit = st.data_editor(teams, num_rows="dynamic", use_container_width=True, key="teams_editor")
slots_text = st.text_input("Available inspection slots (comma-separated)", value=", ".join(slots))
slots = [s.strip() for s in slots_text.split(",") if s.strip()]

if st.button("Run planner", type="primary"):
    leaks_records = leaks_edit.fillna("").to_dict(orient="records")
    teams_records = teams_edit.fillna("").to_dict(orient="records")
    ranked = rank_leaks(leaks_records)
    st.subheader("CO1 / prioritisation result")
    st.dataframe(pd.DataFrame(ranked), use_container_width=True)

    st.subheader("CO2 / route search comparison")
    problem = build_grid_problem()
    start, goals, blocked, width, height = problem
    u = ucs(start, goals, blocked, width, height)
    a = astar(start, goals, blocked, width, height)
    comparison = pd.DataFrame([
        {"Algorithm":"Uniform-cost search (UCS)", "Path":str(u["path"]), "Cost":u["cost"], "Nodes expanded":u["expanded"], "Found":u["found"]},
        {"Algorithm":"A*", "Path":str(a["path"]), "Cost":a["cost"], "Nodes expanded":a["expanded"], "Found":a["found"]},
    ])
    st.dataframe(comparison, use_container_width=True)
    st.caption("The same fixed synthetic grid and goal are used for both methods. A* uses Manhattan distance to the goal; all moves cost 1.")

    st.subheader("CO3 / CSP crew schedule")
    assignment, trace = solve_csp(leaks_records, teams_records, slots)
    if assignment:
        st.success("A valid assignment was found.")
        st.dataframe(pd.DataFrame(assignment), use_container_width=True)
        st.write("Assignment valid:", validate_assignment(assignment, leaks_records, teams_records, slots))
    else:
        st.error("No valid assignment exists for the current constraints.")
        st.write("Try adding a qualified team, availability slot, or relaxing a constraint.")
    with st.expander("CSP search trace"):
        st.code("\n".join(trace) if trace else "No search steps recorded.")

    st.subheader("CO4 / knowledge base and forward chaining")
    facts = []
    for r in leaks_records:
        facts.append(("reported", str(r.get("Leak ID","")).strip()))
        if str(r.get("Severity","")).lower() in ("high","critical"):
            facts.append(("high_severity", str(r.get("Leak ID","")).strip()))
        if str(r.get("Critical service affected", False)).lower() in ("true","yes","1"):
            facts.append(("affects_critical_service", str(r.get("Leak ID","")).strip()))
        try:
            if float(r.get("Estimated leak rate",0)) >= 5:
                facts.append(("large_leak_rate", str(r.get("Leak ID","")).strip()))
        except (ValueError, TypeError):
            pass
    conclusions, reasoning = forward_chain(facts)
    st.write("Rules: (1) high_severity(X) → urgent(X); (2) affects_critical_service(X) → urgent(X); (3) large_leak_rate(X) AND reported(X) → urgent(X); (4) urgent(X) → inspect_first(X).")
    query_id = st.text_input("Query leak ID", value=str(leaks_records[0].get("Leak ID","L-101")) if leaks_records else "L-101")
    st.write("Query: Is this leak urgent?")
    st.write("Conclusion:", any(p == ("urgent", query_id) for p in conclusions))
    st.write("Query: Should it be inspected first?")
    st.write("Conclusion:", any(p == ("inspect_first", query_id) for p in conclusions))
    with st.expander("Forward-chaining reasoning trace"):
        st.code("\n".join(reasoning) if reasoning else "No rule fired.")
    output = {"ranked_leaks": ranked, "route_search": {"ucs":u, "astar":a}, "schedule":assignment, "inference_facts":[list(x) for x in facts], "inference_conclusions":[list(x) for x in conclusions]}
    st.download_button("Download results as JSON", json.dumps(output, indent=2), file_name="planner_results.json", mime="application/json")

st.divider()
with st.expander("CO1: PEAS, assumptions and performance measures"):
    st.markdown("""
| PEAS element | Description |
|---|---|
| Performance | High-priority reports scheduled; valid team/skill/availability assignment; route cost and nodes expanded; transparent reasoning |
| Environment | Synthetic leak reports, teams, discrete time slots, and a small grid map |
| Actuators | Rank reports, recommend grid path, assign team and slot, export result |
| Sensors | Report severity, estimated leak rate, report age, critical-service flag, team skills and availability, grid obstacles |

**Assumptions:** data is synthetic; one inspection per team per slot; every movement on the grid costs one unit; route-search demo has one fixed start and goal; leak-rate and priority values are estimates; the app does not dispatch teams or connect to live infrastructure.

**Performance measures:** (a) number of valid assignments / eligible tasks, (b) priority score ordering, (c) route cost and nodes expanded for UCS and A*, (d) whether inference conclusions are derivable from the rule base.
""")
with st.expander("Workflow diagram"):
    st.code("Synthetic reports + team data\\n          ↓\\n Validate and rank leak reports (CO1)\\n          ↓\\n Grid route: UCS vs A* (CO2)\\n          ↓\\n Crew/slot allocation CSP (CO3)\\n          ↓\\n Rule-based inference + queries (CO4)\\n          ↓\\n Results table + JSON export", language="text")
with st.expander("Limitations and future improvements"):
    st.markdown("""
- Priority weights are hand-designed and require calibration with domain experts.
- The grid is a toy map, not a geographic road network; route cost is not real travel time.
- The CSP schedules discrete tasks and does not model travel time between consecutive jobs or crew workload beyond one job per slot.
- Inference is deterministic and only as complete as the listed facts and rules.
- Future work: GIS/road-network routing, uncertainty-aware leak detection, travel-time windows, workload balancing, and evaluation on anonymised operational data.
""")
