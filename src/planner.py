"""Core algorithms for the Water Leak Inspection Planner."""
from __future__ import annotations
import heapq
import json
from pathlib import Path
from collections import deque

ROOT = Path(__file__).resolve().parents[1]

def load_sample_data():
    with open(ROOT / "data" / "sample_data.json", encoding="utf-8") as f:
        return json.load(f)

def _truth(value):
    return str(value).strip().lower() in {"true", "yes", "1"}

def rank_leaks(leaks):
    weights = {"low": 1, "medium": 3, "high": 5, "critical": 8}
    result = []
    for row in leaks:
        severity = weights.get(str(row.get("Severity", "Low")).lower(), 1)
        try: rate = max(0.0, float(row.get("Estimated leak rate", 0) or 0))
        except (ValueError, TypeError): rate = 0.0
        try: age = max(0.0, float(row.get("Report age (hours)", 0) or 0))
        except (ValueError, TypeError): age = 0.0
        score = severity * 5 + min(age / 4, 5) + min(rate, 10) + (10 if _truth(row.get("Critical service affected", False)) else 0)
        result.append({**row, "Priority score": round(score, 2)})
    return sorted(result, key=lambda x: (-x["Priority score"], str(x.get("Leak ID",""))))

def build_grid_problem():
    # Coordinates (x,y), 0-indexed; start at depot (0,0), target is the clinic zone (4,4).
    width, height = 5, 5
    start, goal = (0, 0), (4, 4)
    blocked = {(1, 1), (1, 2), (3, 2), (3, 3)}
    return start, {goal}, blocked, width, height

def _neighbors(node, blocked, width, height):
    x, y = node
    for nxt in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
        if 0 <= nxt[0] < width and 0 <= nxt[1] < height and nxt not in blocked:
            yield nxt

def _reconstruct(parent, node):
    path = [node]
    while node in parent:
        node = parent[node]
        path.append(node)
    return list(reversed(path))

def ucs(start, goals, blocked, width, height):
    frontier = [(0, 0, start)]
    counter = 1
    cost = {start: 0}
    parent = {}
    expanded = 0
    while frontier:
        g, _, node = heapq.heappop(frontier)
        if g != cost.get(node): continue
        expanded += 1
        if node in goals:
            return {"found": True, "path": _reconstruct(parent,node), "cost": g, "expanded": expanded}
        for nxt in _neighbors(node, blocked, width, height):
            ng = g + 1
            if ng < cost.get(nxt, float("inf")):
                cost[nxt] = ng
                parent[nxt] = node
                heapq.heappush(frontier, (ng, counter, nxt)); counter += 1
    return {"found": False, "path": [], "cost": None, "expanded": expanded}

def astar(start, goals, blocked, width, height):
    goal = next(iter(goals))
    h = lambda p: abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    frontier = [(h(start), 0, start)]
    counter = 1
    cost = {start: 0}
    parent = {}
    expanded = 0
    while frontier:
        _, g, node = heapq.heappop(frontier)
        if g != cost.get(node): continue
        expanded += 1
        if node in goals:
            return {"found": True, "path": _reconstruct(parent,node), "cost": g, "expanded": expanded}
        for nxt in _neighbors(node, blocked, width, height):
            ng = g + 1
            if ng < cost.get(nxt, float("inf")):
                cost[nxt] = ng
                parent[nxt] = node
                heapq.heappush(frontier, (ng + h(nxt), ng, nxt)); counter += 1
    return {"found": False, "path": [], "cost": None, "expanded": expanded}

def _skills(team):
    value = team.get("Skills", [])
    if isinstance(value, str):
        return {s.strip().lower() for s in value.replace(";", ",").split(",") if s.strip()}
    return {str(s).strip().lower() for s in value}

def _available(team):
    value = team.get("Available slots", [])
    if isinstance(value, str):
        return {s.strip() for s in value.replace(";", ",").split(",") if s.strip()}
    return {str(s).strip() for s in value}

def solve_csp(leaks, teams, slots):
    """Backtracking CSP: each leak gets one (qualified team, allowed slot); FC prunes domains."""
    tasks = [r for r in leaks if str(r.get("Leak ID","")).strip()]
    if not tasks: return [], ["No tasks to schedule."]
    team_by_id = {str(t.get("Team ID","")).strip(): t for t in teams if str(t.get("Team ID","")).strip()}
    domains = {}
    for task in tasks:
        required = str(task.get("Required skill","")).strip().lower()
        allowed_slots = task.get("Allowed slots", slots)
        if isinstance(allowed_slots, str):
            allowed_slots = [s.strip() for s in allowed_slots.replace(";", ",").split(",") if s.strip()]
        if not allowed_slots: allowed_slots = list(slots)
        domain = []
        for team_id, team in team_by_id.items():
            if required in _skills(team) and _available(team).intersection(set(slots)):
                for slot in slots:
                    if slot in _available(team) and slot in set(allowed_slots):
                        domain.append((team_id, slot))
        domains[str(task["Leak ID"])] = domain
    trace = []
    assignment = {}
    # Task order uses MRV; forward checking removes used team-slot pairs.
    def recurse(remaining, current_domains):
        if not remaining: return True
        task_id = min(remaining, key=lambda k: len(current_domains[k]))
        choices = list(current_domains[task_id])
        trace.append(f"Select {task_id} by MRV: {len(choices)} candidate(s)")
        for team_id, slot in choices:
            if any(t == team_id and s == slot for t, s in assignment.values()):
                continue
            trace.append(f"Try {task_id} -> team {team_id}, slot {slot}")
            assignment[task_id] = (team_id, slot)
            new_remaining = [k for k in remaining if k != task_id]
            new_domains = {k: list(v) for k,v in current_domains.items() if k != task_id}
            failed = False
            for other in new_remaining:
                new_domains[other] = [v for v in new_domains[other] if v != (team_id,slot)]
                if not new_domains[other]:
                    trace.append(f"Forward check fails: {other} has no candidates")
                    failed = True; break
            if not failed and recurse(new_remaining, new_domains): return True
            assignment.pop(task_id, None)
            trace.append(f"Backtrack from {task_id}")
        return False
    ok = recurse(list(domains), domains)
    if not ok:
        trace.append("No satisfying assignment found.")
        return [], trace
    output = []
    for task in tasks:
        tid = str(task["Leak ID"])
        team_id, slot = assignment[tid]
        output.append({"Leak ID":tid, "Location":task.get("Location",""), "Team ID":team_id, "Slot":slot, "Required skill":task.get("Required skill","")})
    trace.append("All tasks assigned; constraints satisfied.")
    return output, trace

def validate_assignment(assignment, leaks, teams, slots):
    by_id = {str(t.get("Team ID","")).strip():t for t in teams}
    leak_by_id = {str(l.get("Leak ID","")).strip():l for l in leaks}
    seen = set()
    for a in assignment:
        task = leak_by_id.get(a["Leak ID"])
        team = by_id.get(a["Team ID"])
        if not task or not team: return False
        if str(task.get("Required skill","")).lower() not in _skills(team): return False
        if a["Slot"] not in slots or a["Slot"] not in _available(team): return False
        allowed = task.get("Allowed slots", slots)
        if isinstance(allowed,str): allowed=[s.strip() for s in allowed.replace(";",",").split(",") if s.strip()]
        if allowed and a["Slot"] not in allowed: return False
        key=(a["Team ID"],a["Slot"])
        if key in seen: return False
        seen.add(key)
    return len(assignment) == len([l for l in leaks if str(l.get("Leak ID","")).strip()])

def forward_chain(initial_facts):
    """Facts are (predicate, entity). Rules derive urgent and inspect_first."""
    known = set((str(p), str(x)) for p,x in initial_facts)
    trace = [f"FACT {p}({x})" for p,x in sorted(known)]
    changed = True
    while changed:
        changed = False
        new = set()
        for pred, entity in list(known):
            if pred in ("high_severity", "affects_critical_service"):
                new.add(("urgent", entity))
            if pred == "large_leak_rate" and ("reported", entity) in known:
                new.add(("urgent", entity))
        for pred, entity in list(known):
            if pred == "urgent":
                new.add(("inspect_first", entity))
        for item in sorted(new - known):
            known.add(item); changed = True
            trace.append(f"RULE FIRED ⇒ {item[0]}({item[1]})")
    return sorted(known), trace
