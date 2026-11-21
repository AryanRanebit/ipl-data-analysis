"""Worked scoring-rate examples and an independent csv snapshot audit."""

import csv
from collections import Counter
from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analyze_scoring import scoring_rate_by_season, validate_scoring


@pytest.fixture
def example():
    return pd.DataFrame({
        "match_id": [1, 1, 1, 1, 1, 1, 2, 2],
        "season": [2025, 2025, 2025, 2025, 2025, 2025, 2026, 2026],
        "innings": [1, 1, 1, 1, 2, 3, 1, 1],
        "total_runs": [4, 1, 6, 2, 5, 7, 0, 12],
        "is_wide": [0, 1, 0, 0, 0, 0, 0, 0],
        "is_noball": [0, 0, 0, 1, 0, 0, 0, 0],
    })


def test_extras_count_but_illegal_balls_do_not(example):
    # 2025 regular innings: 4+1+6+2+5 = 18 runs; the wide and the no-ball
    # are not legal balls, so 3 legal balls -> 18 / 3 * 6 = 36.0. The Super
    # Over (innings 3) is excluded entirely.
    assert scoring_rate_by_season(example).to_dict("list") == {
        "season": [2025, 2026],
        "runs": [18, 12],
        "legal_balls": [3, 2],
        "runs_per_over": [36.0, 36.0],
    }


@pytest.mark.parametrize("problem", [
    "missing_column", "empty", "missing_value", "bad_flag", "negative_runs",
    "fractional_runs",
])
def test_invalid_scoring_inputs(example, problem):
    if problem == "missing_column":
        example = example.drop(columns="is_wide")
    elif problem == "empty":
        example = example.iloc[:0]
    elif problem == "missing_value":
        example.loc[0, "total_runs"] = None
    elif problem == "bad_flag":
        example.loc[0, "is_noball"] = 2
    elif problem == "negative_runs":
        example.loc[0, "total_runs"] = -1
    else:
        example["total_runs"] = example["total_runs"].astype(float)
        example.loc[0, "total_runs"] = 1.5
    with pytest.raises(ValueError):
        validate_scoring(example)


def test_snapshot_with_independent_recount():
    # Deliberately do not reuse production grouping logic.
    runs, legal = Counter(), Counter()
    with open(ROOT / "data/processed/deliveries.csv", newline="") as file:
        for row in csv.DictReader(file):
            if int(row["innings"]) > 2:
                continue
            season = int(row["season"])
            runs[season] += int(row["total_runs"])
            if row["is_wide"] == "0" and row["is_noball"] == "0":
                legal[season] += 1
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    table = scoring_rate_by_season(deliveries)
    expected = [
        (season, runs[season], legal[season], round(runs[season] / legal[season] * 6, 2))
        for season in sorted(runs)
    ]
    assert list(table.itertuples(index=False, name=None)) == expected
    committed = pd.read_csv(ROOT / "results/scoring_rate_by_season.csv")
    pd.testing.assert_frame_equal(committed, table)
