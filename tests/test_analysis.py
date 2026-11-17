"""Small examples plus an independent audit of the committed snapshot."""

import csv
from collections import Counter
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyze import batter_runs, matches_per_season, outcome_counts, validate_data


@pytest.fixture
def snapshot():
    return (
        pd.read_csv(ROOT / "data/processed/matches.csv"),
        pd.read_csv(ROOT / "data/processed/deliveries.csv"),
    )


def test_batting_excludes_extras_and_super_overs():
    deliveries = pd.DataFrame({
        "innings": [1, 2, 3, 4, 5, 6],
        "batter": ["B", "A", "A", "B", "A", "B"],
        "runs_batter": [4, 4, 6, 6, 6, 6],
        "total_runs": [5, 6, 6, 6, 6, 6],
    })
    assert batter_runs(deliveries).to_dict("list") == {
        "batter": ["A", "B"], "runs_batter": [4, 4]
    }


def test_outcomes_preserve_ties_and_denominator():
    matches = pd.DataFrame({
        "result": ["normal", "normal", "tie", "no result"],
        "win_by_runs": [12, None, None, None],
        "win_by_wickets": [None, 5, None, None],
    })
    table = outcome_counts(matches)
    assert table["matches"].tolist() == [1, 1, 1, 1]
    assert table["percent_of_all_matches"].tolist() == [25.0] * 4
    matches.loc[0, "win_by_wickets"] = 3
    with pytest.raises(ValueError, match="inconsistent"):
        outcome_counts(matches)


@pytest.mark.parametrize(
    "problem", ["duplicate", "unknown", "season", "missing", "negative"]
)
def test_validation_rejects_bad_inputs(snapshot, problem):
    matches, deliveries = snapshot
    if problem == "duplicate":
        matches.loc[1, "match_id"] = matches.loc[0, "match_id"]
    elif problem == "unknown":
        deliveries.loc[0, "match_id"] = -1
    elif problem == "season":
        deliveries.loc[0, "season"] = 1900
    elif problem == "missing":
        matches = matches.drop(columns="season")
    else:
        deliveries.loc[0, "runs_batter"] = -1
    with pytest.raises(ValueError):
        validate_data(matches, deliveries)


def test_snapshot_against_independent_csv_counts(snapshot):
    """Use csv/Counter, not Pandas groupby, to check every output cell."""
    matches, deliveries = snapshot
    validate_data(matches, deliveries)
    seasons, runs, outcomes = Counter(), Counter(), Counter()
    with open(ROOT / "data/processed/matches.csv", newline="") as file:
        for row in csv.DictReader(file):
            seasons[int(row["season"])] += 1
            if row["result"] == "normal":
                category = "win by runs" if row["win_by_runs"] else "win by wickets"
            else:
                category = row["result"]
            outcomes[category] += 1
    with open(ROOT / "data/processed/deliveries.csv", newline="") as file:
        for row in csv.DictReader(file):
            if int(row["innings"]) <= 2:
                runs[row["batter"]] += int(row["runs_batter"])
    season_table = matches_per_season(matches)
    assert list(season_table.itertuples(index=False, name=None)) == sorted(seasons.items())
    batting_table = batter_runs(deliveries)
    assert list(batting_table.itertuples(index=False, name=None)) == sorted(
        runs.items(), key=lambda item: (-item[1], item[0])
    )
    outcome_table = outcome_counts(matches)
    for row in outcome_table.itertuples(index=False):
        assert row.matches == outcomes[row.outcome]
        expected_percent = round(outcomes[row.outcome] / sum(seasons.values()) * 100, 2)
        assert row.percent_of_all_matches == expected_percent
    assert season_table["matches"].sum() == outcome_table["matches"].sum() == len(matches)
    assert batting_table["runs_batter"].sum() == sum(runs.values())
    for filename, expected in [
        ("matches_per_season", season_table),
        ("top_10_batters", batting_table.head(10)),
        ("match_outcomes", outcome_table),
    ]:
        committed = pd.read_csv(ROOT / f"results/{filename}.csv")
        pd.testing.assert_frame_equal(committed, expected)
