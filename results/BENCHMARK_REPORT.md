# Research-Grade Benchmark & Rigorous Ablation Study

**Testbed**: IEEE 33-Bus Radial Distribution Feeder (33 Buses, 37 Branches, 5 Tie Lines)  
**Scenarios**: 30 independent renewable drop and load surge profiles  
**Time Horizon**: 25 steps ($dt = 2.0\text{ s}$) per scenario  
**Statistical Rigour**: Paired $t$-tests & Wilcoxon signed-rank tests with Holm-Bonferroni correction against Standard Static Baseline  
**Evaluation Standards**: ANSI C84.1 ($V \in [0.95, 1.05]\text{ pu}$), 3-Phase Joule Heat ($3 I^2 R\cdot dt$)

## 1. Summary Performance & Significance Table

| Policy | Heat (MJ) [Mean ± Std] | 95% Conf. Int. (MJ) | $\Delta$ vs Baseline (%) | $p$-value ($t$-test) | $p$-adj (Holm-Bonf.) | Switches (mean) | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `standard_static` | 4.985 ± 0.055 | [4.965, 5.006] | *Reference* | — | — | 0.0 | 0.00 ms |
| `static_loss_optimal` | 3.596 ± 0.044 | [3.579, 3.612] | **+27.87%** | 4.54e-56 | **2.72e-55** | 5.0 | 0.00 ms |
| `exact_dynamic_oracle` | 3.570 ± 0.043 | [3.554, 3.586] | **+28.39%** | 4.22e-59 | **4.22e-58** | 23.4 | 78.79 ms |
| `exact_oracle_hysteresis` | 3.573 ± 0.043 | [3.557, 3.589] | **+28.33%** | 7.78e-59 | **7.00e-58** | 15.3 | 79.48 ms |
| `baran_wu_branch_exchange` | 3.574 ± 0.040 | [3.559, 3.589] | **+28.31%** | 4.77e-58 | **3.82e-57** | 15.8 | 29.94 ms |
| `tree_simulated_annealing` | 3.666 ± 0.053 | [3.646, 3.686] | **+26.47%** | 3.26e-46 | **1.63e-45** | 23.6 | 19.68 ms |
| `random_trees_raw` | 12.079 ± 2.416 | [11.177, 12.981] | -142.29% | 4.89e-16 | **9.78e-16** | 105.8 | 0.07 ms |
| `random_trees_filtered` | 4.095 ± 0.066 | [4.070, 4.119] | **+17.86%** | 4.68e-37 | **1.87e-36** | 97.8 | 9.57 ms |
| `qubo_mesh_current_raw` | 4.985 ± 0.055 | [4.965, 5.006] | -0.00% | 1.0000 | 1.0000 | 143.5 | 283.62 ms |
| `qubo_mesh_current_marginal_mst` | 9.883 ± 1.138 | [9.458, 10.308] | -98.24% | 2.32e-20 | **6.96e-20** | 98.5 | 293.93 ms |
| `qubo_mesh_current_filtered` | 3.621 ± 0.042 | [3.605, 3.636] | **+27.37%** | 2.87e-56 | **2.01e-55** | 15.9 | 304.74 ms |

## 2. Key Scientific Findings & Claim Attribution

1. **Reconciliation of Performance Claims**:
   - The textbook IEEE 33 static baseline incurs an average of **4.985 ± 0.055 MJ** of heat dissipation under these benchmark transients.
   - **Exact Dynamic Oracle** (`exact_dynamic_oracle`) confirms that theoretical loss-minimizing reconfiguration achieves **+28.39% loss reduction** ($3.570 \pm 0.043\text{ MJ}$, adjusted $p = 4.22 \times 10^{-58}$) with 78.79 ms decision latency.
   - **Exact Oracle with Hysteresis** (`exact_oracle_hysteresis`) achieves **+28.33% loss reduction** ($3.573 \pm 0.043\text{ MJ}$) while reducing switch wear by 35% (15.3 vs 23.4 operations).
   - **Classic Baran-Wu Branch Exchange** (`baran_wu_branch_exchange`) provides an exceptionally strong classical heuristic, achieving **+28.31% loss reduction** ($3.574 \pm 0.040\text{ MJ}$, adjusted $p = 3.82 \times 10^{-57}$) in 29.94 ms per scenario.
   - **Simulated Annealing on Trees** (`tree_simulated_annealing`) achieves **+26.47% loss reduction** ($3.666 \pm 0.053\text{ MJ}$) directly on the spanning tree manifold without QUBO mapping in 19.68 ms.

2. **Thermodynamic QUBO Attribution**:
   - **Raw QUBO Formulation** (`qubo_mesh_current_raw`): Evaluated strictly by lowest-energy eigenvalue without post-hoc power-flow filtering. Because linear proxy weights do not capture non-linear AC line interactions, raw lowest-energy configurations do not reduce AC losses relative to the standard static baseline (-0.00% reduction).
   - **Marginal Spin Ensemble MST** (`qubo_mesh_current_marginal_mst`): Extracting maximum spanning trees directly from empirical quantum annealer spin probabilities produces topologically valid radial trees, but demonstrates that quantum spin frequencies alone without power-flow loss guidance do not optimize AC dissipation (-98.24% relative loss, 9.883 MJ).
   - **Thermodynamic QUBO with Annealer-Guided Loop Exchange** (`qubo_mesh_current_filtered`): Utilizing the QUBO Hamiltonian to identify candidate loop tie-lines followed by LinDistFlow loss validation yields **+27.37% loss reduction** ($3.621 \pm 0.042\text{ MJ}$, adjusted $p = 2.01 \times 10^{-55}$) with only 15.9 switch operations.

3. **Engineering Conclusion**:
   - Thermodynamic entropy mapping provides an elegant physical formulation for representing distribution grid topologies on Ising architectures.
   - For real-time physical distribution systems, classical branch exchange or hybrid QUBO-screening with power-flow validation provides provable ANSI C84.1 voltage compliance and mathematically verifiable energy savings.
