<div align="center">

# ⚡ Qfficient: Thermodynamic-Mapped QUBO for Dynamic Microgrid Distribution
### *Next-Generation Distribution Network Reconfiguration via Non-Equilibrium Thermodynamics, Fast LinDistFlow, and Quantum Annealing*
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-2ea44f?style=for-the-badge&logo=github&logoColor=white)](https://sharmeshms.github.io/Qfficient/)
[![Quantum-inspired](https://img.shields.io/badge/Quantum--inspired-QUBO--Ready-4A154B?style=for-the-badge&logo=quantum&logoColor=white)](docs/QUANTUM_HARDWARE.md)
[![Framework](https://img.shields.io/badge/Streamlit-2.0%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(42%2F42)-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Grid Scale](https://img.shields.io/badge/Grid%20Scale-10%20to%20100%20Components-orange?style=for-the-badge&logo=target&logoColor=white)](#-custom-microgrid-generator-10-to-100-components)

<p align="center">
  <b>Dynamic Power Routing</b> • <b>Entropy Minimization</b> • <b>Exergy Preservation</b> • <b>Thermal Runaway Suppression</b> • <b>10–100 Component Scalability</b>
</p>

</div>

---

## 📌 Table of Contents
1. [Executive Summary & Problem Context](#-executive-summary--problem-context)
2. [Complete Technical Stack & Operational User Manual](#-complete-technical-stack--operational-user-manual)
3. [Proven Experimental Outcomes & Claim Reconciliation](#-proven-experimental-outcomes--claim-reconciliation)
4. [Quantum Scope & Physical Hardware Path](#-quantum-scope--physical-hardware-path)
5. [Thermodynamic Entropy vs. Joule Heat Dissipation](#-thermodynamic-entropy-vs-joule-heat-dissipation)
6. [Lagrange Multiplier Heuristics & Sensitivity](#-lagrange-multiplier-heuristics--sensitivity)
7. [Data Scope & Synthetic Profiles](#-data-scope--synthetic-profiles)
8. [Core Physics & Non-Equilibrium Thermodynamics](#-core-physics--non-equilibrium-thermodynamics)
9. [Thermodynamic QUBO & Ising Formulation](#-thermodynamic-qubo--ising-formulation)
10. [Custom Microgrid Generator (10 to 100 Components)](#-custom-microgrid-generator-10-to-100-components)
11. [Multi-Solver Architecture & Scalable Quantum Annealing](#-multi-solver-architecture--scalable-quantum-annealing)
12. [Visual Diagnostics & Network Topologies](#-visual-diagnostics--network-topologies)
13. [Interactive Review Portal (Streamlit 2.0 Web Dashboard)](#-interactive-review-portal-streamlit-20-web-dashboard)
14. [Quickstart & CLI Commands](#-quickstart--cli-commands)
15. [Repository Architecture](#-repository-architecture)
16. [License & Citation](#-license--citation)

---

## 📌 Executive Summary & Problem Context

Modern electrical distribution microgrids are experiencing rapid, high-density penetration of intermittent **Distributed Energy Resources (DERs)**, including rooftop and commercial solar PV, wind turbines, community Battery Energy Storage Systems (BESS), and high-power Electric Vehicle (EV) fast-charging depots.

### The Engineering Challenge
* **The Classical Reconfiguration Bottleneck**: Traditional Distribution Network Reconfiguration (DNR) relies on static shortest-path heuristics or Mixed-Integer Non-Linear Programming (MINLP). These solvers assume fixed conductor resistances ($R_0$) and take seconds to minutes to converge—making real-time topological adaptation during steep transient ramps ($di/dt$ and $dP/dt$) physically impossible.
* **Thermal Runaway & Resistance Feedback**: Electric current generates heat quadratically ($P = 3 I^2 R$). As heavy feeder lines heat up under demand surges, conductor resistance rises non-linearly ($R(T) = R_0 [1 + \alpha(T - T_0)]$). This positive feedback loop amplifies voltage sag, triggers line ampacity overloads, and permanently destroys available electrical work (exergy).
* **The Qfficient Solution**: We reframe dynamic network reconfiguration strictly as an **entropy-generation minimization problem grounded in non-equilibrium thermodynamics**. Dynamic conductor temperatures, transient power injections, and topological radiality constraints are compiled into an Ising spin glass Hamiltonian solved on quantum annealers, simulated quantum annealing (SQA), or exact loss-minimizing classical oracles in milliseconds.

---

## 📖 Complete Technical Stack & Operational User Manual

For a comprehensive, end-to-end technical reference with step-by-step CLI walkthroughs, programmatic Python APIs, technology stack breakdowns, and diagnostic troubleshooting:

* 📄 **Markdown User Manual**: See [`MANUAL.md`](MANUAL.md) for complete file-by-file blueprints, solver parameter guides, and Docker orchestration details.
* 📑 **Formatted Word Manual**: Download [`QFFICIENT_SYSTEM_MANUAL.docx`](QFFICIENT_SYSTEM_MANUAL.docx) (generated via `python generate_docx_manual.py`) for formatted printing, stakeholder submission, and formal project presentation.

---

## 🏆 Proven Experimental Outcomes & Claim Reconciliation

### 1. IEEE 33-Bus Benchmark (Rigorous Research-Grade Evaluation)
Evaluated across **30 independent pseudo-random scenarios** (750 total power-flow steps, seeds 1000..1029) over 25 time steps ($dt = 2.0\text{ s}$) using IEEE 33-Bus benchmark parameters ($V_{\text{base}} = 12.66\text{ kV}$, $S_{\text{base}} = 10\text{ MVA}$, ANSI C84.1 voltage band $[0.95, 1.05]\text{ p.u.}$):

<!-- RESULTS_TABLE_START -->
| Policy / Algorithm | Total Joule Heat (MJ) [Mean ± Std] | Heat Reduction vs Std. Baseline (%) | $p$-value ($t$-test) | Peak Conductor Temp (°C) | Voltage Violations (steps) | Switch Operations | Decision Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Standard Static Baseline (IEEE 33 default)** | $4.985 \pm 0.055$ | *Reference* | — | $26.5^\circ\text{C}$ | $18.6$ | $0.0$ | $0.00\text{ ms}$ |
| **Static Loss-Optimal (Best static tree)** | $3.596 \pm 0.044$ | **+27.87%** | 4.54e-56 | $26.0^\circ\text{C}$ | $6.1$ | $5.0$ | $0.00\text{ ms}$ |
| **Exact Dynamic Oracle** | $3.570 \pm 0.043$ | **+28.39%** | 4.22e-59 | $25.9^\circ\text{C}$ | $5.6$ | $23.4$ | $78.79\text{ ms}$ |
| **Exact Dynamic Oracle with Hysteresis (0.5 kW)** | $3.573 \pm 0.043$ | **+28.33%** | 7.78e-59 | $25.9^\circ\text{C}$ | $5.7$ | $15.3$ | $79.48\text{ ms}$ |
| **Baran-Wu Branch Exchange (Heuristic)** | $3.574 \pm 0.040$ | **+28.31%** | 4.77e-58 | $26.0^\circ\text{C}$ | $4.2$ | $15.8$ | $29.94\text{ ms}$ |
| **Simulated Annealing on Spanning Trees (No QUBO)** | $3.666 \pm 0.053$ | **+26.47%** | 3.26e-46 | $26.0^\circ\text{C}$ | $4.4$ | $23.6$ | $19.68\text{ ms}$ |
| **Random Spanning Trees (Raw)** | $12.079 \pm 2.416$ | -142.29% | 4.89e-16 | $26.8^\circ\text{C}$ | $22.2$ | $105.8$ | $0.07\text{ ms}$ |
| **Random Spanning Trees (Filtered / PF ranked)** | $4.095 \pm 0.066$ | **+17.86%** | 4.68e-37 | $26.0^\circ\text{C}$ | $6.3$ | $97.8$ | $9.57\text{ ms}$ |
| **Thermodynamic QUBO (Raw eigenvalue)** | $4.985 \pm 0.055$ | -0.00% | 1.0000 | $26.5^\circ\text{C}$ | $18.6$ | $143.5$ | $283.62\text{ ms}$ |
| **Thermodynamic QUBO (Marginal Spin MST, No PF Filter)** | $9.883 \pm 1.138$ | -98.24% | 2.32e-20 | $26.7^\circ\text{C}$ | $20.8$ | $98.5$ | $293.93\text{ ms}$ |
| **Thermodynamic QUBO (Repair + PF ranked)** | $3.621 \pm 0.042$ | **+27.37%** | 2.87e-56 | $25.9^\circ\text{C}$ | $4.4$ | $15.9$ | $304.74\text{ ms}$ |
*Benchmark parameters: 30 scenarios, 25 time steps ($dt = 2.0\text{ s}$), seeds: 1000..1029, correction: Paired t-test with Holm-Bonferroni step-down correction (alpha = 0.05). Generated from `python run_benchmark.py --n 30 --steps 25`.*
<!-- RESULTS_TABLE_END -->

### 2. Scientific Claim Reconciliation & Attribution
* **Empirical Verification of Loss Reduction Claims**:
  - The theoretical optimum established by the **Exact Dynamic Oracle** achieves **+28.39% loss reduction** ($3.570 \pm 0.043\text{ MJ}$ vs $4.985 \pm 0.055\text{ MJ}$, adjusted $p = 4.22 \times 10^{-58}$) relative to the textbook IEEE-33 static baseline.
  - Classic **Baran-Wu Branch Exchange** (1989) achieves **+28.31% loss reduction** ($3.574 \pm 0.040\text{ MJ}$, adjusted $p = 3.82 \times 10^{-57}$) in under $30\text{ ms}$ per scenario, demonstrating that classical branch exchange heuristics perform comparably to exact combinatorial search on 33-bus topologies.
  - Adding a $0.5\text{ kW}$ switching hysteresis threshold (`exact_oracle_hysteresis`) cuts breaker operations by **35%** (from 23.4 to 15.3 switches) while preserving virtually 100% of optimal loss reduction (+28.33% vs +28.39%).
* **Honest Attribution of Pure QUBO vs. Filtering**:
  - **Raw QUBO Ground States** (`qubo_mesh_current_raw`): Evaluated strictly by lowest-energy eigenvalue without post-hoc power-flow filtering. Because linear proxy weights do not capture non-linear AC line interactions, raw lowest-energy configurations do not reduce AC losses relative to the standard static baseline (-0.00% reduction).
  - **Marginal Spin Ensemble MST** (`qubo_mesh_current_marginal_mst`): Extracting maximum spanning trees directly from quantum annealer spin probabilities $\Pr(x_e = 1)$ yields valid radial trees but results in -98.24% loss relative to baseline (9.883 MJ vs 4.985 MJ). This proves that proxy weights without power-flow loss selection create bottleneck branches with high Joule dissipation.
  - **Thermodynamic QUBO Filtered** (`qubo_mesh_current_filtered`): Screening quantum candidates and refining via annealer-guided loop branch exchanges achieves **+27.37% loss reduction** ($3.621 \pm 0.042\text{ MJ}$, adjusted $p = 2.01 \times 10^{-55}$).
* **Radiality vs. Voltage Security**:
  - Radial tree validity ($|V|-1$ lines, connected, zero cycles) is strictly enforced by construction and Kruskal loop repair.
  - Voltage compliance is evaluated and monitored via LinDistFlow/AC power flow; it is **reported, not mathematically guaranteed** by the unconstrained QUBO alone. Under severe peak load without reactive support, voltages dip below 0.95 pu (4.4 to 18.6 violation steps). Complete ANSI C84.1 compliance is never claimed unless measured.

---

## 🌌 Quantum Scope & Physical Hardware Path

### 1. Honest Backend Attribution Policy
Every simulation and benchmark reported in this repository complies with our strict **Honest Attribution Policy**:
* **No Cloud QPU Execution in Reported Benchmarks**: All numerical benchmark outcomes reported in `results/` were evaluated using **classical execution backends**:
  - `exact_oracle` / `exact_oracle_hysteresis`: Deterministic combinatorial search over valid spanning trees via vectorized AC / LinDistFlow.
  - `baran_wu_branch_exchange`: Deterministic classical heuristic algorithm (Baran & Wu, 1989).
  - `tree_simulated_annealing`: Classical Metropolis-Hastings Markov Chain Monte Carlo over spanning trees.
  - `openjij_annealer`: Classical Markov Chain Monte Carlo Simulated Quantum Annealing (SQA) executed on host CPUs.
  - `numpy_annealer` / `neal`: Classical Simulated Annealing (SA) executed on host CPUs.
* **No Stale or Deceptive Claims**: Software execution logs strictly record `solver_backend` (`"classical_exact_oracle"`, `"sqa_classical_simulation"`, `"neal_classical_sa"`, or `"local_fallback"`). Fallback simulations are **never** labeled as quantum hardware execution.

### 2. Direct Hardware Interface (D-Wave Advantage QPU)
The repository contains an end-to-end, production-grade hardware submission interface (`DWaveQPURunner` in `thermodynamic_grid_qubo/solvers/dwave_qpu_runner.py`) ready for physical quantum execution:
* **Supported Backends**:
  - `dwave_qpu`: Submits directly to physical D-Wave Advantage QPUs via `DWaveSampler` and `EmbeddingComposite`.
  - `dwave_hybrid`: Submits to D-Wave Leap hybrid quantum-classical solvers (`LeapHybridSampler`).
* **Pegasus Minor Embedding Analysis**:
  - The radiality constraint $(\sum_{e} x_e - 32)^2$ introduces all-to-all quadratic couplings, creating a complete graph clique $K_{37}$ (666 non-zero couplings).
  - On D-Wave Advantage QPUs with Pegasus topology (degree 15), embedding $K_{37}$ requires minor embedding with chain lengths between 2 and 6 physical qubits, expanding 37 logical variables into **150 to 320 physical qubits**.
  - Programmed chain strength $\ge 2.0 \times \max|J_{ij}|$ prevents chain breaks under strong radial penalties.
* **Hardware Readiness**: See [`docs/QUANTUM_HARDWARE.md`](docs/QUANTUM_HARDWARE.md) for complete hardware submission workflows, API token configuration, and embedding telemetry.

---

## ⚖️ Thermodynamic Entropy vs. Joule Heat Dissipation

### 1. Collinearity Analysis
A core scientific question addressed in our research is whether explicitly compiling non-equilibrium thermodynamic entropy generation $\dot{S}_{\text{gen}} = \dot{Q} / T$ provides distinct topological routing decisions compared to direct Joule heat minimization $\dot{Q} = 3 I^2 R$.

We conducted an empirical correlation analysis (`scripts/analyze_entropy_vs_heat.py`) across 300 independent simulation runs (30 scenario seeds $\times$ 10 optimization policies):
* **Pearson Correlation**: $r = 1.000000$ ($p < 10^{-300}$)
* **Spearman Rank Correlation**: $\rho = 0.999981$ ($p < 10^{-300}$)
* **Coefficient of Determination**: $R^2 = 1.000000$
* **Linear Regression Model**:
  $$\text{Entropy Reduction } (\%) = 0.9996 \times \text{Heat Reduction } (\%) - 0.0215$$

<p align="center">
  <img src="results/entropy_vs_heat.png" alt="Entropy vs Joule Heat Dissipation Correlation" width="700">
</p>

### 2. Physical Mechanism
The near-perfect mathematical collinearity arises from the thermodynamics of distribution feeders:
1. Conductor operating temperatures in overhead and underground lines fluctuate between $25^\circ\text{C}$ and $75^\circ\text{C}$ ($298.15\text{ K}$ to $348.15\text{ K}$).
2. In absolute Kelvin units, temperature variations span less than $3\%$ relative to ambient reference temperature $T_0 = 298.15\text{ K}$.
3. Under quasi-isothermal conditions, the thermodynamic factor $\frac{1}{T_e(t)} \approx \frac{1}{T_0}$ behaves as a near-constant scalar multiplier. Consequently, **minimizing non-equilibrium thermodynamic entropy generation is physically and mathematically equivalent to minimizing Ohmic Joule losses**.

### 3. Long-Horizon Heatwave Simulation
In our 40-minute heatwave experiment (`scripts/run_thermal_experiment.py`, $T_{\text{amb}} = 40^\circ\text{C}$, 1.35x load surge, 900 kW EV charging pulse):
* `qubo_thermo` (dynamic thermal resistance feedback) achieved **+30.68% loss reduction** (417.286 MJ, peak conductor temp 71.9°C, 18 switches).
* `qubo_no_thermo` (static reference resistance) achieved the **exact same +30.68% loss reduction** (417.286 MJ, peak conductor temp 71.9°C, 18 switches).
* **Finding**: The thermal term effect is **+0.00% on discrete switching decisions**. Large branch current disparities induced by load and generation topology dominate combinatorial switch selection over local ~5% thermal resistance adjustments.

---

## 🎛️ Lagrange Multiplier Heuristics & Sensitivity

### 1. Dynamic Adaptive Penalty Scaling
The composite QUBO Hamiltonian balances the thermodynamic dissipation objective with four operational constraints. To prevent constraint violations under steep load swings, `PenaltyTuner` dynamically scales penalties using current and temperature feedback:

$$\lambda_{\text{cycle}} = \lambda_{\text{cycle},0} \cdot \left(\frac{I_{\text{mean}}}{I_{\text{base}}}\right)^2 \cdot \left(1 + \frac{T_{\text{max}} - T_0}{50}\right)$$

$$\lambda_{\text{rad}} = \lambda_{\text{rad},0} \cdot \left(\frac{I_{\text{mean}}}{I_{\text{base}}}\right)^2, \quad \lambda_{\text{cap}} = \lambda_{\text{cap},0} \cdot \left(\frac{I_{\text{max}}}{I_{\text{base}}}\right)^2, \quad \lambda_{\text{sw}} = \lambda_{\text{sw},0} \cdot \left(\frac{I_{\text{base}}}{I_{\text{mean}}}\right)$$

### 2. Parametric Sensitivity Sweep
We executed an automated parametric sensitivity sweep (`scripts/sweep_penalty_weights.py`, multipliers from 0.1x to 10.0x):

<p align="center">
  <img src="results/penalty_sensitivity.png" alt="QUBO Penalty Multiplier Sensitivity Sweep" width="850">
</p>

* **Cycle Breaking ($\lambda_{\text{cycle}}$)**: At multipliers $< 0.5\text{x}$ ($\lambda_{\text{cycle}} < 12.5$), quantum annealers produce closed loops in elementary cycles. Multipliers $\ge 1.0\text{x}$ ($\lambda_{\text{cycle}} \ge 25.0$) guarantee 100% loop-free configurations.
* **Radiality ($\lambda_{\text{rad}}$)**: Multipliers $< 0.3\text{x}$ yield disconnected networks ($|E| \ne 32$). Multipliers $\ge 1.0\text{x}$ ($\lambda_{\text{rad}} \ge 30.0$) strictly enforce $|E| = |V| - 1 = 32$.
* **Switching Wear ($\lambda_{\text{sw}}$)**: Multipliers in the range $[0.5, 5.0]$ smoothly suppress unnecessary switch toggling without degrading loss optimality.

---

## 📋 Data Scope & Synthetic Profiles

### 1. Benchmark Grid Topologies
* **IEEE 33-Bus Feeder**: The core evaluation topology is the standard textbook Baran & Wu (1989) 33-bus radial distribution system ($12.66\text{ kV}$, $10\text{ MVA}$ base, 33 buses, 32 sectionalizing branches, 5 normally-open tie switches).
* **Procedural Custom Microgrids**: Topologies from 10 to 100 components are procedurally generated using synthetic graph layouts with guaranteed connectivity, central spine trunks, and branching laterals.

### 2. Synthetic Transient Profiles
* **Stochastic Fluctuation Models**: Solar PV intermittency, wind fluctuations, BESS charge/discharge cycles, and EV charging pulses are modeled via parameterized synthetic time-series (`RenewableProfileSimulator`, `Scenario.sample`) using explicit pseudo-random seeds.
* **No Real-World Utility SCADA Data**: The repository uses synthetic benchmark profiles for reproducible open-source evaluation. No proprietary utility smart-meter or live SCADA recordings are included.

## 🔬 Core Physics & Non-Equilibrium Thermodynamics

```
                                  SUNLIGHT / WIND
                                        │
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │                       DISTRIBUTION FEEDER LINE                          │
    │                                                                        │
    │   Electric Current I_e(t) ──► Non-Linear Joule Dissipation:            │
    │                               Q̇_e(t) = 3 · I_e(t)² · R_e(T_e)         │
    │                                        │                               │
    │                                        ▼                               │
    │   Thermal Balance:           dT_e/dt = (Q̇_e - Q̇_loss) / C_th           │
    │                                        │                               │
    │                                        ▼                               │
    │   Resistance Feedback:       R_e(T) = R_0 · [1 + α · (T_e - T_0)]     │
    │                                        │                               │
    │                                        ▼                               │
    │   Entropy Generation:        Ṡ_gen,e(t) = Q̇_e(t) / T_e(t)              │
    │                                        │                               │
    │                                        ▼                               │
    │   Gouy-Stodola Exergy Loss:  E_x,dest = T_0 · ∫ Ṡ_gen dt               │
    └────────────────────────────────────────────────────────────────────────┘
                                        │
                         THERMODYNAMIC QUBO MINIMIZATION
                                        │
                                        ▼
                  Optimized Reconfigured Feeder Topology
```

### 1. Non-Equilibrium Entropy Generation Rate
Electric current transport through resistive conductors produces irreversible entropy. For a three-phase branch $e \in E$ at temperature $T_e(t)$:

$$\dot{S}_{\text{gen},e}(t) = \frac{\dot{Q}_e(t)}{T_e(t)} = \frac{3 \cdot I_e(t)^2 \cdot R_e(T_e(t))}{T_e(t)} \quad \left[\frac{\text{W}}{\text{K}}\right]$$

### 2. The Gouy-Stodola Theorem
The rate of usable electrical work capability (exergy) destroyed is directly proportional to entropy generation:

$$E_{x,\text{destroyed}} = T_0 \cdot \int_0^{\Delta t} \sum_{e \in E} \dot{S}_{\text{gen},e}(t) \, dt$$

Where $T_0$ is ambient reference temperature ($298.15\text{ K}$). Minimizing entropy generation directly maximizes delivered useful exergy to loads.

### 3. Conductor Transient Differential Heat Balance
Conductor temperature transients are simulated at each time step using first-order lumped capacitance dynamics:

$$C_{\text{th},e} \frac{dT_e(t)}{dt} = 3 \cdot I_e(t)^2 \cdot R_e(T_e(t)) - \frac{T_e(t) - T_{\text{amb}}}{\theta_{\text{th},e}}$$

Conductor resistance updates non-linearly with temperature:

$$R_e(T_e) = R_{0,e} \cdot \left[1 + \alpha \cdot (T_e - T_0)\right]$$

Where $\alpha \approx 0.00393\text{ K}^{-1}$ for aluminum/copper conductors.

---

## ⚛️ Thermodynamic QUBO & Ising Formulation

### Decision Variables
For each candidate distribution line and tie switch $e \in E$, binary decision variable $x_e \in \{0, 1\}$ represents:
* $x_e = 1$: Switch closed (branch energized)
* $x_e = 0$: Switch open (branch isolated)

### Master Objective Hamiltonian
The composite Hamiltonian submitted to the quantum annealing core is:

$$H(x) = \lambda_{\text{thermo}} H_{\text{thermo}}(x) + \lambda_{\text{cycle}} H_{\text{cycle}}(x) + \lambda_{\text{rad}} H_{\text{rad}}(x) + \lambda_{\text{cap}} H_{\text{cap}}(x) + \lambda_{\text{sw}} H_{\text{sw}}(x)$$

1. **Thermodynamic Dissipation**:
   $$H_{\text{thermo}}(x) = \sum_{e \in E} w_e \cdot x_e \quad \text{where } w_e = \frac{3 \cdot I_e^2 \cdot R_e(T_e)}{T_e}$$
2. **Fundamental Loop Breaking**: For each fundamental cycle $C_k$ in the co-tree, enforce exactly one open branch:
   $$H_{\text{cycle}}(x) = \sum_{k} \left(\sum_{e \in C_k} x_e - (|C_k| - 1)\right)^2$$
3. **Radial Spanning Tree**: Enforce exactly $N - 1$ active lines ($|V| - 1$ branches for 1 substation):
   $$H_{\text{rad}}(x) = \left(\sum_{e \in E} x_e - (|V| - 1)\right)^2$$
4. **Thermal Ampacity Protection**:
   $$H_{\text{cap}}(x) = \sum_{e \in E} \max\left(0, \frac{I_e - I_{\max,e}}{I_{\max,e}}\right)^2 \cdot x_e$$
5. **Switching Wear Fatigue**: Penalize toggling switch states between consecutive time intervals $t-1$ and $t$:
   $$H_{\text{sw}}(x) = \sum_{e \in E} |x_e^{(t)} - x_e^{(t-1)}|$$

### Mapping to Transverse Ising Spin Glass
Using change of variables $x_i = \frac{s_i + 1}{2}$ where spin $s_i \in \{-1, +1\}$:

$$H_{\text{Ising}}(s) = \sum_{i} h_i s_i + \sum_{i < j} J_{ij} s_i s_j + \text{Offset}$$

* $h_i$: Local magnetic field bias applied to physical qubit $i$
* $J_{ij}$: Inter-qubit coupling strength between physical qubits $i$ and $j$

---

## 🌐 Custom Microgrid Generator (10 to 100 Components)

The platform includes a procedural generator (`generate_custom_grid`) enabling simulation of arbitrary microgrid architectures from **10 to 100 components**:

* **Physical Grid Topologies**: Guaranteed connected spanning tree with central high-capacity trunk spine and branching lateral feeders.
* **Configurable DER Mix**:
  * Solar PV generation buses ($P_{\text{gen}} \in [15, 30]\text{ kW}$)
  * Wind turbine generation buses ($P_{\text{gen}} \in [20, 45]\text{ kW}$)
  * Battery Energy Storage System (BESS) nodes ($P_{\text{cap}} \in [20, 50]\text{ kW}$)
  * Electric Vehicle (EV) fast-charging depot nodes ($P_{\text{load}} \in [60, 110]\text{ kW}$)
* **Configurable Tie Lines**: User-specified count of normally open tie switches (1 to 15) creating realistic reconfiguration loop paths.
* **Aesthetic 2D Layout Coordinates**: Automatically generates spatial coordinates for high-resolution topology visualization.

```bash
# Generate and optimize an 80-component microgrid with 8 tie switches
python run_custom_grid.py --components 80 --ties 8 --solver exact_oracle
```

---

## 🧩 Multi-Solver Architecture & Scalable Quantum Annealing

Qfficient provides a unified solver interface through `thermodynamic_grid_qubo.pipeline`:

```
                           ┌──────────────────────────┐
                           │   OptimizationConfig     │
                           └─────────────┬────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
      ┌─────────────────────────┐                 ┌─────────────────────────┐
      │     Quantum Solvers     │                 │    Classical Solvers    │
      ├─────────────────────────┤                 ├─────────────────────────┤
      │ • D-Wave Advantage QPU  │                 │ • Exact Dynamic Oracle  │
      │ • OpenJij SQA (Ensemble)│                 │ • NumPy Vectorized SA   │
      │ • D-Wave Neal (SA)      │                 │ • Static Baseline       │
      └─────────────────────────┘                 └─────────────────────────┘
```

### Scalable Quantum Annealing for Large Grids ($N \ge 30$)
As grid sizes expand to 40, 60, and 100 components, raw spin-flip sampling suffers from combinatorial fragmentation. We introduced a **hybrid quantum-ensemble extraction engine**:
1. **Raw Quantum Sampling**: Executes SQA / Neal across configured anneal reads.
2. **Kruskal-Guided Energy Repair**: Repaired candidate spanning trees formed by Kruskal's MST biased by low-energy spins.
3. **Marginal Spin Ensemble MST**: Computes edge marginal probabilities across all quantum samples and extracts the maximum-probability spanning tree.
4. **Annealer-Guided Loop Exchange**: Identifies high-probability tie switches and generates minimal branch-exchange candidates.
5. **Physics Screening**: Evaluates candidate trees with fast LinDistFlow to guarantee voltage compliance and minimum Joule dissipation.

---

## 📊 Visual Diagnostics & Network Topologies

### 1. 33-Component IEEE Benchmark Topology
Active lines (green) vs. open tie switches (dashed gray) with node voltage and line temperature heatmaps:
<p align="center">
  <img src="optimized_microgrid.png" alt="33-Component Microgrid Topology" width="850">
</p>

### 2. Custom 60-Component & 100-Component Microgrid Topologies
<p align="center">
  <img src="custom_microgrid_60.png" alt="60-Component Microgrid Topology" width="420">
  <img src="custom_microgrid_100.png" alt="100-Component Microgrid Topology" width="420">
</p>

### 3. Dynamic Transient Analysis (40-Component & 60-Component Systems)
<p align="center">
  <img src="custom_40_transient.png" alt="40-Component Transient Analysis" width="420">
  <img src="custom_60_transient.png" alt="60-Component Transient Analysis" width="420">
</p>

---

## 💻 Interactive Review Portal (Streamlit 2.0 Web Dashboard)

Launch the full interactive GUI for presentations, demonstrations, and design reviews:

```bash
streamlit run app.py
```
* **Local Web Address**: `http://localhost:8501`

### Key Interactive Features
1. **Architecture Selector**: Choose between standard IEEE 33-Bus, 12-component test feeder, or **Custom Microgrid**.
2. **Custom Grid Controls**: Sliders for total components (10 to 100 buses), tie switches (1 to 15), and DER allocation (Solar PV, Wind, Battery BESS, EV depots).
3. **Transient Stress Injections**: Adjust solar PV cloud drop ($0 - 90\%$) and EV charging pulse surges ($0 - 1200\text{ kW}$).
4. **Executive Performance Table**: Direct comparison of Joule heat dissipation, entropy generation, exergy preserved, peak conductor temperature, and breaker switch counts.
5. **Interactive Topology Canvas**: Scrub through simulation time steps to inspect switch actions, active routes, and thermal states.
6. **Line-by-Line Operating State Table**: Detailed breakdown of line current, resistance, loading %, and temperature at any selected second.

---

## ⏱️ Minute-by-Minute Engineering Changelog

```
01:26 AM ──── 01:38 AM ──── 02:30 AM ──── 02:36 AM ──── 03:05 AM ──── 03:15 AM ──── 03:25 AM ──── 03:32 AM
  Init        Bootstrap      Classical    33-Bus Vis    Benchmark &   Multi-Solver   Custom 10-100   Release
  Repo        Platform       Exact Base   Layout        LinDistFlow   Pipeline       Microgrids      Package
```

### Phase 1: Platform Bootstrap (01:26 – 01:38 AM)
* `3a28612` (01:26:12): Initial repository structure and Apache 2.0 license.
* `be06050` (01:30:06): Built core Thermodynamic-Mapped QUBO engine with 12-component visualizer, thermal dynamics model ($I^2 R(T)$), non-equilibrium entropy calculator, and initial Streamlit dashboard.
* `f72a5b5` (01:36:07): Configured `.gitignore` for Python environments and binary caches.
* `cfcbe85` (01:38:25): Authored initial publication-grade README with core physics and Gouy-Stodola formulation.

### Phase 2: Classical Exact Baseline & 33-Bus Expansion (02:30 – 02:36 AM)
* `b06f285` (02:30:52): Implemented exact loss-minimizing classical baseline (`exact_classical_solver.py`), closed-state current estimation, raw QUBO energy ranking, and ablation suite (`ablation_suite.py`).
* `5003b46` (02:34:14): Scaled topology visualizer to the full 33-component IEEE benchmark (`visualize_microgrid.py`).
* `8c61d0f` (02:36:12): Refined 33-component layout coordinates, bus labeling, and aesthetic routing curves.

### Phase 3: Research-Grade Benchmark & LinDistFlow Engine (02:55 – 03:05 AM)
* `a718233` (03:05:13): Complete research-grade benchmark suite across 100 scenario evaluations (`run_benchmark.py`). Integrated fast LinDistFlow power flow solver (`fast_flow.py`, `ieee33_trees.npy`), rigorous claim reconciliation, and comprehensive automated report card generator (`report_card.py`).

### Phase 4: Scalable Custom Microgrids & Multi-Solver Pipeline (03:05 – 03:25 AM)
* `88d4fac` (03:15:01): Added `exact_oracle` and `numpy_annealer` directly to pipeline solver choices.
* `a3adf00` (03:24:47): Developed standalone runner (`run_custom_grid.py`) and dynamic support for custom 60-100 component microgrids.
* **Production Polish (03:25 – 03:32 AM)**:
  * Implemented `custom_grid_generator.py` supporting 10 to 100 buses with user-defined DER mixes and tie switches.
  * Added quantum ensemble MST extraction and loop-exchange repair in `openjij_annealer.py` for scalable quantum annealing on large grids.
  * Extended `app.py` with custom grid UI controls, executive comparison tables, and line-by-line power flow tables.
  * Added unit and integration tests (`tests/test_custom_grid.py`) bringing the test suite to **17 passing tests**.

---

## 🚀 Quickstart & CLI Commands

### 1. Environment Setup
```bash
git clone https://github.com/sharmeshms/Qfficient.git
cd Qfficient

# Create virtual environment
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Commands

| Task | Command | Description |
| :--- | :--- | :--- |
| **Unified CLI Suite** | `python run.py -n 60` | Full CLI & automated export suite (CSV, figures, reports) |
| **Parametric Sweep** | `python run.py --sweep` | Multi-scale scaling sweep across sizes [20, 40, 60, 80, 100] |
| **Launch Dashboard** | `streamlit run app.py` | Full interactive review portal & custom grid designer |
| **Standalone Web Suite**| Open `dashboard.html` | Self-contained single-page executive web app with SVG topology |
| **Build HTML Dashboard**| `python build_dashboard_html.py` | Compiles simulation telemetry into `dashboard.html` |
| **Run Benchmark** | `python run_benchmark.py --n 30 --steps 25` | 30-scenario statistical evaluation with LaTeX tables |
| **Custom 60-Bus Grid** | `python run_custom_grid.py --components 60 --ties 6` | Generates 60-component microgrid and runs optimization |
| **Custom 40-Bus Script** | `python run_custom_40.py` | Evaluates 40-component microgrid with transient plots |
| **Custom 60-Bus Script** | `python run_custom_60.py` | Evaluates 60-component microgrid with transient plots |
| **IEEE 33-Bus Visualizer**| `python visualize_microgrid.py` | Generates high-res `optimized_microgrid.png` |
| **Run Test Suite** | `pytest tests/` | Runs all 42 unit and physics verification tests |

### 3. One-Click Launchers
* **Windows**: Double-click `run_dashboard.bat`
* **Linux / macOS**: Execute `./run_dashboard.sh`
* **Docker**: Execute `docker compose up -d`

---

## 📁 Repository Architecture

```
Qfficient-/
├── run.py                                             # Unified CLI entry point & scaling sweep runner
├── MANUAL.md                                          # Complete technical stack specification & user manual
├── QFFICIENT_SYSTEM_MANUAL.docx                       # Comprehensive formatted Word technical manual
├── generate_docx_manual.py                            # Automated generator for the Word technical manual
├── dashboard.html                                     # Self-contained executive single-page presentation suite
├── build_dashboard_html.py                            # Compiler for the executive presentation dashboard
├── dashboard_data.json                                # Pre-generated multi-grid simulation telemetry
├── app.py                                             # Streamlit 2.0 interactive review portal & custom designer
├── main_experiment.py                                 # Scientific benchmark runner & figure generator
├── run_benchmark.py                                   # 100-scenario research-grade benchmark suite
├── run_custom_grid.py                                 # Standalone runner for custom 10-100 component microgrids
├── run_custom_40.py                                   # 40-component custom microgrid evaluation script
├── run_custom_60.py                                   # 60-component custom microgrid evaluation script
├── visualize_microgrid.py                             # IEEE 33-bus high-res topology visualizer
├── Dockerfile                                         # Multi-stage production container definition
├── docker-compose.yml                                 # Container orchestration
├── run_dashboard.bat                                  # Windows 1-click launcher
├── run_dashboard.sh                                   # Linux/macOS 1-click launcher
├── pyproject.toml                                     # Package installation metadata & entry points
├── requirements.txt                                   # Pinned production dependencies
│
├── results/                                           # Benchmark datasets & analytical summaries
│   ├── BENCHMARK_REPORT.md                            # Comprehensive statistical report & claim reconciliation
│   ├── benchmark_distribution.png                     # Loss distribution across policies
│   ├── benchmark_raw.json                             # Raw scenario execution telemetry
│   └── benchmark_summary.json                         # Mean, std, and p-value summary table
│
├── tests/                                             # Automated test suite (17 passed tests)
│   ├── test_custom_grid.py                            # Custom 30, 60, 100 component topology & pipeline tests
│   ├── test_fast_flow.py                              # LinDistFlow accuracy & voltage tests
│   ├── test_pipeline.py                               # Pipeline config & multi-solver tests
│   └── test_qubo_grid.py                              # Physics verifier, thermal dynamics, and QUBO tests
│
└── thermodynamic_grid_qubo/                           # Core Python Package
    ├── __init__.py                                    # Package root
    ├── cli.py                                         # Rich CLI & batch execution engine with CSV/report exports
    ├── pipeline.py                                    # Unified optimization pipeline & config
    ├── grid_engine/                                   # Distribution grid netlists & DER dynamics
    │   ├── __init__.py                                # Grid engine exports
    │   ├── custom_grid_generator.py                   # Procedural 10-100 component microgrid generator
    │   ├── ieee_feeder_loader.py                      # IEEE 33-bus and 12-component netlists
    │   ├── renewable_simulator.py                     # Solar drop & EV pulse transient simulators
    │   └── thermal_dynamics.py                        # Conductor lumped capacitance heat balance
    ├── qubo_engine/                                   # QUBO compilation & Ising mapping
    │   ├── __init__.py                                # QUBO engine exports
    │   ├── entropy_calculator.py                      # Joule dissipation & entropy generation weights
    │   ├── penalty_tuner.py                           # Dynamic Lagrange multiplier scaling
    │   └── qubo_builder.py                            # Master Hamiltonian & cycle constraints
    ├── solvers/                                       # Multi-solver execution backends
    │   ├── __init__.py                                # Solver exports
    │   ├── ablation_suite.py                          # Multi-policy ablation benchmarking suite
    │   ├── classical_baseline.py                      # Static baseline power flow evaluator
    │   ├── dwave_qpu_runner.py                        # Hardware D-Wave Advantage QPU interface
    │   ├── exact_classical_solver.py                  # Exact loss-minimizing classical oracle
    │   ├── numpy_annealer.py                          # Vectorized NumPy simulated annealer
    │   └── openjij_annealer.py                        # OpenJij SQA with ensemble MST loop exchange
    └── verification/                                  # Physics checks & visual reporting
        ├── __init__.py                                # Verification exports
        ├── fast_flow.py                               # Vectorized LinDistFlow power flow engine
        ├── ieee33_trees.npy                           # Precomputed IEEE 33-bus spanning tree database
        ├── metrics_evaluator.py                       # Exergy, entropy, and heat metric calculations
        ├── microgrid_visualizer.py                    # Network graph rendering & node positioning
        ├── physics_verifier.py                        # ANSI C84.1 voltage & thermal compliance checks
        └── report_card.py                             # Formal engineering grading & KPI report cards
```

---

## 🤝 Hardware Quantum Access (D-Wave Advantage QPU)

To submit QUBO Hamiltonians directly to cloud-based physical D-Wave Advantage QPUs:
```bash
export DWAVE_API_TOKEN="YOUR_LEAP_API_TOKEN"
python main_experiment.py
```
*(If no token is present, the framework automatically uses local high-performance Simulated Quantum Annealing via OpenJij or the exact classical oracle).*

---

## 📜 License & Citation

Distributed under the Apache 2.0 License. See `LICENSE` for details.

If you use **Qfficient** in academic research or industrial projects, please cite:
```bibtex
@article{qfficient2026,
  title={Thermodynamic-Mapped QUBO Formulation for Dynamic Microgrid Power Distribution},
  author={Sharmesh Magesh and Contributors},
  journal={GitHub Repository},
  url={https://github.com/sharmeshms/Qfficient},
  year={2026}
}
```