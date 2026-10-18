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
- **Date**: 2026-10-18
- **3A. Strong Classical Baselines**:
  - Implemented `BaranWuBranchExchangePolicy` in `policies.py`: Rigorous implementation of the classic Baran & Wu (1989) branch-exchange heuristic. Evaluates single-loop closure and candidate tie-line exchanges at each step. Achieves 3.574 ± 0.040 MJ (+28.31% heat reduction, 15.8 switches) in <30 ms per scenario.
  - Implemented `DirectTreeSimulatedAnnealingPolicy` in `policies.py`: Classical simulated annealing directly on the spanning tree manifold using cycle-basis edge swaps and Metropolis-Hastings acceptance on exact LinDistFlow losses. Achieves 3.666 ± 0.053 MJ (+26.47% heat reduction, 23.6 switches).
  - Implemented `ExactDynamicOraclePolicy` with switching hysteresis (0.5 kW switching threshold): Demonstrates that switching operations can be cut by 35% (from 23.4 to 15.3 switches) while preserving virtually 100% of optimal loss reduction (3.573 ± 0.043 MJ, +28.33% vs 3.570 ± 0.043 MJ, +28.39%).
- **3B. Attribution & Ablation Policies**:
  - Implemented `qubo_mesh_current_marginal_mst`: Directly extracts maximum spanning trees from empirical quantum annealer marginal spin probabilities $\Pr(x_e = 1)$ using Kruskal's algorithm without post-hoc power-flow ranking. Yields 9.883 ± 1.138 MJ (-98.24% vs baseline, $p_{adj} = 6.96 \times 10^{-20}$), proving that linearized proxy weights without power-flow selection create bottleneck branches with high Joule dissipation.
  - Implemented Hamiltonian term ablations in `QUBOPolicy` (`no_thermo`, `no_cycle`, `no_rad`, `no_cap`, `no_sw`).
  - Added annealer-guided loop branch exchange to `QUBOPolicy(selection="filtered")` combining QUBO candidate exploration with local branch-exchange refinement (3.621 ± 0.042 MJ, +27.37%, 15.9 switches).
- **3C. Statistical Rigor**:
  - Extended benchmark from single seed to 30 independent scenario seeds (750 total power-flow steps).
  - Implemented two-sided paired Student's $t$-tests and Wilcoxon signed-rank tests against `standard_static`.
  - Implemented Holm-Bonferroni step-down correction for multiple testing across all policies.
  - Computed 95% confidence intervals for all energy, voltage, radiality, and switching metrics.
- **3D. Measured Results Summary (30 Seeds, 750 Steps)**:
  - `standard_static`: 4.985 ± 0.055 MJ [4.965, 5.006] (Baseline, 0.0 switches)
  - `static_loss_optimal`: 3.596 ± 0.044 MJ (+27.87%, $p_{adj} = 2.72 \times 10^{-55}$, 5.0 switches)
  - `exact_dynamic_oracle`: 3.570 ± 0.043 MJ (+28.39%, $p_{adj} = 4.22 \times 10^{-58}$, 23.4 switches)
  - `exact_oracle_hysteresis`: 3.573 ± 0.043 MJ (+28.33%, $p_{adj} = 7.00 \times 10^{-58}$, 15.3 switches)
  - `baran_wu_branch_exchange`: 3.574 ± 0.040 MJ (+28.31%, $p_{adj} = 3.82 \times 10^{-57}$, 15.8 switches)
  - `tree_simulated_annealing`: 3.666 ± 0.053 MJ (+26.47%, $p_{adj} = 1.63 \times 10^{-45}$, 23.6 switches)
  - `random_trees_raw`: 12.079 ± 2.416 MJ (-142.29%, 105.8 switches)
  - `random_trees_filtered`: 4.095 ± 0.066 MJ (+17.86%, $p_{adj} = 1.87 \times 10^{-36}$, 97.8 switches)
  - `qubo_mesh_current_raw`: 4.985 ± 0.055 MJ (-0.00%, $p = 1.0000$, 143.5 switches)
  - `qubo_mesh_current_marginal_mst`: 9.883 ± 1.138 MJ (-98.24%, $p_{adj} = 6.96 \times 10^{-20}$, 98.5 switches)
  - `qubo_mesh_current_filtered`: 3.621 ± 0.042 MJ (+27.37%, $p_{adj} = 2.01 \times 10^{-55}$, 15.9 switches)
- **3E. Acceptance & Consistency**:
  - Added unit test suite `tests/test_phase3.py` (7 tests). Total passing unit tests: 32/32.
  - Automated table update via `scripts/generate_readme_table.py` and passed `scripts/check_readme_consistency.py`.
  - Documented IEEE 69-bus scaling constraints and smart-meter scope in `docs/LIMITATIONS.md`.

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
