"""Worked bowling examples and an independent csv/Counter snapshot audit."""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analyze_bowling import bowler_wickets, validate_bowling
from build_dataset import parse_match


@pytest.fixture
def example():
    # A: caught + stumped in separate innings; B: run out, then no wicket.
    # Super Over wickets are excluded even when credited to the bowler.
    return pd.DataFrame({
        "match_id": [1, 1, 1, 2, 2, 2, 3, 3],
        "season": [2025] * 6 + [2026] * 2,
        "innings": [1, 1, 2, 1, 3, 4, 1, 1],
        "bowler": ["A", "B", "A", "B", "B", "A", "C", "D"],
        "wicket_kind": ["caught", "run out", "stumped", None,
                        "bowled", "lbw", "hit wicket", "retired hurt"],
        "is_wicket": [1, 1, 1, 0, 1, 1, 1, 1],
        "bowler_wicket": [1, 0, 1, 0, 1, 1, 1, 0],
    })


def test_wickets_exclude_run_out_retirement_and_super_overs(example):
    assert bowler_wickets(example).to_dict("list") == {
        "bowler": ["A", "C", "B", "D"],
        "wickets": [2, 1, 0, 0],
        "innings_bowled": [2, 1, 2, 1],
    }
    assert bowler_wickets(example, by_season=True)["season"].tolist() == [
        2025, 2025, 2026, 2026
    ]


def test_repeated_deliveries_count_one_innings_and_sort_ties(example):
    repeated = pd.concat([example, example.iloc[[3]]], ignore_index=True)
    pd.testing.assert_frame_equal(bowler_wickets(repeated), bowler_wickets(example))
    repeated.loc[6, "bowler"] = "Z"
    repeated.loc[0, "bowler"] = "Y"
    table = bowler_wickets(repeated)
    assert table.loc[table["wickets"].eq(1), "bowler"].tolist() == ["A", "Y", "Z"]


@pytest.mark.parametrize("kind", ["bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket"])
def test_all_credited_dismissal_types(example, kind):
    example.loc[0, "wicket_kind"] = kind
    assert bowler_wickets(example).iloc[0]["wickets"] == 2


@pytest.mark.parametrize("kind", ["run out", "retired hurt", "retired out", "obstructing the field", "hit the ball twice", "handled the ball", "timed out"])
def test_non_bowler_dismissal_types(example, kind):
    example.loc[0, ["wicket_kind", "bowler_wicket"]] = [kind, 0]
    assert bowler_wickets(example)["wickets"].sum() == 2


@pytest.mark.parametrize("problem", ["missing_column", "empty", "missing_bowler", "blank_bowler", "unknown_kind", "bad_flag", "wrong_credit", "wrong_wicket_flag", "fractional_innings", "missing_season"])
def test_invalid_bowling_inputs(example, problem):
    if problem == "missing_column":
        example = example.drop(columns="bowler")
    elif problem == "empty":
        example = example.iloc[:0]
    elif problem == "missing_bowler":
        example.loc[0, "bowler"] = None
    elif problem == "blank_bowler":
        example.loc[0, "bowler"] = " "
    elif problem == "unknown_kind":
        example.loc[0, "wicket_kind"] = "mystery dismissal"
    elif problem == "bad_flag":
        example.loc[0, "bowler_wicket"] = 2
    elif problem == "wrong_credit":
        example.loc[1, "bowler_wicket"] = 1
    elif problem == "wrong_wicket_flag":
        example.loc[0, "is_wicket"] = 0
    elif problem == "fractional_innings":
        example["innings"] = example["innings"].astype(float)
        example.loc[0, "innings"] = 1.5
    else:
        example.loc[0, "season"] = None
    with pytest.raises(ValueError):
        validate_bowling(example)


def test_hit_ball_twice_is_not_credited_in_future_builds(tmp_path):
    import json
    match = {
        "info": {"dates": ["2026-01-01"], "teams": ["A", "B"]},
        "innings": [{"team": "A", "overs": [{"over": 0, "deliveries": [{
            "batter": "Batter", "bowler": "Bowler",
            "runs": {"batter": 0, "total": 0},
            "wickets": [{"kind": "hit the ball twice", "player_out": "Batter"}],
        }]}]}],
    }
    path = tmp_path / "1.json"
    path.write_text(json.dumps(match))
    _, deliveries = parse_match(path)
    assert deliveries[0]["is_wicket"] == 1
    assert deliveries[0]["bowler_wicket"] == 0


def test_snapshot_with_independent_wicket_kind_recount():
    # Deliberately do not import production credit categories or sum its flags.
    credited = {"bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket"}
    overall, seasonal = Counter(), Counter()
    innings, seasonal_innings = defaultdict(set), defaultdict(set)
    with open(ROOT / "data/processed/deliveries.csv", newline="") as file:
        for row in csv.DictReader(file):
            if int(row["innings"]) > 2:
                continue
            bowler = row["bowler"]
            key = (int(row["season"]), bowler)
            wicket = int(row["wicket_kind"] in credited)
            overall[bowler] += wicket
            seasonal[key] += wicket
            innings[bowler].add((row["match_id"], row["innings"]))
            seasonal_innings[key].add((row["match_id"], row["innings"]))
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    lifetime = bowler_wickets(deliveries)
    per_season = bowler_wickets(deliveries, by_season=True)
    expected = [
        (bowler, wickets, len(innings[bowler]))
        for bowler, wickets in sorted(overall.items(), key=lambda p: (-p[1], p[0]))
    ]
    assert list(lifetime.itertuples(index=False, name=None)) == expected
    expected_seasons = [
        (season, bowler, wickets, len(seasonal_innings[(season, bowler)]))
        for (season, bowler), wickets in sorted(
            seasonal.items(), key=lambda p: (p[0][0], -p[1], p[0][1])
        )
    ]
    assert list(per_season.itertuples(index=False, name=None)) == expected_seasons
    assert lifetime["wickets"].sum() == per_season["wickets"].sum() == sum(overall.values())
    for filename, expected_table in [
        ("top_10_bowlers", lifetime.head(10)),
        ("bowler_wickets_by_season", per_season),
    ]:
        committed = pd.read_csv(ROOT / f"results/{filename}.csv")
        pd.testing.assert_frame_equal(committed, expected_table)
