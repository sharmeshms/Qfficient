import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.check_readme_consistency import check_consistency


def test_readme_and_app_consistent_with_benchmark_summary():
    """Verify that all policy metrics in README and app.py match benchmark_summary.json exactly."""
    assert check_consistency() is True
