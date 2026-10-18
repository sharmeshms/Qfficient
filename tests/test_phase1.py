"""Unit tests for Phase 1: Engine correctness, feasibility, constraints, and power flow."""
import numpy as np
import pytest

from thermodynamic_grid_qubo.grid_engine.ieee_feeder_loader import IEEEFeederLoader
from thermodynamic_grid_qubo.pipeline import load_12_component_microgrid, OptimizationConfig, run_optimization
from thermodynamic_grid_qubo.verification.fast_flow import FastFeeder
from thermodynamic_grid_qubo.verification.reference_ac_solver import reference_ac_power_flow
from thermodynamic_grid_qubo.verification.physics_verifier import PhysicsVerifier
from thermodynamic_grid_qubo.verification.metrics_evaluator import MetricsEvaluator
from thermodynamic_grid_qubo.solvers.exact_classical_solver import ExactClassicalSolver
from thermodynamic_grid_qubo.qubo_engine.qubo_builder import ThermodynamicQUBOBuilder
import networkx as nx


# ---------------------------------------------------------------------------
# 1A Tests: Baseline feasibility, oracle feasibility, N/A guarding
# ---------------------------------------------------------------------------
def test_12_component_microgrid_baseline_is_radial_tree():
    """Verify 12-component microgrid baseline forms a single connected radial spanning tree."""
    grid = load_12_component_microgrid()
    verifier = PhysicsVerifier(grid)
    solver = ExactClassicalSolver(grid)

    base_switches, _ = solver.solve_unreconfigured_standard()
    is_tree, msg = verifier.is_valid_radial_tree(base_switches)

    assert is_tree is True, f"12-component baseline is not radial: {msg}"
    assert sum(base_switches.values()) == len(grid.graph.nodes) - 1

    # Solve power flow on baseline to ensure non-zero, finite physical loss
    injections = {k: (-v[0], -v[1]) for k, v in grid.bus_loads.items()}
    ok, v_pu, cur, loss_kw = verifier.solve_power_flow(base_switches, injections)
    assert ok is True
    assert 5.0 < loss_kw < 15.0  # ~8.22 kW
    assert min(v_pu.values()) > 0.95


def test_exact_oracle_feasible_every_step_on_12_component():
    """Verify ExactClassicalSolver returns a valid radial tree for 12-component microgrid."""
    grid = load_12_component_microgrid()
    verifier = PhysicsVerifier(grid)
    solver = ExactClassicalSolver(grid)

    injections = {k: (-v[0], -v[1]) for k, v in grid.bus_loads.items()}
    switches, loss_kw, _ = solver.solve_exact_loss_minimizer(injections)

    is_tree, msg = verifier.is_valid_radial_tree(switches)
    assert is_tree is True, f"Oracle returned non-tree: {msg}"
    assert loss_kw > 0.0 and np.isfinite(loss_kw)


def test_invalid_baseline_returns_na_metric():
    """Verify MetricsEvaluator returns 'N/A (invalid baseline)' and no huge negative percent."""
    evaluator = MetricsEvaluator()
    base_metrics = evaluator.summarize_run([0.0], [0.0], [25.0], 0, [1.0])
    qubo_metrics = evaluator.summarize_run([10.0], [1.0], [25.0], 0, [1.0])

    # Case 1: baseline_valid is False
    res1 = evaluator.compare_methods(base_metrics, qubo_metrics, baseline_valid=False)
    assert res1["heat_reduction_pct"] == "N/A (invalid baseline)"
    assert res1["entropy_reduction_pct"] == "N/A (invalid baseline)"

    # Case 2: baseline heat is 0.0
    res2 = evaluator.compare_methods(base_metrics, qubo_metrics, baseline_valid=True)
    assert res2["heat_reduction_pct"] == "N/A (invalid baseline)"
    assert res2["entropy_reduction_pct"] == "N/A (invalid baseline)"


# ---------------------------------------------------------------------------
# 1B Tests: QUBO constraint ground state on small grid
# ---------------------------------------------------------------------------
def test_qubo_ground_states_are_valid_spanning_trees_small_grid():
    """Brute force check on a 3-node triangle cycle: every ground state of the QUBO is a valid tree."""
    edges = [(0, 1), (1, 2), (2, 0)]
    G = nx.Graph()
    for i, (u, v) in enumerate(edges):
        G.add_edge(u, v, edge_id=i)

    builder = ThermodynamicQUBOBuilder(
        num_buses=3,
        edges=edges,
        substations=[0],
        graph=G,
        lambda_thermo=0.0,
        lambda_cycle=10.0,
        lambda_rad=10.0,
        lambda_cap=0.0,
        lambda_sw=0.0,
        cycle_mode="elementary",
    )
    model = builder.build_model(entropy_weights={})
    Q = model.Q
    offset = model.offset
    n_vars = len(model.names)

    # Brute-force enumerate all 2^n_vars states
    min_energy = float("inf")
    ground_states = []
    for s_int in range(1 << n_vars):
        vec = np.array([(s_int >> i) & 1 for i in range(n_vars)])
        energy = float(vec @ Q @ vec + offset)
        if energy < min_energy - 1e-6:
            min_energy = energy
            ground_states = [vec]
        elif abs(energy - min_energy) <= 1e-6:
            ground_states.append(vec)

    assert min_energy == pytest.approx(0.0)
    assert len(ground_states) == 3  # exactly the 3 spanning trees of K3

    # Check that each ground state's edge selection is a connected radial tree
    for s in ground_states:
        closed_edges = [i for i in range(3) if s[i] == 1]
        assert len(closed_edges) == 2
        sub = nx.Graph()
        for e in closed_edges:
            sub.add_edge(*edges[e])
        assert len(sub.nodes) == 3
        assert nx.is_connected(sub)


# ---------------------------------------------------------------------------
# 1C Tests: Power flow accuracy and reference solver
# ---------------------------------------------------------------------------
def test_reference_ac_solver_reproduces_ieee33_base_case():
    """Reference BFS reproduces standard IEEE-33 power flow loss of 210.99 kW and 0.9038 pu min V."""
    grid = IEEEFeederLoader.load_ieee33()
    injections = {k: (-v[0], -v[1]) for k, v in grid.bus_loads.items()}
    converged, v_pu, i_a, loss_kw, v_min = reference_ac_power_flow(grid, injections)

    assert converged is True
    assert loss_kw == pytest.approx(210.9876, abs=0.05)
    assert v_min == pytest.approx(0.9038, abs=0.001)


def test_evaluate_ac_matches_reference_within_one_percent():
    """FastFeeder.evaluate_ac matches reference solver within 0.1% on standard IEEE-33."""
    grid = IEEEFeederLoader.load_ieee33()
    fast = FastFeeder(grid)
    injections = {k: (-v[0], -v[1]) for k, v in grid.bus_loads.items()}
    p_pu, q_pu = fast.vectors(injections)
    r_ohm = fast.resistances()

    valid, v_pu, currents, loss_kw, v_min = fast.evaluate_ac(fast.standard_edges, p_pu, q_pu, r_ohm)
    ref_conv, ref_v, ref_i, ref_loss, ref_vmin = reference_ac_power_flow(grid, injections)

    assert valid is True
    assert ref_conv is True
    # Tolerances: AC solver within 0.1% of reference
    diff_pct = abs(loss_kw - ref_loss) / ref_loss * 100.0
    assert diff_pct < 0.1
    assert abs(v_min - ref_vmin) < 0.001


def test_lindistflow_optimism_documented_and_measured():
    """LinDistFlow yields ~196.93 kW, demonstrating ~6.7% optimism relative to AC reference."""
    grid = IEEEFeederLoader.load_ieee33()
    fast = FastFeeder(grid)
    injections = {k: (-v[0], -v[1]) for k, v in grid.bus_loads.items()}
    p_pu, q_pu = fast.vectors(injections)
    r_ohm = fast.resistances()

    valid, v_pu, currents, lin_loss, v_min = fast.evaluate(fast.standard_edges, p_pu, q_pu, r_ohm)
    ref_conv, _, _, ref_loss, _ = reference_ac_power_flow(grid, injections)

    assert valid is True
    # LinDistFlow is ~196.93 kW
    assert lin_loss == pytest.approx(196.93, abs=0.1)
    # Optimism ratio ~ -6.66%
    optimism_pct = (lin_loss - ref_loss) / ref_loss * 100.0
    assert -7.5 < optimism_pct < -6.0


# ---------------------------------------------------------------------------
# 1D Tests: Ambient temperature slider changes resistance and losses
# ---------------------------------------------------------------------------
def test_ambient_temperature_slider_alters_losses():
    """Changing ambient temperature slider from 25C to 45C increases baseline Joule heat."""
    cfg25 = OptimizationConfig(grid="ieee33", solver="classical", ambient_c=25.0, time_steps=5, seed=42)
    res25 = run_optimization(cfg25)

    cfg45 = OptimizationConfig(grid="ieee33", solver="classical", ambient_c=45.0, time_steps=5, seed=42)
    res45 = run_optimization(cfg45)

    heat25 = res25["summary"]["baseline"]["total_heat_mj"]
    heat45 = res45["summary"]["baseline"]["total_heat_mj"]

    assert heat45 > heat25
    # Relative resistance increase for copper/aluminum with alpha ~ 0.00393 /K over 20 K is ~7-8%
    pct_increase = (heat45 - heat25) / heat25 * 100.0
    assert 4.0 < pct_increase < 15.0
