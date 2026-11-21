"""Scoring rate by season for the committed IPL snapshot.

Run: python src/analyze_scoring.py
Only regular innings (1 and 2) are included; Super Overs are excluded.
No downloads are performed.
"""

from pathlib import Path

import pandas as pd

from analyze import validate_data

ROOT = Path(__file__).resolve().parents[1]


def validate_scoring(deliveries: pd.DataFrame) -> None:
    """Reject missing columns, non-binary flags and invalid run values."""
    required = {"match_id", "season", "innings", "total_runs", "is_wide", "is_noball"}
    missing = required - set(deliveries.columns)
    if missing:
        raise ValueError(f"deliveries: missing scoring columns {sorted(missing)}")
    if deliveries.empty:
        raise ValueError("deliveries: table is empty")
    for column in ["match_id", "season", "innings", "total_runs"]:
        if deliveries[column].isna().any():
            raise ValueError(f"{column} must be present")
    for column in ["is_wide", "is_noball"]:
        if not deliveries[column].isin([0, 1]).all():
            raise ValueError(f"{column} must be a binary flag")
    runs = deliveries["total_runs"]
    if not (runs.ge(0) & runs.mod(1).eq(0)).all():
        raise ValueError("total_runs must contain nonnegative whole numbers")


def scoring_rate_by_season(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Recorded runs per over per season from the frozen snapshot.

    All recorded runs count toward scoring, including extras. Wides and
    no-balls are not legal deliveries, so they are excluded from the ball
    count, matching how an over progresses. This is a descriptive league
    scoring rate, not a measure of any team or player.
    """
    validate_scoring(deliveries)
    regular = deliveries.loc[deliveries["innings"].le(2)]
    legal = regular.loc[regular["is_wide"].eq(0) & regular["is_noball"].eq(0)]
    runs = regular.groupby("season")["total_runs"].sum().rename("runs")
    balls = legal.groupby("season").size().rename("legal_balls")
    table = pd.concat([runs, balls], axis=1).reset_index()
    table["runs_per_over"] = (table["runs"] / table["legal_balls"] * 6).round(2)
    return table.sort_values("season").reset_index(drop=True)


def main() -> None:
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    validate_data(matches, deliveries)
    table = scoring_rate_by_season(deliveries)
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    table.to_csv(output / "scoring_rate_by_season.csv", index=False)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
