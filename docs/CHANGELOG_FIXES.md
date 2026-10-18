# Changelog of Fixes & Scientific Corrections

This document records every modification, bug fix, algorithm correction, and changed metric value across all phases of the consistency and scientific rigor overhaul.

---

## Phase 0: Safety Net & Baseline Archival
- **Date**: 2026-10-18
- **Branch**: `fix/consistency-and-science`
- **Initial Test Suite**: 17 tests passed in 4.95s (`tests/test_custom_grid.py`, `tests/test_fast_flow.py`, `tests/test_pipeline.py`, `tests/test_qubo_grid.py`).
- **Baseline Archival**: Pre-change `results/` archived to `results/_before/`. Captured pre-fix default simulation runs:
  - `results/_before/default_run.json` (IEEE-33, SQA, default sliders, seed 42)
  - `results/_before/default_run_12.json` (12-component microgrid, SQA, default sliders, seed 42)
- **Initialized Documentation**: `docs/CHANGELOG_FIXES.md`, `docs/LIMITATIONS.md`, `docs/KNOWN_ISSUES.md`.

---

## Phase 1: Engine Correctness
- **Date**: 2026-10-18
- **1A. Invalid Baselines & Infeasible Networks**:
  - `load_12_component_microgrid` (`pipeline.py`): Designated branches `{1, 2, 10, 12, 14}` (L2, L3, L11, L13, L15) as tie switches. Baseline changed from 4 disconnected islands (0.0 MJ heat, -42,747,267,346% reduction, grade D) to a valid connected radial spanning tree (8.22 kW loss, 0.9895 pu min V).
  - `ExactClassicalSolver` (`exact_classical_solver.py`): Enforced radial tree checks in `solve_unreconfigured_standard()` and `solve_exact_loss_minimizer()`, with Kruskal minimum-resistance tree fallback.
  - `MetricsEvaluator` (`metrics_evaluator.py`) & `report_card.py`: Guarded baseline division by zero/invalid; returns `"N/A (invalid baseline)"` and flags a warning instead of reporting astronomical negative percentages or assigning Grade D.
  - Tracking: Added `infeasible_steps` metric to `pipeline.py` and `simulate.py`.
- **1B. QUBO Constraint Correctness & Attribution**:
  - Added `scripts/verify_qubo_constraints.py` and generated `results/qubo_constraint_check.json`:
    - Enumerated all $C(37, 32) = 435,897$ configurations of IEEE-33.
    - 5 basis cycles admit 159,964 zero-penalty configurations, of which 109,213 (68.27%) are cyclic/disconnected subgraphs (only 31.73% valid trees).
    - 26 elementary cycles admit exactly 50,751 zero-penalty configurations, 100.00% of which are valid radial spanning trees.
  - `ThermodynamicQUBOBuilder` (`qubo_builder.py`): Added `cycle_mode="elementary"` (default in benchmark policies) alongside legacy `cycle_mode="basis"` behind a flag; added bounded binary slack variables for exact inequality constraints $\sum_{e \in C} x_e \le |C| - 1$.
  - `OpenJijAnnealer` (`openjij_annealer.py`): Removed false claims of "no post-hoc power-flow filtering"; documented raw Hamiltonian extraction vs LinDistFlow loss ranking.
  - Attribution policies (`policies.py`): Added `raw`, `repair_only`, and `filtered` modes to `QUBOPolicy` and `RandomTreePolicy`.
- **1C. Power-Flow Accuracy**:
  - `verification/reference_ac_solver.py`: Implemented independent Backward/Forward Sweep AC power flow reference solver. Verified IEEE-33 base case: 210.9876 kW loss, 0.9038 pu min V at bus 18.
  - Diagnosed AC DistFlow error: sending-end Baran-Wu voltage formula $+ (r^2+x^2)I^2$ was applied to receiving-end flows without branch loss feedback, yielding 205.83 kW (-2.4%) or 210.74 kW.
  - Implemented exact Baran-Wu DistFlow with branch loss feedback `FastFeeder.evaluate_ac()` in `verification/fast_flow.py`: matches reference solver to 0.0001% (210.9876 kW, 0.9038 pu).
  - Documented LinDistFlow's measured optimism: 196.93 kW (-6.66% vs AC reference) and min V 0.9071 pu.
- **1D. Ambient-Temperature Slider**:
  - Root cause: `thermal_dynamics.py` and `fast_flow.py` evaluated $R(T) = R_0 [1 + \alpha(T - T_{amb})]$ instead of $T_{ref} = 298.15\text{ K}$, causing $T - T_{amb} = 0$ and neutralizing ambient temperature shifts.
  - Fixed $T_{ref} = 298.15\text{ K}$ across `ThermodynamicLineModel` and `FastFeeder.resistances()`.
  - Measured effect: Increasing ambient temperature from 25°C to 45°C increases baseline heat dissipation by +7.7% due to thermal resistance scaling.
- **1E. Acceptance & Test Coverage**:
  - Added `tests/test_phase1.py` covering all Phase 1 fixes. All 25 unit tests passing.

---

## Phase 2: Automation & Housekeeping
- **Date**: 2026-10-18
- **2.1. Standalone HTML Dashboard Generator**:
  - `build_dashboard_html.py`: Replaced hard-coded author machine path `c:\ep-project\dashboard_data.json` with repository-local `Path(__file__).resolve().parent / "dashboard_data.json"`.
  - Regenerated `dashboard.html` with zero external absolute path dependencies.
- **2.2. Automated README Results Table Generator**:
  - Created `scripts/generate_readme_table.py` which reads `results/benchmark_summary.json` and updates `README.md` between `<!-- RESULTS_TABLE_START -->` and `<!-- RESULTS_TABLE_END -->` markers.
  - Formatted columns: Policy, Heat Dis. (MJ), $\Delta$ vs Baseline (%), Min Voltage (pu), Radiality (%), Latency (ms), and P-Value / Significance.
- **2.3. Markdown & App Number Consistency Verifier**:
  - Created `scripts/check_readme_consistency.py` and test `tests/test_readme_consistency.py`.
  - Verifies that every numeric metric cited in `README.md` and `app.py` corresponds exactly to `results/benchmark_summary.json`.
- **2.4. Dynamic Streamlit Metric Binding**:
  - `app.py`: Updated Benchmark tab narrative to dynamically format metrics from `results/benchmark_summary.json` instead of using stale hard-coded strings.
  - Enforced positive sign convention (`+X.XX%` indicates positive heat reduction / savings).
  - Maintained 100% strict adherence to zero-CSS/styling modification rules.
- **2.5. Deterministic Random Seeds**:
  - `pipeline.py` & `openjij_annealer.py`: Enabled explicit random seed passing (`cfg.seed + t`) to `neal.SimulatedAnnealingSampler` and `openjij.SASampler` ensuring perfect reproducibility across test runs.
  - Configured `pyproject.toml` with `[tool.pytest.ini_options] pythonpath = ["."]`.

---

## Phase 3: Benchmark Rigour
*(To be populated as Phase 3 progresses)*

---

## Phase 4: Science Improvements
*(To be populated as Phase 4 progresses)*

---

## Phase 5: Quantum Hardware Path
*(To be populated as Phase 5 progresses)*

---

## Phase 6: Documentation Rewrite
*(To be populated as Phase 6 progresses)*

---

## Phase 7: Final Verification & Report
*(To be populated as Phase 7 progresses)*
