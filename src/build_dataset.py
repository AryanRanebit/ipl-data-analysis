"""Parse Cricsheet IPL JSON files into flat CSV tables.

Outputs (written to data/processed/):
  matches.csv     one row per match (metadata, toss, outcome)
  deliveries.csv  one row per legal/illegal delivery (ball-by-ball)

The JSON format is documented at https://cricsheet.org/format/json/
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "ipl_json"
OUT_DIR = ROOT / "data" / "processed"

# Franchise renames over the years. We map renamed franchises to one
# canonical current name so "team by season" stats follow the franchise.
# Defunct teams (Deccan Chargers, Kochi Tuskers, Pune Warriors, Gujarat
# Lions, Rising Pune Supergiant(s)) keep their own names.
TEAM_CANONICAL = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
}

# Wicket kinds that are credited to the bowler.
BOWLER_WICKETS = {
    "bowled",
    "caught",
    "caught and bowled",
    "lbw",
    "stumped",
    "hit wicket",
    "hit the ball twice",
}

EXTRA_TYPES = ["wides", "noballs", "byes", "legbyes", "penalty"]


def _season_year(info: dict) -> int:
    """IPL season year taken from the match date, so the first season shows
    as 2008 (Cricsheet labels it '2007/08')."""
    return int(info["dates"][0][:4])


def parse_match(path: Path):
    with open(path) as f:
        data = json.load(f)
    info = data["info"]
    outcome = info.get("outcome", {})

    match_id = path.stem
    match_row = {
        "match_id": match_id,
        "date": info["dates"][0],
        "season": _season_year(info),
        "city": info.get("city"),
        "venue": info.get("venue"),
        "team1": TEAM_CANONICAL.get(info["teams"][0], info["teams"][0]),
        "team2": TEAM_CANONICAL.get(info["teams"][1], info["teams"][1]),
        "toss_winner": TEAM_CANONICAL.get(
            info.get("toss", {}).get("winner"), info.get("toss", {}).get("winner")
        ),
        "toss_decision": info.get("toss", {}).get("decision"),
        "winner": TEAM_CANONICAL.get(outcome.get("winner"), outcome.get("winner")),
        "win_by_runs": outcome.get("by", {}).get("runs"),
        "win_by_wickets": outcome.get("by", {}).get("wickets"),
        "result": outcome.get("result", "normal"),  # normal / tie / no result
        "method": outcome.get("method"),  # e.g. D/L
        "player_of_match": "; ".join(info.get("player_of_match", [])),
    }

    delivery_rows = []
    for innings_no, innings in enumerate(data.get("innings", []), start=1):
        batting = TEAM_CANONICAL.get(innings["team"], innings["team"])
        bowling = [t for t in (match_row["team1"], match_row["team2"]) if t != batting]
        bowling_team = bowling[0] if bowling else None
        for over in innings.get("overs", []):
            over_no = over["over"]  # 0-indexed
            for ball_idx, d in enumerate(over["deliveries"], start=1):
                extras = d.get("extras", {})
                extras_runs = sum(extras.values()) if extras else 0
                wickets = d.get("wickets", [])
                wicket = wickets[0] if wickets else None
                ball_label = d.get("actual_delivery", f"{over_no}.{ball_idx}")
                delivery_rows.append(
                    {
                        "match_id": match_id,
                        "season": match_row["season"],
                        "innings": innings_no,
                        "batting_team": batting,
                        "bowling_team": bowling_team,
                        "over": over_no + 1,  # 1-indexed for readability
                        "ball": ball_label,
                        "batter": d["batter"],
                        "bowler": d["bowler"],
                        "runs_batter": d["runs"]["batter"],
                        "extras_runs": extras_runs,
                        "extras_type": next(iter(extras), None),
                        "total_runs": d["runs"]["total"],
                        "is_wide": int("wides" in extras),
                        "is_noball": int("noballs" in extras),
                        "is_wicket": int(bool(wickets)),
                        "wicket_kind": wicket["kind"] if wicket else None,
                        "player_out": wicket["player_out"] if wicket else None,
                        "bowler_wicket": int(
                            bool(wicket) and wicket["kind"] in BOWLER_WICKETS
                        ),
                    }
                )
    return match_row, delivery_rows


def main() -> None:
    json_files = sorted(RAW_DIR.glob("*.json"))
    if not json_files:
        raise SystemExit(f"No JSON files found in {RAW_DIR}; run fetch_data.py first")

    match_rows, delivery_rows = [], []
    for path in json_files:
        m, ds = parse_match(path)
        match_rows.append(m)
        delivery_rows.extend(ds)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    matches = pd.DataFrame(match_rows).sort_values(["date", "match_id"])
    deliveries = pd.DataFrame(delivery_rows)

    matches.to_csv(OUT_DIR / "matches.csv", index=False)
    deliveries.to_csv(OUT_DIR / "deliveries.csv", index=False)

    print(f"matches.csv:    {len(matches):,} rows "
          f"({matches['season'].min()}-{matches['season'].max()})")
    print(f"deliveries.csv: {len(deliveries):,} rows")


if __name__ == "__main__":
    main()
