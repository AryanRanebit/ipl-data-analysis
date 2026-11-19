"""Small examples, invalid-input checks and independent csv snapshot audits."""

import csv
from collections import defaultdict
from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analyze_venues import outcome_summary


@pytest.fixture
def example():
    return pd.DataFrame({
        "match_id": [1, 2, 3, 4, 5], "season": [2025, 2025, 2025, 2026, 2026],
        "venue": ["V", "V", "V", "W", "W"],
        "team1": ["A"] * 5, "team2": ["B"] * 5,
        "toss_winner": ["A"] * 5, "toss_decision": ["bat"] * 5,
        "winner": ["A", "B", "B", None, None],
        "result": ["normal", "normal", "normal", "tie", "no result"],
        "win_by_runs": [10, None, None, None, None],
        "win_by_wickets": [None, 4, 2, None, None],
        "method": [None, None, "D/L", None, None],
    })


@pytest.mark.parametrize("group", ["venue", "season"])
def test_worked_example_and_undefined_rate(example, group):
    table = outcome_summary(example, group)
    assert table["matches"].tolist() == [3, 2]
    assert table["decided_matches"].tolist() == [3, 0]
    assert table["chasing_wins"].tolist() == [2, 0]
    assert table["defending_wins"].tolist() == [1, 0]
    assert table["ties"].tolist() == [0, 1]
    assert table["no_results"].tolist() == [0, 1]
    assert table["dl_decided_matches"].tolist() == [1, 0]
    assert table.loc[0, "chasing_win_pct"] == 66.67
    assert pd.isna(table.loc[1, "chasing_win_pct"])


def test_exact_venue_labels_are_not_silently_combined(example):
    example.loc[1, "venue"] = "V, City"
    assert outcome_summary(example, "venue")["venue"].tolist() == ["V", "V, City", "W"]


@pytest.mark.parametrize("problem", [
    "missing_venue", "missing_method", "null_venue", "blank_venue", "duplicate_id",
    "null_id", "negative_margin", "fractional_margin", "unknown_method",
    "winner_on_tie", "both_margins", "empty", "unknown_group",
])
def test_reject_bad_inputs(example, problem):
    group = "venue"
    if problem.startswith("missing_"):
        example = example.drop(columns=problem.removeprefix("missing_"))
    elif problem == "null_venue":
        example.loc[0, "venue"] = None
    elif problem == "blank_venue":
        example.loc[0, "venue"] = " "
    elif problem == "duplicate_id":
        example.loc[1, "match_id"] = 1
    elif problem == "null_id":
        example.loc[0, "match_id"] = None
    elif problem == "negative_margin":
        example.loc[0, "win_by_wickets"] = -1
    elif problem == "fractional_margin":
        example.loc[0, "win_by_runs"] = 1.5
    elif problem == "unknown_method":
        example.loc[0, "method"] = "unknown"
    elif problem == "winner_on_tie":
        example.loc[3, "winner"] = "A"
    elif problem == "both_margins":
        example.loc[0, "win_by_wickets"] = 2
    elif problem == "empty":
        example = example.iloc[:0]
    else:
        group = "city"
    with pytest.raises(ValueError):
        outcome_summary(example, group)


@pytest.mark.parametrize("group,filename", [
    ("venue", "venue_outcomes"), ("season", "season_chasing_outcomes"),
])
def test_independent_snapshot_recount_and_committed_csv(group, filename):
    # Plain csv iteration, deliberately no production aggregation helpers.
    counts = defaultdict(lambda: [0] * 7)
    with open(ROOT / "data/processed/matches.csv", newline="") as file:
        for row in csv.DictReader(file):
            key = row[group] if group == "venue" else int(row[group])
            c = counts[key]
            c[0] += 1
            if row["result"] == "normal":
                c[1] += 1
                if float(row["win_by_wickets"] or 0) > 0:
                    c[2] += 1
                elif float(row["win_by_runs"] or 0) > 0:
                    c[3] += 1
                if row["method"] == "D/L":
                    c[6] += 1
            elif row["result"] == "tie":
                c[4] += 1
            else:
                assert row["result"] == "no result"
                c[5] += 1
    expected = []
    for key, c in sorted(counts.items()):
        rate = round(c[2] / c[1] * 100, 2) if c[1] else float("nan")
        expected.append([key, *c, rate])
    actual = outcome_summary(pd.read_csv(ROOT / "data/processed/matches.csv"), group)
    pd.testing.assert_frame_equal(actual, pd.DataFrame(expected, columns=actual.columns))
    pd.testing.assert_frame_equal(actual, pd.read_csv(ROOT / f"results/{filename}.csv"))
    assert actual["matches"].sum() == 1243
    assert actual["decided_matches"].sum() == 1218
    assert actual["chasing_wins"].sum() == 660
    assert actual["defending_wins"].sum() == 558
    assert (actual["chasing_wins"] + actual["defending_wins"]).equals(actual["decided_matches"])
    assert (actual["decided_matches"] + actual["ties"] + actual["no_results"]).equals(actual["matches"])
