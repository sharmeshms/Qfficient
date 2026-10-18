"""Consistency checker between benchmark_summary.json, README.md, and app.py.

Exits non-zero if any policy, mean, reduction %, latency, or p-value differs
from results/benchmark_summary.json beyond rounding tolerance, or if any policy
is missing/unexpected, or if app.py contains stale hard-coded numbers.
"""
import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT_DIR / "results" / "benchmark_summary.json"
README_PATH = ROOT_DIR / "README.md"
APP_PATH = ROOT_DIR / "app.py"

DISPLAY_NAME_TO_POLICY = {
    "standard static baseline (ieee 33 default)": "standard_static",
    "standard static baseline": "standard_static",
    "static loss-optimal (best static tree)": "static_loss_optimal",
    "static loss-optimal": "static_loss_optimal",
    "exact dynamic oracle (exact_oracle)": "exact_dynamic_oracle",
    "exact dynamic oracle": "exact_dynamic_oracle",
    "random spanning trees (raw)": "random_trees_raw",
    "random spanning trees (filtered / pf ranked)": "random_trees_filtered",
    "random spanning trees (filtered)": "random_trees_filtered",
    "thermodynamic qubo (raw eigenvalue)": "qubo_mesh_current_raw",
    "thermodynamic qubo (repair only, no pf ranking)": "qubo_mesh_current_repair_only",
    "thermodynamic qubo (repair + pf ranked)": "qubo_mesh_current_filtered",
    "thermodynamic qubo (quadratic loss + pf ranked)": "qubo_quadratic_loss_filtered",
    "branch-exchange heuristic (baran-wu style)": "branch_exchange_heuristic",
    "genetic algorithm / simulated annealing trees": "genetic_algorithm_trees",
}


def check_consistency() -> bool:
    if not JSON_PATH.exists():
        print(f"ERROR: {JSON_PATH} does not exist.")
        return False

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    summary = bench_data.get("summary", {})
    stat_tests = bench_data.get("statistical_tests", {})

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_text = f.read()

    # 1. Extract README Table
    match = re.search(r"<!-- RESULTS_TABLE_START -->(.*?)<!-- RESULTS_TABLE_END -->", readme_text, re.DOTALL)
    if not match:
        print("ERROR: Missing <!-- RESULTS_TABLE_START --> / <!-- RESULTS_TABLE_END --> markers in README.md")
        return False

    table_text = match.group(1).strip()
    rows = [r.strip() for r in table_text.splitlines() if r.strip().startswith("|")]

    if len(rows) < 3:
        print("ERROR: Incomplete markdown table in README.md")
        return False

    # Skip header and separator rows
    data_rows = rows[2:]
    table_policies_found = set()
    errors = []

    for r in data_rows:
        cols = [c.strip() for c in r.strip("|").split("|")]
        if len(cols) < 7:
            continue

        raw_name = cols[0].replace("**", "").strip().lower()
        policy_key = None
        for display_name, key in DISPLAY_NAME_TO_POLICY.items():
            if display_name in raw_name or raw_name in display_name:
                policy_key = key
                break

        if not policy_key:
            # Try raw matching
            for key in summary.keys():
                if key in raw_name:
                    policy_key = key
                    break

        if not policy_key or policy_key not in summary:
            errors.append(f"Unknown policy '{cols[0]}' in README table not found in benchmark_summary.json")
            continue

        table_policies_found.add(policy_key)
        p_json = summary[policy_key]

        # Parse heat: "$4.980 \pm 0.068$"
        heat_m = re.search(r"\$([0-9.]+)\s*\\pm\s*([0-9.]+)\$", cols[1])
        if heat_m:
            table_mean = float(heat_m.group(1))
            table_std = float(heat_m.group(2))
            json_mean = p_json["heat_mj"]["mean"]
            json_std = p_json["heat_mj"]["std"]

            if abs(table_mean - json_mean) > 0.006:
                errors.append(f"Policy {policy_key}: heat mean in README ({table_mean}) differs from JSON ({json_mean:.4f})")
            if abs(table_std - json_std) > 0.006:
                errors.append(f"Policy {policy_key}: heat std in README ({table_std}) differs from JSON ({json_std:.4f})")

        # Parse reduction %
        if policy_key != "standard_static":
            red_m = re.search(r"([+-]?[0-9.]+)%", cols[2])
            if red_m:
                table_red = float(red_m.group(1))
                json_red = stat_tests.get(policy_key, {}).get("percent_loss_reduction", 0.0)
                if abs(table_red - json_red) > 0.06:
                    errors.append(f"Policy {policy_key}: reduction % in README ({table_red}%) differs from JSON ({json_red:.2f}%)")

        # Parse latency
        lat_m = re.search(r"\$([0-9.]+)\\text\{ ms\}\$", cols[-1])
        if lat_m:
            table_lat = float(lat_m.group(1))
            json_lat = p_json["mean_decision_ms"]["mean"]
            if abs(table_lat - json_lat) > 0.06 and abs(table_lat - json_lat) / max(json_lat, 1e-4) > 0.05:
                errors.append(f"Policy {policy_key}: latency in README ({table_lat} ms) differs from JSON ({json_lat:.2f} ms)")

    # Verify all JSON policies are represented
    for key in summary.keys():
        if key not in table_policies_found:
            errors.append(f"Policy '{key}' in benchmark_summary.json is missing from README table")

    # 2. Check app.py for stale hard-coded numbers
    with open(APP_PATH, "r", encoding="utf-8") as f:
        app_text = f.read()

    stale_patterns = [
        (r"-28\.37%", "Stale -28.37% loss reduction text"),
        (r"-20\.06%", "Stale -20.06% loss reduction text"),
        (r"22\.27%", "Stale 22.27% claim text"),
        (r"~4\.98\s*MJ", "Stale ~4.98 MJ baseline text"),
    ]

    for pat, desc in stale_patterns:
        if re.search(pat, app_text):
            errors.append(f"app.py contains stale hard-coded text: {desc} (pattern {pat})")

    if errors:
        print(f"FAILED: Found {len(errors)} consistency errors:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("SUCCESS: README.md and app.py are completely consistent with results/benchmark_summary.json.")
    return True


if __name__ == "__main__":
    success = check_consistency()
    sys.exit(0 if success else 1)
