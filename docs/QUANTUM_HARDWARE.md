# Quantum Hardware Execution Guide

This document outlines the quantum hardware submission architecture, graph embedding constraints, and execution requirements for the **Qfficient Thermodynamic QUBO Microgrid Optimizer**.

---

## 1. Overview & Execution Path

Qfficient formulates distribution feeder reconfiguration as a Binary Quadratic Model (BQM) compatible with both classical Ising/QUBO samplers and quantum annealing hardware.

The solver interface `DWaveQPURunner` (`thermodynamic_grid_qubo/solvers/dwave_qpu_runner.py`) provides three execution backends:

| Backend Key | Execution Target | Access Requirement | Reported `solver_backend` |
| :--- | :--- | :--- | :--- |
| `qpu` | Physical Quantum Processing Unit (e.g., D-Wave Advantage System 4.1 / 6.1) via `DWaveSampler` + `EmbeddingComposite` | D-Wave Leap API Token (`DWAVE_API_TOKEN`), `dwave-ocean-sdk` | `"qpu"` |
| `hybrid` | D-Wave Leap Hybrid Solver Service (cloud quantum-classical decomposition) via `LeapHybridSampler` | D-Wave Leap API Token (`DWAVE_API_TOKEN`), `dwave-ocean-sdk` | `"hybrid"` |
| `local_fallback` | Classical Simulated Annealing via `neal.SimulatedAnnealingSampler` | Local CPU (`neal` package) | `"local_fallback"` |

---

## 2. Strict Backend Attribution Policy

> [!IMPORTANT]
> **A run is classified as physical quantum hardware execution if and only if `solver_backend == "qpu"`.**

If `DWAVE_API_TOKEN` is unset, invalid, or network errors occur:
1. The solver falls back gracefully to local classical simulated annealing.
2. The returned metadata explicitly sets `solver_backend = "local_fallback"`.
3. It is strictly prohibited to cite a `local_fallback` run as quantum hardware execution.

---

## 3. Physical QPU Minor Embedding Constraints

The microgrid reconfiguration QUBO Hamiltonian contains a global radiality constraint:
$$H_{rad}(x) = \lambda_{rad} \left( \sum_{e=1}^M x_e - (|V| - N_{sub}) \right)^2$$

Expanding this term couples **every single pair of binary switch decision variables** ($Q_{ab} = 2 \lambda_{rad}$ for all $a < b$). Consequently, the interaction graph is a complete graph (clique) $K_M$:

- **IEEE 33-Bus Feeder ($M = 37$ branches)**:
  - Decision variables: 37 binary variables $+ \text{slack variables}$ ($N \approx 50-60$).
  - Couplings: $C(37, 2) = 666$ quadratic couplings.
  - Native QPU Topology: D-Wave Advantage processors use the **Pegasus graph topology** ($P_{16}$ with degree 15).
  - Minor Embedding: Embedding a dense clique $K_{37}$ requires mapping each logical variable to a chain of multiple physical superconducting qubits.
  - Physical Qubit Usage: Typically requires **150 to 320 physical qubits**.
  - Chain Strength: Must be calibrated to $\sim 1.5 \times \max |Q_{ij}|$ (typically 30–60) to prevent chain breaks while avoiding penalty energy distortion.

- **Scaling to Large Grids ($M > 100$ branches)**:
  - Dense radiality terms produce $> 5,000$ quadratic couplings.
  - Direct minor embedding into physical Advantage QPUs exceeds single-qubit degree limits.
  - Dense large grids must either use `backend="hybrid"` (Leap Hybrid decomposition) or edge-sparsified cycle formulations.

---

## 4. Hardware Telemetry & Reporting

When executing on physical QPU (`solver_backend == "qpu"`), `DWaveQPURunner` captures and logs the following hardware telemetry in `last_qpu_metrics`:

1. `logical_variables`: Count of binary problem variables ($x_e$, slacks).
2. `physical_qubits`: Total physical qubits allocated on the QPU lattice.
3. `max_chain_length`: Maximum physical chain length for any logical variable.
4. `chain_strength`: Ferromagnetic coupling applied along variable chains.
5. `chain_break_fraction`: Measured fraction of broken chains across all sample reads.
6. `annealing_time_us`: Programmed QPU annealing time per read (default: $20\,\mu\text{s}$).
7. `num_reads`: Number of independent annealing cycles executed.
8. `wall_clock_ms`: Total submission and HTTP roundtrip latency.
9. `timing`: Detailed D-Wave timing breakdown (QPU programming time, sampling time, post-processing time).

---

## 5. How to Run with Hardware Credentials

To run against D-Wave Leap hardware:

### Option A: Direct QPU Execution in Python
```python
import os
from thermodynamic_grid_qubo.qubo_engine.qubo_builder import ThermodynamicQUBOBuilder
from thermodynamic_grid_qubo.solvers.dwave_qpu_runner import DWaveQPURunner

# Set your API token
os.environ["DWAVE_API_TOKEN"] = "DEV-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Initialize direct QPU runner
runner = DWaveQPURunner(backend="qpu")
sample, energy, ms, response = runner.solve(bqm, num_reads=100)

print(f"Backend executed: {runner.solver_backend}")
print(f"Hardware metrics: {runner.last_qpu_metrics}")
```

### Option B: Via the Pipeline
```python
from thermodynamic_grid_qubo.pipeline import OptimizationConfig, run_optimization

cfg = OptimizationConfig(
    grid="ieee33",
    solver="dwave_qpu", # Automatically enabled when DWAVE_API_TOKEN is set
    time_steps=5,
)
result = run_optimization(cfg)
print(f"True backend: {result['solver_backend']}")
```
