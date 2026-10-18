# Known Issues & Audit Registry

This document tracks known bugs, mathematical discrepancies, and architectural issues discovered during system auditing, along with their severity, affected files, and recommended or implemented fixes.

## Discovered Issues Summary

| Issue ID | Severity | File | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-01** | High | `grid_engine/ieee_feeder_loader.py`, `solvers/exact_classical_solver.py` | 12-component microgrid lacks tie switches; baseline selects first 11 lines resulting in disconnected islands and -42B% heat reduction report | Investigating (Phase 1A) |
| **ISSUE-02** | High | `qubo_engine/qubo_builder.py`, `solvers/openjij_annealer.py` | QUBO basis cycle constraints admit 159,964 non-tree configurations for IEEE-33; raw QUBO ground states often invalid trees without repair | Investigating (Phase 1B) |
| **ISSUE-03** | Medium | `verification/fast_flow.py` | LinDistFlow and AC DistFlow power flow discrepancies relative to exact Newton-Raphson / backward-forward reference | Investigating (Phase 1C) |
| **ISSUE-04** | Low | `pipeline.py`, `grid_engine/thermal_dynamics.py` | Ambient temperature slider does not feed $R(T)$ feedback directly into LinDistFlow impedances | Investigating (Phase 1D) |
| **ISSUE-05** | Medium | `cli.py` | Unicode box-drawing characters trigger `UnicodeEncodeError` on Windows consoles with default CP1252 | Identified (Workaround: `PYTHONIOENCODING=utf-8`) |
| **ISSUE-06** | Medium | `build_dashboard_html.py`, `generate_docx_manual.py` | Hard-coded development paths (`c:\ep-project\...`) cause failures on foreign environments | Fixing in Phase 2 |
