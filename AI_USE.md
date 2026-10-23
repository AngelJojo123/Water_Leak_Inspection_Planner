# AI-use record

## Tools used
- **ChatGPT (OpenAI):** brainstorming the project structure, drafting explanations and code scaffolding, suggesting test cases, and helping produce the methodology document.
- **Python standard library / unittest:** used to execute local automated tests.
- **Streamlit and pandas:** UI and tabular display libraries used by the prototype.

## Representative prompt log
1. “Create a water leak inspection planner aligned to SDG 6 and SDG 11.”
2. “Check the project against CO1–CO4, search, CSP, inference, evaluation, repository, and presentation requirements.”
3. “Develop a complete version satisfying all requirements and provide a ZIP and DOCX.”

## Accepted and changed
- Accepted the synthetic leak/crew scheduling use case, UCS/A* comparison, CSP allocation, forward-chaining rules, and tests.
- The implementation uses a small synthetic grid and hand-designed priority weights for clarity and reproducibility.
- No real operational dataset is included. The team should review and adapt the code and report before submission.

## Verification performed
- Automated tests are included in `tests/test_planner.py`.
- Test results are documented in `results/test_results.md`.
- Before submission, all team members should rerun tests, inspect outputs, verify assumptions and constraints, and be able to explain the implementation.
- AI-generated content must not be submitted without review. Add any additional tools used by the team and record any changes made.

## External material
- United Nations SDG 6 and SDG 11 pages and the A* reference listed in README.
- Python, Streamlit, and pandas documentation may be consulted during implementation; add exact versions/URLs if further external material is used.
