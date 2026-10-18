"""Generate and insert benchmark results markdown table into README.md from benchmark_summary.json.

Never type results by hand. All table entries are generated directly from results/benchmark_summary.json.
Markers:
<!-- RESULTS_TABLE_START -->
<!-- RESULTS_TABLE_END -->
"""
import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
README_PATH = ROOT_DIR / "README.md"
JSON_PATH = ROOT_DIR / "results" / "benchmark_summary.json"

POLICY_DISPLAY_NAMES = {
    "standard_static": "Standard Static Baseline (IEEE 33 default)",
    "static_loss_optimal": "Static Loss-Optimal (Best static tree)",
    "exact_dynamic_oracle": "Exact Dynamic Oracle (exact_oracle)",
    "random_trees_raw": "Random Spanning Trees (Raw)",
    "random_trees_filtered": "Random Spanning Trees (Filtered / PF ranked)",
    "qubo_mesh_current_raw": "Thermodynamic QUBO (Raw eigenvalue)",
    "qubo_mesh_current_repair_only": "Thermodynamic QUBO (Repair only, no PF ranking)",
    "qubo_mesh_current_filtered": "Thermodynamic QUBO (Repair + PF ranked)",
    "qubo_quadratic_loss_filtered": "Thermodynamic QUBO (Quadratic loss + PF ranked)",
    "branch_exchange_heuristic": "Branch-Exchange Heuristic (Baran-Wu style)",
    "genetic_algorithm_trees": "Genetic Algorithm / Simulated Annealing Trees",
}


def format_p_value(p: float) -> str:
    if p is None or p < 0:
        return "—"
    if p < 0.001:
        return f"{p:.2e}"
    return f"{p:.4f}"


def build_markdown_table(data: dict) -> str:
    summary = data.get("summary", {})
    stat_tests = data.get("statistical_tests", {})
    meta = data.get("metadata", {})

    lines = [
        "| Policy / Algorithm | Total Joule Heat (MJ) [Mean ± Std] | Heat Reduction vs Std. Baseline (%) | $p$-value ($t$-test) | Peak Conductor Temp (°C) | Voltage Violations (steps) | Switch Operations | Decision Latency (ms) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for policy, metrics in summary.items():
        name = POLICY_DISPLAY_NAMES.get(policy, policy.replace("_", " ").title())
        h = metrics.get("heat_mj", {})
        h_str = f"${h.get('mean', 0.0):.3f} \\pm {h.get('std', 0.0):.3f}$"

        if policy == "standard_static":
            red_str = "*Reference*"
            p_str = "—"
        else:
            test = stat_tests.get(policy, {})
            red = test.get("percent_loss_reduction", 0.0)
            red_str = f"**{red:+.2f}%**" if red > 0 else f"{red:+.2f}%"
            p_str = format_p_value(test.get("p_value_paired_t", 1.0))

        temp = metrics.get("peak_temp_c", {}).get("mean", 0.0)
        viol = metrics.get("voltage_violation_steps", {}).get("mean", 0.0)
        sw = metrics.get("switch_operations", {}).get("mean", 0.0)
        lat = metrics.get("mean_decision_ms", {}).get("mean", 0.0)

        lines.append(
            f"| **{name}** | {h_str} | {red_str} | {p_str} | ${temp:.1f}^\\circ\\text{{C}}$ | ${viol:.1f}$ | ${sw:.1f}$ | ${lat:.2f}\\text{{ ms}}$ |"
        )

    scenarios = meta.get("scenarios", "N/A")
    steps = meta.get("steps", "N/A")
    dt = meta.get("dt_seconds", 2.0)
    seeds = meta.get("seeds", "1000..")
    cmd = meta.get("command", "python run_benchmark.py")
    correction = meta.get("correction_method", "Paired t-test / Wilcoxon signed-rank")

    footer = (
        f"\n*Benchmark parameters: {scenarios} scenarios, {steps} time steps ($dt = {dt}\\text{{ s}}$), "
        f"seeds: {seeds}, correction: {correction}. Generated from `{cmd}`.*"
    )

    return "\n".join(lines) + footer


def update_readme():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Missing benchmark summary: {JSON_PATH}")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    table_md = build_markdown_table(data)
    block = f"<!-- RESULTS_TABLE_START -->\n{table_md}\n<!-- RESULTS_TABLE_END -->"

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- RESULTS_TABLE_START -->.*?<!-- RESULTS_TABLE_END -->"
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, lambda m: block, content, flags=re.DOTALL)
    else:
        # Replace the manual table under section 1. IEEE 33-Bus Benchmark
        table_find = r"(\| Policy / Algorithm.*?Decision Latency \(ms\).*?\n)((\|.*?\n)+)"
        if re.search(table_find, content):
            new_content = re.sub(table_find, lambda m: block + "\n", content)
        else:
            # Append if not found
            new_content = content + "\n\n" + block

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully updated README.md with generated results table from {JSON_PATH}")


if __name__ == "__main__":
    update_readme()
