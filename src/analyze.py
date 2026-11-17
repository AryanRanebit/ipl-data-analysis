"""First descriptive tables for the frozen IPL snapshot.

Run from any directory: python src/analyze.py
No downloads or charts are needed for this increment.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def validate_data(matches: pd.DataFrame, deliveries: pd.DataFrame) -> None:
    """Fail early if the two tables cannot safely support these questions."""
    match_columns = {
        "match_id", "date", "season", "result", "win_by_runs", "win_by_wickets"
    }
    delivery_columns = {"match_id", "season", "innings", "batter", "runs_batter"}
    for label, table, required in [
        ("matches", matches, match_columns),
        ("deliveries", deliveries, delivery_columns),
    ]:
        missing = required - set(table.columns)
        if missing:
            raise ValueError(f"{label}: missing columns {sorted(missing)}")
        if table.empty:
            raise ValueError(f"{label}: table is empty")
    if matches["match_id"].isna().any() or not matches["match_id"].is_unique:
        raise ValueError("Match IDs must be present and unique")
    if not deliveries["match_id"].isin(matches["match_id"]).all():
        raise ValueError("Delivery refers to an unknown match")
    years = pd.to_datetime(matches["date"], errors="raise").dt.year
    if not years.eq(matches["season"]).all():
        raise ValueError("Match season must equal its calendar year")
    season_by_id = matches.set_index("match_id")["season"]
    if not deliveries["season"].eq(deliveries["match_id"].map(season_by_id)).all():
        raise ValueError("Delivery season does not match its match")
    if deliveries["batter"].isna().any():
        raise ValueError("Batter name is missing")
    for column in ["innings", "runs_batter"]:
        values = deliveries[column]
        minimum = 1 if column == "innings" else 0
        if not (values.ge(minimum) & values.mod(1).eq(0)).all():
            raise ValueError(f"{column} must contain valid whole numbers")


def matches_per_season(matches: pd.DataFrame) -> pd.DataFrame:
    """Count recorded matches, including ties and no-results."""
    return matches.groupby("season").size().reset_index(name="matches")


def batter_runs(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Sum bat runs, not team runs; innings after 2 are Super Overs."""
    regular = deliveries.loc[deliveries["innings"].le(2)]
    totals = regular.groupby("batter")["runs_batter"].sum().reset_index()
    # Alphabetical tie-break makes reruns stable even when run totals tie.
    return totals.sort_values(
        ["runs_batter", "batter"], ascending=[False, True]
    ).reset_index(drop=True)


def outcome_counts(matches: pd.DataFrame) -> pd.DataFrame:
    """Keep recorded ties/no-results separate from ordinary winning margins."""
    runs = matches["win_by_runs"].gt(0)
    wickets = matches["win_by_wickets"].gt(0)
    normal = matches["result"].eq("normal")
    valid_normal = normal & (runs ^ wickets)
    special = matches["result"].isin(["tie", "no result"]) & ~runs & ~wickets
    if not (valid_normal | special).all():
        raise ValueError("Unexpected result or inconsistent winning margins")
    categories = pd.Series("", index=matches.index, dtype="object")
    categories.loc[normal & runs] = "win by runs"
    categories.loc[normal & wickets] = "win by wickets"
    categories.loc[matches["result"].eq("tie")] = "tie"
    categories.loc[matches["result"].eq("no result")] = "no result"
    order = ["win by runs", "win by wickets", "tie", "no result"]
    counts = categories.value_counts().reindex(order, fill_value=0)
    result = counts.rename_axis("outcome").reset_index(name="matches")
    result["percent_of_all_matches"] = (result["matches"] / len(matches) * 100).round(2)
    return result


def main() -> None:
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    validate_data(matches, deliveries)
    tables = {
        "matches_per_season": matches_per_season(matches),
        "top_10_batters": batter_runs(deliveries).head(10),
        "match_outcomes": outcome_counts(matches),
    }
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
        print(f"\n{name}\n{table.to_string(index=False)}")


if __name__ == "__main__":
    main()
