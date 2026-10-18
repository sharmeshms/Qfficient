# Scientific Method & Mathematical Specification

This document provides the formal mathematical and physical specification of **Qfficient: Thermodynamic-Mapped QUBO Microgrid Optimizer**, detailing the optimization formulation, power-flow mechanics, thermal dynamics, and solver architectures.

---

## 1. Problem Formulation: Dynamic Distribution Network Reconfiguration (DNR)

### 1.1 Microgrid Graph Representation
Let a distribution microgrid be represented by a connected graph $G = (V, E)$, where:
* $V = \{0, 1, \dots, |V|-1\}$ represents the set of electrical buses, with bus $0$ denoting the main substation / slack bus.
* $E = \{e_1, e_2, \dots, e_{|E|}\}$ represents the set of candidate branches (both normally-closed sectionalizing switches and normally-open tie lines).

A valid radial operating configuration is a spanning tree $T \subset E$ satisfying:
1. **Connectivity**: Every bus $i \in V$ has a path to the substation bus $0$.
2. **Acyclicity**: The subgraph $(V, T)$ contains no closed loops.
3. **Branch Cardinality**: $|T| = |V| - 1$. For the IEEE 33-Bus system, $|V| = 33$ and $|E| = 37$, requiring exactly $|T| = 32$ energized branches and $|E| - |T| = 5$ open tie switches.

### 1.2 AC Power Flow & Objective Function
For each branch $e = (i, j) \in T$, let $P_e$ and $Q_e$ be the real and reactive power flows, $r_e$ and $x_e$ be the branch resistance and reactance, and $I_e$ be the branch current magnitude.

The branch current is governed by:
$$I_e^2 = \frac{P_e^2 + Q_e^2}{V_i^2}$$

The total instantaneous three-phase active power loss is:
$$P_{\text{loss}}(T, t) = \sum_{e \in T} 3 \cdot I_e(t)^2 \cdot R_e(T_e(t))$$

Over a planning horizon $t \in [0, \tau]$, the cumulative Joule heat dissipated is:
$$Q_{\text{joule}} = \int_0^\tau P_{\text{loss}}(T, t) \, dt$$

The dynamic reconfiguration problem seeks to determine the sequence of spanning trees $T(t)$ that minimizes cumulative energy dissipation and breaker operation wear while maintaining voltage security:

$$\min_{\{T(t)\}} \sum_{t=1}^M \left[ P_{\text{loss}}(T(t), t) \cdot \Delta t + c_{\text{sw}} \cdot d(T(t), T(t-1)) \right]$$

subject to:
$$V_{\min} \le |V_i(t)| \le V_{\max} \quad \forall i \in V, \, \forall t$$
$$I_e(t) \le I_{\max,e} \quad \forall e \in T(t), \, \forall t$$
$$(V, T(t)) \text{ is a connected spanning tree} \quad \forall t$$

where $d(T(t), T(t-1)) = \frac{1}{2} |T(t) \triangle T(t-1)|$ is the number of switch toggles between consecutive time intervals.

---

## 2. Compilation into Thermodynamic QUBO & Ising Model

### 2.1 Decision Variables
For each branch $e \in E$, a binary decision variable $x_e \in \{0, 1\}$ represents the switch state:
* $x_e = 1$: Branch $e$ is closed (energized).
* $x_e = 0$: Branch $e$ is open (isolated tie switch).

### 2.2 Master Objective Hamiltonian
The combinatorial problem is compiled into an unconstrained binary quadratic Hamiltonian:
$$H(x) = \lambda_{\text{thermo}} H_{\text{thermo}}(x) + \lambda_{\text{cycle}} H_{\text{cycle}}(x) + \lambda_{\text{rad}} H_{\text{rad}}(x) + \lambda_{\text{cap}} H_{\text{cap}}(x) + \lambda_{\text{sw}} H_{\text{sw}}(x)$$

#### 1. Thermodynamic Dissipation ($H_{\text{thermo}}$)
Linearized proxy weighting maps branch dissipation to linear spin biases:
$$H_{\text{thermo}}(x) = \sum_{e \in E} w_e \cdot x_e \quad \text{where } w_e = \frac{3 \cdot \hat{I}_e^2 \cdot R_e(T_e)}{T_e}$$
Here, $\hat{I}_e$ is the estimated branch current under closed conditions, and $T_e$ is the conductor temperature in Kelvin.

**Quadratic Loss Extension** (`weight_mode="quadratic_loss"`):
Following Soler et al. (2012) and Mahdavi et al. (2021), branches sharing a common cycle $C_k$ incur quadratic cross-couplings:
$$Q_{ab} = \lambda_{\text{thermo}} \cdot \frac{w_a w_b}{w_{\max}} \cdot 0.5 \quad \forall (a, b) \in C_k, \, a \ne b$$
This penalizes simultaneous closure of branches in the same loop, discouraging circulating loop currents.

#### 2. Elementary Cycle Breaking ($H_{\text{cycle}}$)
In earlier formulations, cycle constraints were defined over 5 fundamental co-tree cycles:
$$H_{\text{basis\_cycle}}(x) = \sum_{k=1}^5 \left( \sum_{e \in C_k} x_e - (|C_k| - 1) \right)^2$$
**Rigorous Finding**: Our audit (`scripts/verify_qubo_constraints.py`) revealed that the 5 fundamental co-tree cycles admit 159,964 zero-penalty configurations out of $C(37, 32) = 435,897$, of which **68.27% are invalid non-tree subgraphs** (multiple cycles canceling each other or disconnecting nodes).

**Elementary Cycle Formulation**:
The IEEE 33-bus system contains exactly 26 elementary cycles. To guarantee that every elementary cycle contains at least one open switch, we introduce binary slack variables $y_{k,s} \in \{0, 1\}$:
$$\sum_{e \in C_k} x_e + \sum_{s=1}^{S_k} 2^{s-1} y_{k,s} = |C_k| - 1$$
This enforces $\sum_{e \in C_k} x_e \le |C_k| - 1$. The 26 elementary cycle constraints admit exactly **50,751 zero-penalty configurations, 100.00% of which are valid radial spanning trees**.

#### 3. Radial Spanning Tree Cardinality ($H_{\text{rad}}$)
Enforces exactly $|V| - 1$ active lines:
$$H_{\text{rad}}(x) = \left( \sum_{e \in E} x_e - (|V| - 1) \right)^2$$
Expanding this quadratic penalty produces an all-to-all coupling clique $K_{|E|}$:
$$H_{\text{rad}}(x) = \sum_{e \in E} (1 - 2(|V|-1)) x_e + 2 \sum_{e < e'} x_e x_{e'} + (|V|-1)^2$$

#### 4. Conductor Thermal Ampacity Protection ($H_{\text{cap}}$)
Penalizes overloading branches beyond rated current $I_{\max,e}$:
$$H_{\text{cap}}(x) = \sum_{e \in E} \left[ \max\left(0, \frac{\hat{I}_e - I_{\max,e}}{I_{\max,e}}\right) \right]^2 \cdot x_e$$

#### 5. Breaker Switching Fatigue ($H_{\text{sw}}$)
Penalizes toggling switch states between consecutive time steps $t-1$ and $t$:
$$H_{\text{sw}}(x) = \sum_{e \in E} |x_e^{(t)} - x_e^{(t-1)}| = \sum_{e \in E} \left[ x_e^{(t)} (1 - 2 x_e^{(t-1)}) + x_e^{(t-1)} \right]$$

---

## 3. Power-Flow Analysis & Solver Accuracy

### 3.1 Baran-Wu AC DistFlow (Branch Flow Model)
For a radial distribution network, the AC power flow equations formulated by Baran & Wu (1989) are:
$$P_j = P_i - r_{ij} I_{ij}^2 - P_{L,j} + P_{G,j}$$
$$Q_j = Q_i - x_{ij} I_{ij}^2 - Q_{L,j} + Q_{G,j}$$
$$V_j^2 = V_i^2 - 2(r_{ij} P_{ij} + x_{ij} Q_{ij}) + (r_{ij}^2 + x_{ij}^2) I_{ij}^2$$
$$I_{ij}^2 = \frac{P_{ij}^2 + Q_{ij}^2}{V_i^2}$$

In our engine (`verification/fast_flow.py` `FastFeeder.evaluate_ac()`), branch loss feedback is computed iteratively until voltage and flow convergence.

### 3.2 LinDistFlow Linear Approximation
Neglecting higher-order loss terms ($I_{ij}^2 \approx 0$) and assuming flat nominal voltage ($V_i \approx 1.0\text{ p.u.}$):
$$P_j \approx P_i - P_{L,j} + P_{G,j}$$
$$Q_j \approx Q_i - Q_{L,j} + Q_{G,j}$$
$$V_j \approx V_i - \frac{r_{ij} P_{ij} + x_{ij} Q_{ij}}{V_0}$$

### 3.3 Power-Flow Numerical Accuracy Comparison
We validated our vectorized AC DistFlow against an independent Backward/Forward Sweep reference solver (`verification/reference_ac_solver.py`) on the IEEE 33-Bus base case:
* **Reference Backward/Forward Sweep**: Active Loss = $210.9876\text{ kW}$, Min Voltage = $0.9038\text{ p.u.}$ (at bus 18).
* **Qfficient AC DistFlow (`evaluate_ac`)**: Active Loss = $210.9876\text{ kW}$, Min Voltage = $0.9038\text{ p.u.}$.
* **Numerical Discrepancy**: $< 0.0001\%$ active loss error ($< 0.001\text{ W}$).
* **LinDistFlow Approximator (`evaluate_tree`)**: Active Loss = $196.93\text{ kW}$ (underestimates losses by $6.66\%$), Min Voltage = $0.9071\text{ p.u.}$.

---

## 4. Conductor Thermal Dynamics & Non-Equilibrium Thermodynamics

### 4.1 Transient Lumped-Capacitance Heat Balance
For each line $e \in E$, conductor temperature evolves according to Newton's law of cooling with Ohmic heat generation:
$$C_{\text{th},e} \frac{dT_e(t)}{dt} = 3 \cdot I_e(t)^2 \cdot R_e(T_e(t)) - \frac{T_e(t) - T_{\text{amb}}}{\theta_{\text{th},e}}$$
where:
* $C_{\text{th},e}$ is the thermal heat capacity of the conductor ($\text{J}/\text{K}$).
* $\theta_{\text{th},e}$ is the thermal resistance to ambient air ($\text{K}/\text{W}$).
* Conductor thermal time constant $\tau_e = C_{\text{th},e} \cdot \theta_{\text{th},e} \approx 750\text{ s}$ ($12.5\text{ minutes}$).

### 4.2 Temperature-Dependent Electrical Resistance
Conductor electrical resistance scales linearly with temperature relative to standard reference temperature $T_{\text{ref}} = 298.15\text{ K}$ ($25^\circ\text{C}$):
$$R_e(T_e) = R_{0,e} \left[ 1 + \alpha (T_e - T_{\text{ref}}) \right]$$
where $\alpha = 0.00393\text{ K}^{-1}$ for aluminum/copper conductors.

### 4.3 Entropy vs. Heat Dissipation Collinearity
Non-equilibrium thermodynamic entropy generation rate is:
$$\dot{S}_{\text{gen},e}(t) = \frac{\dot{Q}_e(t)}{T_e(t)} = \frac{3 \cdot I_e(t)^2 \cdot R_e(T_e(t))}{T_e(t)} \quad \left[\frac{\text{W}}{\text{K}}\right]$$

Because line temperatures in distribution feeders vary by less than $3\%$ in absolute units ($298.15\text{ K}$ to $348.15\text{ K}$), the factor $1/T_e(t) \approx 1/T_0$ is virtually constant. Consequently, empirical analysis across 300 simulation runs demonstrates:
* Pearson correlation: $r = 1.000000$ ($p < 10^{-300}$)
* Spearman rank correlation: $\rho = 0.999981$
* Coefficient of determination: $R^2 = 1.000000$

Minimizing non-equilibrium thermodynamic entropy generation is physically and mathematically collinear with minimizing Ohmic Joule losses.

---

## 5. Solvers & Benchmark Policies

| Policy Identifier | Description | Algorithm & Mechanism |
| :--- | :--- | :--- |
| `standard_static` | IEEE 33 textbook baseline | Static tree with default tie lines $\{32, 33, 34, 35, 36\}$ (branches 33–37 open). |
| `static_loss_optimal` | Best static radial tree | Optimal single tree configuration (tie lines $\{6, 8, 13, 31, 36\}$) evaluated across all steps. |
| `exact_dynamic_oracle` | Exhaustive dynamic oracle | Evaluates all 50,751 valid trees in `ieee33_trees.npy` via vectorized LinDistFlow at every step. |
| `exact_oracle_hysteresis` | Oracle with wear damping | Reconfigures only when loss improvement exceeds $0.5\text{ kW}$, cutting breaker wear by 35%. |
| `baran_wu_branch_exchange` | Baran & Wu (1989) heuristic | Closes candidate tie lines, detects induced loops, and opens the branch with minimum current. |
| `tree_simulated_annealing` | Markov Chain tree SA | Direct tree swaps on cycle basis with Metropolis-Hastings acceptance on LinDistFlow losses. |
| `random_trees_raw` | Random tree baseline | Uniformly samples valid spanning trees from the 50,751 tree manifold without loss ranking. |
| `random_trees_filtered` | Random ensemble with filter | Samples 50 random spanning trees and selects the minimum LinDistFlow loss candidate. |
| `qubo_mesh_current_raw` | Pure QUBO ground state | Evaluates the lowest-energy spin sample without post-hoc power-flow filtering. |
| `qubo_mesh_current_marginal_mst` | Annealer spin marginals | Extracts Kruskal MST weighted by empirical spin probabilities $\Pr(x_e = 1)$ without power-flow selection. |
| `qubo_mesh_current_filtered` | Hybrid QUBO + filter | Screens annealer candidate trees and refines via annealer-guided loop branch exchange. |

---

## 6. Quantum Hardware Architecture & Minor Embedding

For hardware submission on D-Wave Advantage QPUs (Pegasus P16 topology):
* **Logical Variables**: 37 binary line variables $x_e$ plus slack variables $y_{k,s}$ (total $\le 45$ logical variables).
* **Graph Connectivity**: The radiality constraint $(\sum x_e - 32)^2$ introduces complete quadratic coupling, forming a $K_{37}$ clique (666 non-zero couplers).
* **Minor Embedding Expansion**: Because physical Pegasus qubits have degree 15, embedding $K_{37}$ requires chains of length 2 to 6, utilizing **150 to 320 physical qubits**.
* **Chain Strength**: Programmed at $J_{\text{chain}} \ge 2.0 \times \max|J_{ij}|$ to prevent chain breakage during transverse-field annealing.
* **Strict Attribution**: If hardware tokens are absent or calls fail, execution falls back to classical Neal SA and is strictly reported as `"local_fallback"`.
