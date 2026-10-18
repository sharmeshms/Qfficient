"""Unit test suite for Phase 3: Benchmark Rigour & Strong Baselines."""
import numpy as np
import pytest

from thermodynamic_grid_qubo.grid_engine.ieee_feeder_loader import IEEEFeederLoader
from thermodynamic_grid_qubo.verification.fast_flow import FastFeeder
from thermodynamic_grid_qubo.benchmark.policies import (
    StandardStaticPolicy,
    StaticLossOptimalPolicy,
    ExactDynamicOraclePolicy,
    BaranWuBranchExchangePolicy,
    DirectTreeSimulatedAnnealingPolicy,
    QUBOPolicy,
    DecisionContext,
)
from thermodynamic_grid_qubo.benchmark.simulate import Scenario, simulate
from run_benchmark import holm_bonferroni_correction, calc_ci95


@pytest.fixture
def feeder_and_context():
    grid = IEEEFeederLoader.load_ieee33()
    fast = FastFeeder(grid)
    sc = Scenario.sample(seed=42, time_steps=4)
    injections = sc.timeline[0]
    p_pu, q_pu = fast.vectors(injections)
    resistances = fast.resistances()
    ctx = DecisionContext(
        grid=grid,
        fast=fast,
        injections=injections,
        temps_k=np.array([grid.lines[e].t_amb for e in fast.edge_ids]),
        prev_active=fast.standard_edges,
        step=0,
        p_pu=p_pu,
        q_pu=q_pu,
        resistances=resistances,
    )
    return grid, fast, sc, ctx


def test_baran_wu_branch_exchange(feeder_and_context):
    grid, fast, sc, ctx = feeder_and_context
    policy = BaranWuBranchExchangePolicy(max_iterations=10)
    policy.reset(grid, fast, sc.timeline)
    tree, ms = policy.decide(ctx)

    assert fast.is_tree(tree)
    assert len(tree) == 32
    ok_base, _, _, loss_base, _ = fast.evaluate(fast.standard_edges, ctx.p_pu, ctx.q_pu, ctx.resistances)
    ok_bw, _, _, loss_bw, v_min_bw = fast.evaluate(tree, ctx.p_pu, ctx.q_pu, ctx.resistances)
    assert ok_bw
    assert v_min_bw >= 0.90
    assert loss_bw < loss_base


def test_tree_simulated_annealing(feeder_and_context):
    grid, fast, sc, ctx = feeder_and_context
    policy = DirectTreeSimulatedAnnealingPolicy(steps=30, seed=42)
    policy.reset(grid, fast, sc.timeline)
    tree, ms = policy.decide(ctx)

    assert fast.is_tree(tree)
    assert len(tree) == 32
    ok, _, _, loss, v_min = fast.evaluate(tree, ctx.p_pu, ctx.q_pu, ctx.resistances)
    assert ok


def test_exact_oracle_hysteresis(feeder_and_context):
    grid, fast, sc, ctx = feeder_and_context
    candidate_trees = fast.enumerate_radial_configs()
    policy_no_hyst = ExactDynamicOraclePolicy(candidate_trees=candidate_trees, pool_size=50, hysteresis_kw=0.0)
    policy_hyst = ExactDynamicOraclePolicy(candidate_trees=candidate_trees, pool_size=50, hysteresis_kw=5.0)

    policy_no_hyst.reset(grid, fast, sc.timeline)
    policy_hyst.reset(grid, fast, sc.timeline)

    tree1, _ = policy_no_hyst.decide(ctx)
    tree2, _ = policy_hyst.decide(ctx)
    assert fast.is_tree(tree1)
    assert fast.is_tree(tree2)


def test_qubo_marginal_mst_and_ablations(feeder_and_context):
    grid, fast, sc, ctx = feeder_and_context

    # Marginal MST
    policy_mst = QUBOPolicy(num_reads=25, selection="marginal_mst", seed=42)
    policy_mst.reset(grid, fast, sc.timeline)
    tree_mst, _ = policy_mst.decide(ctx)
    assert fast.is_tree(tree_mst)

    # Hamiltonian ablations
    for abl in ["no_thermo", "no_cycle", "no_rad", "no_cap", "no_sw"]:
        policy_abl = QUBOPolicy(num_reads=20, selection="filtered", ablation=abl, seed=42)
        policy_abl.reset(grid, fast, sc.timeline)
        assert policy_abl.builder is not None


def test_holm_bonferroni_correction():
    raw_p = {
        "p1": 0.001,
        "p2": 0.012,
        "p3": 0.040,
        "p4": 0.250,
    }
    adj = holm_bonferroni_correction(raw_p, alpha=0.05)
    assert adj["p1"]["p_corrected"] == pytest.approx(0.004)  # 0.001 * 4
    assert adj["p2"]["p_corrected"] == pytest.approx(0.036)  # 0.012 * 3
    assert adj["p3"]["p_corrected"] == pytest.approx(0.080)  # 0.040 * 2
    assert adj["p4"]["p_corrected"] == pytest.approx(0.250)  # 0.250 * 1

    assert adj["p1"]["significant"] is True
    assert adj["p2"]["significant"] is True
    assert adj["p3"]["significant"] is False
    assert adj["p4"]["significant"] is False


def test_calc_ci95():
    vals = np.array([10.0, 11.0, 12.0, 9.0, 10.5])
    low, high = calc_ci95(vals)
    assert low < np.mean(vals) < high
    assert high - low > 0.5
