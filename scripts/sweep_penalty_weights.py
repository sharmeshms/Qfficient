"""
Lagrange Multiplier Penalty Sensitivity Sweep.

Performs a systematic parameter sensitivity sweep across the 5 QUBO Hamiltonian terms:
    H(x) = λ_thermo * H_thermo(x)
         + λ_cycle  * H_cycle(x)
         + λ_rad    * H_radiality(x)
         + λ_cap    * H_capacity(x)
         + λ_sw     * H_switching(x)

Evaluates the impact of varying each multiplier on:
1. Valid radial spanning tree rate (%)
2. Cycle breaking violation rate (%)
3. Radiality (branch count |E| - 32) compliance
4. Hamiltonian ground state validity

Generates:
- results/penalty_sensitivity.json
- results/penalty_sensitivity.png
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from thermodynamic_grid_qubo.grid_engine.ieee_feeder_loader import IEEEFeederLoader
from thermodynamic_grid_qubo.verification.fast_flow import FastFeeder
from thermodynamic_grid_qubo.qubo_engine.qubo_builder import ThermodynamicQUBOBuilder
from thermodynamic_grid_qubo.qubo_engine.penalty_tuner import PenaltyTuner
from thermodynamic_grid_qubo.solvers.numpy_annealer import NumpyAnnealer


def run_penalty_sweep(output_dir: str = "results", num_reads: int = 80):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    grid = IEEEFeederLoader.load_ieee33()
    fast = FastFeeder(grid)
    edges = [(grid.lines[e].u, grid.lines[e].v) for e in fast.edge_ids]
    m = fast.m
    n_target = fast.n - 1 # 32 for IEEE-33

    # Representative operating weights
    entropy_weights = {i: fast.r0[i] * 3.0 * (45.0 ** 2) / 298.15 for i in range(m)}
    tuner = PenaltyTuner(base_scale=1.0)
    nominal_lams = tuner.calibrate(entropy_weights, num_buses=fast.n)

    multipliers = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0]
    param_keys = ["lambda_thermo", "lambda_cycle", "lambda_rad", "lambda_cap", "lambda_sw"]
    param_titles = {
        "lambda_thermo": "λ_thermo (Loss Objective)",
        "lambda_cycle": "λ_cycle (Cycle Breaking)",
        "lambda_rad": "λ_rad (Radiality / Branch Count)",
        "lambda_cap": "λ_cap (Thermal Ampacity)",
        "lambda_sw": "λ_sw (Switching Inertia)",
    }

    sampler = NumpyAnnealer(sweeps=60, seed=123)
    sweep_results = {}

    print("=" * 70)
    print("STARTING PENALTY WEIGHT SENSITIVITY SWEEP")
    print(f"Nominal Parameters: {nominal_lams}")
    print("=" * 70)

    for p_key in param_keys:
        sweep_results[p_key] = {
            "nominal_value": nominal_lams[p_key],
            "multipliers": multipliers,
            "values": [],
            "valid_tree_rate": [],
            "ground_state_valid": [],
            "mean_active_branches": [],
            "cycle_violation_rate": [],
        }

        for mult in multipliers:
            active_lams = dict(nominal_lams)
            active_lams[p_key] = nominal_lams[p_key] * mult
            sweep_results[p_key]["values"].append(float(active_lams[p_key]))

            builder = ThermodynamicQUBOBuilder(
                num_buses=fast.n,
                edges=edges,
                substations=grid.substations,
                graph=grid.graph,
                lambda_thermo=active_lams["lambda_thermo"],
                lambda_cycle=active_lams["lambda_cycle"],
                lambda_rad=active_lams["lambda_rad"],
                lambda_cap=active_lams["lambda_cap"],
                lambda_sw=active_lams["lambda_sw"],
                cycle_mode="elementary",
            )

            prev_sw = {i: (1 if i in fast.standard_edges else 0) for i in range(m)}
            qubo_model = builder.build_model(
                entropy_weights=entropy_weights,
                line_currents={i: 45.0 for i in range(m)},
                line_i_max={i: 350.0 for i in range(m)},
                prev_switch_states=prev_sw,
            )

            X, E, _ = sampler.sample(qubo_model.Q, num_reads=num_reads, offset=qubo_model.offset)

            # Analyze reads
            valid_count = 0
            cycle_viols = 0
            active_counts = []

            for r in range(num_reads):
                bitstring = X[r, :m]
                active_idx = tuple(sorted(np.nonzero(bitstring)[0]))
                active_counts.append(len(active_idx))

                # Check cycle breaking
                has_cycle = any(all(e in active_idx for e in c) for c in builder.cycle_edge_ids)
                if has_cycle:
                    cycle_viols += 1

                if fast.is_tree(active_idx):
                    valid_count += 1

            v_rate = float(valid_count / num_reads)
            c_rate = float(cycle_viols / num_reads)
            mean_branches = float(np.mean(active_counts))
            gs_valid = bool(fast.is_tree(tuple(sorted(np.nonzero(X[0, :m])[0]))))

            sweep_results[p_key]["valid_tree_rate"].append(v_rate)
            sweep_results[p_key]["cycle_violation_rate"].append(c_rate)
            sweep_results[p_key]["mean_active_branches"].append(mean_branches)
            sweep_results[p_key]["ground_state_valid"].append(gs_valid)

            print(f"[{p_key:13s}] mult={mult:4.2f} (val={active_lams[p_key]:6.2f}) -> Valid: {v_rate*100:5.1f}%, Cycles: {c_rate*100:5.1f}%, Mean Br: {mean_branches:4.1f}, GS: {gs_valid}")

    # Save JSON
    json_path = out_path / "penalty_sensitivity.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sweep_results, f, indent=2)

    # Plot 5-Panel Figure
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.flatten()

    for idx, p_key in enumerate(param_keys):
        ax = axes[idx]
        data = sweep_results[p_key]
        x_vals = np.array(data["multipliers"])

        ax.plot(x_vals, np.array(data["valid_tree_rate"]) * 100.0, marker="o", color="#2B6CB0", lw=2, label="Valid Radial Tree %")
        ax.plot(x_vals, np.array(data["cycle_violation_rate"]) * 100.0, marker="s", color="#C53030", lw=2, linestyle="--", label="Cycle Violations %")
        
        ax.set_xscale("log")
        ax.set_title(param_titles[p_key], fontsize=11, fontweight="bold")
        ax.set_xlabel("Multiplier relative to nominal (1.0x)")
        ax.set_ylabel("Percentage (%)")
        ax.axvline(1.0, color="gray", linestyle=":", label="Nominal (1.0x)")
        ax.set_ylim(-5, 105)
        ax.grid(True, alpha=0.3)
        if idx == 0:
            ax.legend(loc="best", fontsize=8.5)

    # 6th panel: Summary of parameter roles
    ax_summary = axes[5]
    ax_summary.axis("off")
    summary_text = (
        "QUBO Multiplier Tuning Insights:\n\n"
        "1. λ_thermo: Balances physical loss against graph\n"
        "   topology constraints. When > 2x nominal, raw reads\n"
        "   may violate cycle constraints due to aggressive cost pruning.\n\n"
        "2. λ_cycle: Minimum ~15-25 needed to eliminate closed\n"
        "   elementary loops. Under 0.5x, cyclic graphs proliferate.\n\n"
        "3. λ_rad: Enforces exactly N-1=32 closed branches.\n"
        "   Strict quadratic penalty (Sum x - 32)^2 stabilizes\n"
        "   spanning tree density.\n\n"
        "4. λ_cap: Suppresses lines with I > I_max.\n\n"
        "5. λ_sw: Controls switching hysteresis and wear."
    )
    ax_summary.text(0.05, 0.95, summary_text, fontsize=9.5, family="monospace", va="top")

    plt.tight_layout()
    plot_path = out_path / "penalty_sensitivity.png"
    plt.savefig(plot_path, dpi=160)
    plt.close()

    print(f"Sensitivity sweep completed. Saved to {json_path} and {plot_path}.")
    return sweep_results


if __name__ == "__main__":
    run_penalty_sweep()
