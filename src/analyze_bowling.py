"""Bowler wicket counts for the committed IPL snapshot, not live records.

Run: python src/analyze_bowling.py
Only regular innings (1 and 2) are included. No downloads are performed.
"""

from pathlib import Path

import pandas as pd

from analyze import validate_data
from build_dataset import BOWLER_WICKETS

ROOT = Path(__file__).resolve().parents[1]
NON_BOWLER_DISMISSALS = {
    "run out", "retired hurt", "retired out", "obstructing the field",
    "hit the ball twice", "handled the ball", "timed out",
}


def validate_bowling(deliveries: pd.DataFrame) -> None:
    """Reject missing labels, unknown dismissal types and inconsistent flags."""
    required = {
        "match_id", "season", "innings", "bowler", "wicket_kind",
        "is_wicket", "bowler_wicket",
    }
    missing = required - set(deliveries.columns)
    if missing:
        raise ValueError(f"deliveries: missing bowling columns {sorted(missing)}")
    if deliveries.empty:
        raise ValueError("deliveries: table is empty")
    for column in ["bowler", "match_id", "season", "innings"]:
        if deliveries[column].isna().any():
            raise ValueError(f"{column} must be present")
    if deliveries["bowler"].astype(str).str.strip().eq("").any():
        raise ValueError("bowler must not be blank")
    for column in ["season", "innings"]:
        values = deliveries[column]
        if not (values.ge(1) & values.mod(1).eq(0)).all():
            raise ValueError(f"{column} must contain positive whole numbers")
    for column in ["is_wicket", "bowler_wicket"]:
        if not deliveries[column].isin([0, 1]).all():
            raise ValueError(f"{column} must be a binary flag")
    kinds = deliveries["wicket_kind"].fillna("")
    allowed = BOWLER_WICKETS | NON_BOWLER_DISMISSALS | {""}
    unknown = set(kinds) - allowed
    if unknown:
        raise ValueError(f"Unknown dismissal types: {sorted(unknown)}")
    if not deliveries["is_wicket"].eq(kinds.ne("").astype(int)).all():
        raise ValueError("is_wicket disagrees with wicket_kind")
    if not deliveries["bowler_wicket"].eq(kinds.isin(BOWLER_WICKETS).astype(int)).all():
        raise ValueError("bowler_wicket disagrees with dismissal credit rules")


def bowler_wickets(deliveries: pd.DataFrame, by_season: bool = False) -> pd.DataFrame:
    """Count credited wickets and innings with at least one recorded delivery.

    Zero-wicket bowlers are retained. Alphabetical order breaks equal totals;
    it is a display choice, not a claim that tied bowlers performed differently.
    """
    validate_bowling(deliveries)
    regular = deliveries.loc[deliveries["innings"].le(2)]
    keys = ["season", "bowler"] if by_season else ["bowler"]
    wickets = regular.groupby(keys)["bowler_wicket"].sum().rename("wickets")
    innings = (
        regular.drop_duplicates(["match_id", "innings", "bowler"])
        .groupby(keys).size().rename("innings_bowled")
    )
    table = pd.concat([wickets, innings], axis=1).reset_index()
    sort_keys = ["season", "wickets", "bowler"] if by_season else ["wickets", "bowler"]
    ascending = [True, False, True] if by_season else [False, True]
    return table.sort_values(sort_keys, ascending=ascending).reset_index(drop=True)


def main() -> None:
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    validate_data(matches, deliveries)
    tables = {
        "top_10_bowlers": bowler_wickets(deliveries).head(10),
        "bowler_wickets_by_season": bowler_wickets(deliveries, by_season=True),
    }
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
        print(f"{name}: {len(table)} rows")
    print(tables["top_10_bowlers"].to_string(index=False))


if __name__ == "__main__":
    main()
