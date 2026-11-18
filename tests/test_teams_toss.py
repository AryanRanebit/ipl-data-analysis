"""Worked team/toss examples and an independent csv/Counter snapshot audit."""

import csv
from collections import Counter
from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analyze_teams_toss import team_win_rates, toss_impact, validate_teams


@pytest.fixture
def example():
    # Decided wins for A and B, one tie, one no-result; D/L still decides.
    return pd.DataFrame({
        "match_id": [1, 2, 3, 4, 5],
        "season": [2025, 2025, 2025, 2026, 2026],
        "team1": ["A", "B", "A", "A", "C"],
        "team2": ["B", "A", "C", "B", "A"],
        "toss_winner": ["A", "B", "C", "B", "C"],
        "toss_decision": ["bat", "field", "field", "bat", "field"],
        "winner": ["A", "B", None, "B", None],
        "win_by_runs": [10.0, None, None, None, None],
        "win_by_wickets": [None, 4.0, None, 5.0, None],
        "result": ["normal", "normal", "tie", "normal", "no result"],
    })


def test_appearances_count_ties_and_no_results_but_wins_do_not(example):
    assert team_win_rates(example).to_dict("list") == {
        "team": ["B", "A", "C"],
        "matches": [3, 5, 2],
        "wins": [2, 1, 0],
        "win_pct": [66.67, 20.0, 0.0],
    }


def test_toss_impact_uses_decided_matches_only(example):
    assert toss_impact(example).to_dict("list") == {
        "toss_decision": ["bat", "field", "overall"],
        "decided_matches": [2, 1, 3],
        "toss_winner_won_match": [2, 1, 3],
        "pct": [100.0, 100.0, 100.0],
    }


def test_tied_rate_and_wins_sort_alphabetically():
    # V leads on rate; X and Z tie on win rate AND wins, so the alphabetical
    # order breaks that tie (a display choice, not a performance claim).
    example = pd.DataFrame({
        "match_id": [1, 2, 3, 4, 5, 6],
        "season": [2025] * 6,
        "team1": ["Y", "Y", "Y", "X", "V", "V"],
        "team2": ["Z", "X", "Z", "W", "W", "W"],
        "toss_winner": ["Y", "Y", "Y", "X", "V", "V"],
        "toss_decision": ["bat", "field", "bat", "field", "bat", "field"],
        "winner": ["Y", "Y", "Z", "X", "V", "V"],
        "win_by_runs": [5.0, None, 8.0, None, 12.0, 4.0],
        "win_by_wickets": [None, 3.0, None, 6.0, None, None],
        "result": ["normal"] * 6,
    })
    table = team_win_rates(example)
    assert table["team"].tolist() == ["V", "Y", "X", "Z", "W"]
    assert table["win_pct"].tolist() == [100.0, 66.67, 50.0, 50.0, 0.0]


@pytest.mark.parametrize("problem", [
    "missing_column", "empty", "blank_team", "same_teams", "bad_result",
    "bad_decision", "toss_not_in_match", "winner_not_in_match",
    "winner_on_tie", "no_winner_on_normal", "margin_without_winner",
    "winner_without_margin", "both_margins", "fractional_season",
])
def test_invalid_team_toss_inputs(example, problem):
    if problem == "missing_column":
        example = example.drop(columns="toss_winner")
    elif problem == "empty":
        example = example.iloc[:0]
    elif problem == "blank_team":
        example.loc[0, "team1"] = " "
    elif problem == "same_teams":
        example.loc[0, "team2"] = "A"
    elif problem == "bad_result":
        example.loc[0, "result"] = "abandoned"
    elif problem == "bad_decision":
        example.loc[0, "toss_decision"] = "bowl"
    elif problem == "toss_not_in_match":
        example.loc[0, "toss_winner"] = "Z"
    elif problem == "winner_not_in_match":
        example.loc[0, "winner"] = "Z"
    elif problem == "winner_on_tie":
        example.loc[2, "winner"] = "A"
    elif problem == "no_winner_on_normal":
        example.loc[0, "winner"] = None
    elif problem == "margin_without_winner":
        example.loc[2, "win_by_runs"] = 5.0
    elif problem == "winner_without_margin":
        example.loc[0, "win_by_runs"] = None
    elif problem == "both_margins":
        example.loc[0, "win_by_wickets"] = 3.0
    else:
        example["season"] = example["season"].astype(float)
        example.loc[0, "season"] = 2025.5
    with pytest.raises(ValueError):
        validate_teams(example)


def test_snapshot_with_independent_recount():
    # Deliberately do not reuse production grouping logic.
    played, won = Counter(), Counter()
    toss_games, toss_wins = Counter(), Counter()
    with open(ROOT / "data/processed/matches.csv", newline="") as file:
        for row in csv.DictReader(file):
            played[row["team1"]] += 1
            played[row["team2"]] += 1
            if row["result"] != "normal":
                continue
            won[row["winner"]] += 1
            decision = row["toss_decision"]
            toss_games[decision] += 1
            toss_games["overall"] += 1
            if row["winner"] == row["toss_winner"]:
                toss_wins[decision] += 1
                toss_wins["overall"] += 1
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    rates = team_win_rates(matches)
    expected = [
        (team, played[team], won[team], round(won[team] / played[team] * 100, 2))
        for team in played
    ]
    expected.sort(key=lambda row: (-row[3], -row[2], row[0]))
    assert list(rates.itertuples(index=False, name=None)) == expected
    impact = toss_impact(matches)
    expected_impact = [
        (
            label, toss_games[label], toss_wins[label],
            round(toss_wins[label] / toss_games[label] * 100, 2),
        )
        for label in ["bat", "field", "overall"]
    ]
    assert list(impact.itertuples(index=False, name=None)) == expected_impact
    assert rates["wins"].sum() == sum(toss_games[k] for k in ["bat", "field"])
    for filename, expected_table in [
        ("team_win_rates", rates),
        ("toss_impact", impact),
    ]:
        committed = pd.read_csv(ROOT / f"results/{filename}.csv")
        pd.testing.assert_frame_equal(committed, expected_table)
