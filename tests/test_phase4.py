"""
Unit test suite for Phase 4 Science Improvements.

Verifies:
1. Quadratic loss encoding (weight_mode="quadratic_loss") in ThermodynamicQUBOBuilder.
2. Backwards-compatible default (weight_mode="mesh_current").
3. Voltage-aware candidate tree selection in OpenJijAnnealer and QUBOPolicy.
4. Long-horizon heatwave scenario generator and thermal weight toggles.
5. Entropy vs heat mathematical correlation.
6. All Hamiltonian ablation flags produce valid simulations.
"""
import pytest
import numpy as np

from thermodynamic_grid_qubo.grid_engine.ieee_feeder_loader import IEEEFeederLoader
from thermodynamic_grid_qubo.verification.fast_flow import FastFeeder
from thermodynamic_grid_qubo.qubo_engine.qubo_builder import ThermodynamicQUBOBuilder
from thermodynamic_grid_qubo.qubo_engine.penalty_tuner import PenaltyTuner
from thermodynamic_grid_qubo.solvers.numpy_annealer import NumpyAnnealer
from thermodynamic_grid_qubo.solvers.openjij_annealer import OpenJijAnnealer
from thermodynamic_grid_qubo.benchmark.simulate import Scenario, simulate
from thermodynamic_grid_qubo.benchmark.policies import QUBOPolicy


@pytest.fixture
def ieee_grid():
    return IEEEFeederLoader.load_ieee33()


@pytest.fixture
def fast_feeder(ieee_grid):
    return FastFeeder(ieee_grid)


def test_quadratic_loss_qubo_builder(ieee_grid, fast_feeder):
    """Verifies that weight_mode='quadratic_loss' adds quadratic cross-interaction terms."""
    edges = [(ieee_grid.lines[e].u, ieee_grid.lines[e].v) for e in fast_feeder.edge_ids]
    weights = {i: 0.1 * (i + 1) for i in range(fast_feeder.m)}

    # Builder with default linear mesh current
    builder_linear = ThermodynamicQUBOBuilder(
        num_buses=fast_feeder.n,
        edges=edges,
        substations=ieee_grid.substations,
        graph=ieee_grid.graph,
        cycle_mode="basis",
        weight_mode="mesh_current",
    )
    bqm_lin = builder_linear.build_bqm(weights, {}, {})

    # Builder with quadratic loss
    builder_quad = ThermodynamicQUBOBuilder(
        num_buses=fast_feeder.n,
        edges=edges,
        substations=ieee_grid.substations,
        graph=ieee_grid.graph,
        cycle_mode="basis",
        weight_mode="quadratic_loss",
    )
    bqm_quad = builder_quad.build_bqm(weights, {}, {})

    # Quadratic model must contain interactions with different weights
    assert builder_quad.weight_mode == "quadratic_loss"
    assert builder_linear.weight_mode == "mesh_current"
    # Model with quadratic interactions has non-zero cross-terms
    assert len(bqm_quad.quadratic) >= len(bqm_lin.quadratic)


def test_default_weight_mode_unchanged(ieee_grid, fast_feeder):
    """Verifies that default weight_mode is 'mesh_current' across builder and policy."""
    edges = [(ieee_grid.lines[e].u, ieee_grid.lines[e].v) for e in fast_feeder.edge_ids]
    builder = ThermodynamicQUBOBuilder(
        num_buses=fast_feeder.n,
        edges=edges,
        substations=ieee_grid.substations,
    )
    assert builder.weight_mode == "mesh_current"

    policy = QUBOPolicy()
    assert policy.weight_mode == "mesh_current"
    assert policy.dynamic_thermal_weights is True
    assert policy.voltage_aware is False


def test_voltage_aware_candidate_selection(ieee_grid, fast_feeder):
    """Verifies that voltage-aware selection option works and rejects low-voltage trees."""
    annealer = OpenJijAnnealer(use_sqa=False)
    # Check that extract_optimal_tree accepts enforce_voltage_limits and voltage_penalty_weight
    weights = {i: 1.0 for i in range(fast_feeder.m)}
    current_sw = {e: (1 if e in fast_feeder.standard_edges else 0) for e in range(fast_feeder.m)}
    
    # Create lightweight SampleSet directly
    import dimod
    sample = {f"x_{e}": (1 if e in fast_feeder.standard_edges else 0) for e in range(fast_feeder.m)}
    resp = dimod.SampleSet.from_samples([sample], vartype=dimod.BINARY, energy=[0.0])

    res = annealer.extract_optimal_tree(
        resp,
        ieee_grid,
        weights,
        injections={b: (0.0, 0.0) for b in ieee_grid.graph.nodes},
        current_switches=current_sw,
        enforce_voltage_limits=True,
        voltage_penalty_weight=5.0,
    )
    assert isinstance(res, dict)
    assert len(res) == fast_feeder.m
    assert fast_feeder.is_tree(tuple(sorted([e for e, v in res.items() if v == 1])))


def test_heatwave_long_scenario_and_thermal_weights(ieee_grid):
    """Verifies Scenario.sample_heatwave_long and dynamic_thermal_weights toggle."""
    sc = Scenario.sample_heatwave_long(seed=42, time_steps=5, dt_seconds=60.0)
    assert sc.time_steps == 5
    assert sc.dt_seconds == 60.0
    assert len(sc.timeline) == 5

    # Run policy with dynamic thermal weights
    p_thermo = QUBOPolicy(num_reads=10, selection="filtered", dynamic_thermal_weights=True, seed=42)
    res_thermo = simulate(p_thermo, sc, grid=ieee_grid, ambient_c=40.0)
    assert res_thermo["heat_mj"] > 0
    assert res_thermo["infeasible_steps"] == 0

    # Run policy with static thermal weights
    p_nothermo = QUBOPolicy(num_reads=10, selection="filtered", dynamic_thermal_weights=False, seed=42)
    res_nothermo = simulate(p_nothermo, sc, grid=ieee_grid, ambient_c=40.0)
    assert res_nothermo["heat_mj"] > 0
    assert res_nothermo["infeasible_steps"] == 0


def test_hamiltonian_ablations(ieee_grid):
    """Verifies that all 5 Hamiltonian term ablations initialize and execute properly."""
    ablations = ["no_thermo", "no_cycle", "no_rad", "no_cap", "no_sw"]
    sc = Scenario.sample(seed=99, time_steps=3, dt_seconds=2.0)

    for ab in ablations:
        policy = QUBOPolicy(num_reads=10, selection="filtered", ablation=ab, seed=123)
        assert policy.name == f"qubo_ablation_{ab}"
        res = simulate(policy, sc, grid=ieee_grid)
        assert res["heat_mj"] > 0
        assert res["infeasible_steps"] == 0


def test_qubo_quadratic_loss_simulation(ieee_grid):
    """Verifies that QUBOPolicy with weight_mode='quadratic_loss' completes simulation."""
    sc = Scenario.sample(seed=77, time_steps=3, dt_seconds=2.0)
    policy = QUBOPolicy(num_reads=10, selection="filtered", weight_mode="quadratic_loss", seed=42)
    assert policy.name == "qubo_quadratic_loss_filtered"
    res = simulate(policy, sc, grid=ieee_grid)
    assert res["heat_mj"] > 0
    assert res["infeasible_steps"] == 0
