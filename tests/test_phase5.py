"""
Unit tests for Phase 5 Quantum Hardware Path.

Verifies:
1. DWaveQPURunner gracefully falls back to classical Neal when token is absent.
2. solver_backend is strictly reported as 'local_fallback' and never mislabeled as quantum.
3. Mocked physical QPU path captures embedding telemetry (physical qubits, chain length, etc.).
4. Mocked Leap Hybrid path captures hybrid execution telemetry.
5. Pipeline run_optimization reports honest solver_backend field.
"""
from unittest.mock import MagicMock, patch
import dimod
import pytest
import numpy as np

from thermodynamic_grid_qubo.solvers.dwave_qpu_runner import DWaveQPURunner
from thermodynamic_grid_qubo.pipeline import OptimizationConfig, run_optimization


@pytest.fixture
def sample_bqm():
    """Generates a small 5-variable Binary Quadratic Model."""
    bqm = dimod.BinaryQuadraticModel(dimod.BINARY)
    for i in range(5):
        bqm.add_variable(f"x_{i}", 1.0)
    bqm.add_interaction("x_0", "x_1", 2.0)
    bqm.add_interaction("x_1", "x_2", -1.5)
    return bqm


def test_dwave_qpu_runner_fallback_without_token(sample_bqm):
    """Verifies that DWaveQPURunner defaults to local classical fallback when token is missing."""
    runner = DWaveQPURunner(token="", backend="auto")
    sample, energy, elapsed_ms, response = runner.solve(sample_bqm, num_reads=20)

    assert runner.solver_backend == "local_fallback"
    assert isinstance(sample, dict)
    assert len(sample) == 5
    assert elapsed_ms > 0
    assert "backend_note" in runner.last_qpu_metrics
    assert "No QPU hardware execution occurred" in runner.last_qpu_metrics["backend_note"]


def test_dwave_qpu_mocked_physical_hardware(sample_bqm):
    """Verifies that direct QPU submission records physical embedding metrics when QPU runs."""
    import sys
    mock_response = dimod.SampleSet.from_samples(
        [{f"x_{i}": 0 for i in range(5)}],
        vartype=dimod.BINARY,
        energy=[0.0],
        chain_break_fraction=[0.02],
    )
    mock_response.info["timing"] = {"qpu_anneal_time_per_sample": 20}

    mock_composite = MagicMock()
    mock_composite.sample.return_value = mock_response
    mock_composite.embedding = {
        "x_0": [10, 11],
        "x_1": [12, 13, 14],
        "x_2": [15],
        "x_3": [16, 17],
        "x_4": [18],
    }

    mock_sampler_cls = MagicMock()
    mock_system = MagicMock()
    mock_system.DWaveSampler = mock_sampler_cls
    mock_system.EmbeddingComposite = MagicMock(return_value=mock_composite)

    with patch.dict(sys.modules, {"dwave.system": mock_system}):
        runner = DWaveQPURunner(token="mock_token_123", backend="qpu")
        sample, energy, elapsed_ms, response = runner.solve(sample_bqm, num_reads=50)

        assert runner.solver_backend == "qpu"
        metrics = runner.last_qpu_metrics
        assert metrics["logical_variables"] == 5
        assert metrics["physical_qubits"] == 9  # 2 + 3 + 1 + 2 + 1
        assert metrics["max_chain_length"] == 3  # chain for x_1 has length 3
        assert metrics["chain_break_fraction"] == pytest.approx(0.02)
        assert metrics["annealing_time_us"] == 20


def test_dwave_hybrid_mocked_execution(sample_bqm):
    """Verifies that Leap Hybrid submission records hybrid execution telemetry."""
    import sys
    mock_response = dimod.SampleSet.from_samples(
        [{f"x_{i}": 1 for i in range(5)}],
        vartype=dimod.BINARY,
        energy=[1.5],
    )
    mock_response.info["qpu_access_time"] = 15000

    mock_hybrid = MagicMock()
    mock_hybrid.sample.return_value = mock_response
    mock_system = MagicMock()
    mock_system.LeapHybridSampler = MagicMock(return_value=mock_hybrid)

    with patch.dict(sys.modules, {"dwave.system": mock_system}):
        runner = DWaveQPURunner(token="mock_token_123", backend="hybrid")
        sample, energy, elapsed_ms, response = runner.solve(sample_bqm)

        assert runner.solver_backend == "hybrid"
        assert runner.last_qpu_metrics["logical_variables"] == 5
        assert runner.last_qpu_metrics["qpu_access_time_us"] == 15000


def test_pipeline_solver_backend_reporting():
    """Verifies that run_optimization accurately reports solver_backend."""
    cfg = OptimizationConfig(grid="microgrid12", solver="neal", time_steps=2)
    res = run_optimization(cfg)
    assert res["solver_backend"] == "neal_classical_sa"

    cfg_oracle = OptimizationConfig(grid="microgrid12", solver="exact_oracle", time_steps=2)
    res_oracle = run_optimization(cfg_oracle)
    assert res_oracle["solver_backend"] == "classical_exact_oracle"
