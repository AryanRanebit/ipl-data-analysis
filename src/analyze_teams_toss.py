"""Team win rates and toss impact for the committed IPL snapshot.

Run: python src/analyze_teams_toss.py
Only recorded matches are used; ties and no-results have no winner, so they
count toward appearances but not toward wins or the toss-win question. No
downloads are performed.
"""

from pathlib import Path

import pandas as pd

from analyze import validate_data

ROOT = Path(__file__).resolve().parents[1]
RESULTS = {"normal", "tie", "no result"}
TOSS_DECISIONS = {"bat", "field"}


def validate_teams(matches: pd.DataFrame) -> None:
    """Reject missing labels, unknown results and inconsistent match fields."""
    required = {
        "match_id", "season", "team1", "team2", "toss_winner",
        "toss_decision", "winner", "result", "win_by_runs", "win_by_wickets",
    }
    missing = required - set(matches.columns)
    if missing:
        raise ValueError(f"matches: missing team/toss columns {sorted(missing)}")
    if matches.empty:
        raise ValueError("matches: table is empty")
    for column in ["team1", "team2", "toss_winner", "toss_decision"]:
        if matches[column].isna().any():
            raise ValueError(f"{column} must be present")
        if matches[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"{column} must not be blank")
    if matches["team1"].eq(matches["team2"]).any():
        raise ValueError("team1 and team2 must differ")
    if not matches["result"].isin(RESULTS).all():
        raise ValueError(f"result must be one of {sorted(RESULTS)}")
    if not matches["toss_decision"].isin(TOSS_DECISIONS).all():
        raise ValueError(f"toss_decision must be one of {sorted(TOSS_DECISIONS)}")
    same_match = matches["toss_winner"].isin(
        set(matches["team1"]) | set(matches["team2"])
    )
    if not same_match.all():
        raise ValueError("toss_winner must be a recorded team label")
    row_teams = matches["toss_winner"].eq(matches["team1"]) | matches[
        "toss_winner"
    ].eq(matches["team2"])
    if not row_teams.all():
        raise ValueError("toss_winner must be one of the two teams in its match")
    decided = matches["winner"].notna()
    if not decided.eq(matches["result"].eq("normal")).all():
        raise ValueError("winner must be set exactly for normal results")
    if decided.any():
        in_row = matches.loc[decided, "winner"].eq(matches.loc[decided, "team1"]) | (
            matches.loc[decided, "winner"].eq(matches.loc[decided, "team2"])
        )
        if not in_row.all():
            raise ValueError("winner must be one of the two teams in its match")
    runs = matches["win_by_runs"].fillna(0).gt(0)
    wickets = matches["win_by_wickets"].fillna(0).gt(0)
    if not (runs ^ wickets).eq(decided).all():
        raise ValueError("win margins must be set exactly for decided matches")
    season = matches["season"]
    if not (season.ge(1) & season.mod(1).eq(0)).all():
        raise ValueError("season must contain positive whole numbers")


def team_win_rates(matches: pd.DataFrame) -> pd.DataFrame:
    """Count appearances and wins per recorded team label.

    Team labels are used exactly as the snapshot records them (current
    franchise names); a rename across seasons is one label here. Alphabetical
    order breaks equal rates; it is a display choice, not a claim that tied
    teams performed differently.
    """
    validate_teams(matches)
    appearances = pd.concat([matches["team1"], matches["team2"]]).value_counts()
    wins = matches["winner"].value_counts()
    table = appearances.rename_axis("team").reset_index(name="matches")
    table["wins"] = table["team"].map(wins).fillna(0).astype(int)
    table["win_pct"] = (table["wins"] / table["matches"] * 100).round(2)
    return table.sort_values(
        ["win_pct", "wins", "team"], ascending=[False, False, True]
    ).reset_index(drop=True)


def toss_impact(matches: pd.DataFrame) -> pd.DataFrame:
    """How often the toss winner also won, overall and by toss decision.

    Only decided matches (a recorded winner) can answer this question, so
    ties and no-results are excluded from every row, including "overall".
    """
    validate_teams(matches)
    decided = matches.loc[matches["winner"].notna()].copy()
    decided["toss_won_match"] = decided["winner"].eq(decided["toss_winner"])

    def summarise(frame: pd.DataFrame, label: str) -> dict:
        won = int(frame["toss_won_match"].sum())
        total = len(frame)
        return {
            "toss_decision": label,
            "decided_matches": total,
            "toss_winner_won_match": won,
            "pct": round(won / total * 100, 2) if total else 0.0,
        }

    rows = [
        summarise(decided.loc[decided["toss_decision"].eq(choice)], choice)
        for choice in ["bat", "field"]
    ]
    rows.append(summarise(decided, "overall"))
    return pd.DataFrame(rows)


def toss_decision_by_season(matches: pd.DataFrame) -> pd.DataFrame:
    """What toss winners chose per season, as recorded.

    Every recorded match has a toss decision, so ties and no-results count
    here too. The field-first share is a descriptive strategy trend, not a
    claim about which choice is better.
    """
    validate_teams(matches)
    table = matches.groupby("season")["toss_decision"].value_counts().unstack()
    table = table.reindex(columns=["bat", "field"], fill_value=0)
    table = table.rename(columns={"bat": "chose_bat", "field": "chose_field"})
    table = table.rename_axis(columns=None)
    table.insert(0, "matches", table["chose_bat"] + table["chose_field"])
    table["chose_field_pct"] = (table["chose_field"] / table["matches"] * 100).round(2)
    return table.reset_index()


def main() -> None:
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    validate_data(matches, deliveries)
    tables = {
        "team_win_rates": team_win_rates(matches),
        "toss_impact": toss_impact(matches),
        "toss_decision_by_season": toss_decision_by_season(matches),
    }
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
        print(f"\n{name}\n{table.to_string(index=False)}")


if __name__ == "__main__":
    main()
