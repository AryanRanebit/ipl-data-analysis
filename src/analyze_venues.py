"""Venue and season outcome summaries on the frozen IPL match snapshot.

Run python src/analyze_venues.py. Recorded wins by wickets are classified as
chasing wins and wins by runs as defending wins. This is descriptive, not an
estimate of a causal advantage from choosing to chase.
"""

from pathlib import Path

import pandas as pd

from analyze_teams_toss import validate_teams

ROOT = Path(__file__).resolve().parents[1]


def outcome_summary(matches: pd.DataFrame, group: str) -> pd.DataFrame:
    """Summarise each exact venue label or season, including undecided matches.

    Ties/no-results stay in match counts but leave the win-rate denominator.
    A group with no decided match has an undefined (blank CSV) chasing rate.
    D/L matches are retained and counted explicitly, not silently filtered.
    """
    if group not in {"venue", "season"}:
        raise ValueError("group must be venue or season")
    validate_teams(matches)
    for column in ["venue", "method"]:
        if column not in matches:
            raise ValueError(f"matches: missing column {column}")
    if matches["match_id"].isna().any() or not matches["match_id"].is_unique:
        raise ValueError("match IDs must be present and unique")
    if matches["venue"].isna().any() or matches["venue"].astype(str).str.strip().eq("").any():
        raise ValueError("venue must be present and not blank")
    for column in ["win_by_runs", "win_by_wickets"]:
        values = pd.to_numeric(matches[column], errors="raise")
        if not (values.isna() | (values.ge(0) & values.mod(1).eq(0))).all():
            raise ValueError("win margins must be nonnegative whole numbers")
    if not matches["method"].fillna("").isin(["", "D/L"]).all():
        raise ValueError("unexpected adjusted-result method")
    frame = matches.copy()
    frame["decided_matches"] = frame["result"].eq("normal").astype(int)
    frame["chasing_wins"] = frame["win_by_wickets"].gt(0).astype(int)
    frame["defending_wins"] = frame["win_by_runs"].gt(0).astype(int)
    frame["ties"] = frame["result"].eq("tie").astype(int)
    frame["no_results"] = frame["result"].eq("no result").astype(int)
    frame["dl_decided_matches"] = (frame["method"].eq("D/L") & frame["result"].eq("normal")).astype(int)
    columns = ["decided_matches", "chasing_wins", "defending_wins", "ties", "no_results", "dl_decided_matches"]
    table = frame.groupby(group, sort=True)[columns].sum()
    table.insert(0, "matches", frame.groupby(group).size())
    denominator = table["decided_matches"].replace(0, float("nan"))
    table["chasing_win_pct"] = (100 * table["chasing_wins"] / denominator).round(2)
    return table.reset_index()


def main() -> None:
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    for group, filename in [("venue", "venue_outcomes"), ("season", "season_chasing_outcomes")]:
        table = outcome_summary(matches, group)
        table.to_csv(output / f"{filename}.csv", index=False)
        print(f"{filename}: {len(table)} rows")


if __name__ == "__main__":
    main()
