# Project Limitations & Boundary Conditions

This document honestly describes known limitations, assumptions, and bounded scopes within Qfficient.

## 1. Classical Execution of Solvers
- Unless a physical D-Wave QPU is explicitly configured via `DWAVE_API_TOKEN` and verified via `solver_backend == "qpu"`, all solvers (`exact_oracle`, `numpy_annealer`, `neal`, `sqa`, `classical`) execute entirely on classical CPU hardware.
- D-Wave Neal is classical simulated annealing (SA).
- OpenJij SQA is classical Markov Chain Monte Carlo Simulated Quantum Annealing (SQA).

## 2. Benchmark Grid Topologies
- Standard feeder benchmark is the textbook IEEE 33-Bus radial distribution feeder.
- Custom procedural microgrids use synthetic topology generation bounded between 10 and 100 components.

## 3. Synthetic Profile Data & Feeder Topologies
- Solar PV drop and EV charging surge transient profiles are generated using parameterized synthetic equations (`RenewableProfileSimulator`, `Scenario.sample`) with explicit pseudo-random seeds.
- Field SCADA / real utility smart-meter telemetry is not bundled in the core repository.
- **IEEE 69-Bus Feeder Scope**: While the procedural generator scales up to 100 components, the textbook 69-bus distribution feeder and external live profiles (e.g. Pecan Street or NREL smart-meter traces) require citable, verified raw netlist files and are deferred to subsequent releases. Benchmark results in this repository are strictly grounded in the verified IEEE 33-bus system.

## 4. Voltage Security & Radiality Scope
- Radial tree validity ($|V| - 1$ active lines with zero cycles and full connectivity) is strictly enforced by candidate screening and Kruskal-guided repair.
- ANSI C84.1 voltage tolerances ([0.95, 1.05] p.u.) are evaluated and monitored via LinDistFlow/AC DistFlow power flow; they are not mathematically guaranteed by unconstrained raw QUBO alone.

## 5. Physical Quantum Hardware Status
- No physical D-Wave QPU hardware run was executed during this benchmark cycle because no active D-Wave Leap hardware API token (`DWAVE_API_TOKEN`) or QPU allocation was provided in the development environment.
- In accordance with our honesty policy, all quantum-annealing benchmarks in `results/` originate from classical OpenJij SQA simulations and D-Wave Neal, and are labeled with `solver_backend` indicating classical simulation.
- The hardware submission path `DWaveQPURunner` is fully implemented and validated via unit testing with mock samplers, ready for hardware execution whenever user credentials are provided (see `docs/QUANTUM_HARDWARE.md`).
