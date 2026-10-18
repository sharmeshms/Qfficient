# Project Limitations & Boundary Conditions

This document honestly describes known limitations, assumptions, and bounded scopes within Qfficient.

## 1. Classical Execution of Solvers
- Unless a physical D-Wave QPU is explicitly configured via `DWAVE_API_TOKEN` and verified via `solver_backend == "qpu"`, all solvers (`exact_oracle`, `numpy_annealer`, `neal`, `sqa`, `classical`) execute entirely on classical CPU hardware.
- D-Wave Neal is classical simulated annealing (SA).
- OpenJij SQA is classical Markov Chain Monte Carlo Simulated Quantum Annealing (SQA).

## 2. Benchmark Grid Topologies
- Standard feeder benchmark is the textbook IEEE 33-Bus radial distribution feeder.
- Custom procedural microgrids use synthetic topology generation bounded between 10 and 100 components.

## 3. Synthetic Profile Data
- Solar PV drop and EV charging surge transient profiles are generated using parameterized synthetic equations (`RenewableProfileSimulator`) with explicit pseudo-random seeds.
- Field SCADA / real smart-meter telemetry is not bundled in the core repository.

## 4. Voltage Security & Radiality Scope
- Radial tree validity ($|V| - 1$ active lines with zero cycles and full connectivity) is strictly enforced by candidate screening and Kruskal-guided repair.
- ANSI C84.1 voltage tolerances ([0.95, 1.05] p.u.) are evaluated and monitored via LinDistFlow/AC DistFlow power flow; they are not mathematically guaranteed by unconstrained raw QUBO alone.
