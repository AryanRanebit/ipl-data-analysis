"""Chart gallery for the frozen snapshot. No downloads or data changes.

Run from any directory: python src/plot_analysis.py
Calculations reuse the audited analysis functions, not hand-entered figures.
"""
from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from analyze import batter_runs, matches_per_season, outcome_counts, validate_data
from analyze_bowling import bowler_wickets
from analyze_scoring import scoring_rate_by_season
from analyze_teams_toss import team_win_rates, toss_decision_by_season, toss_impact
from analyze_venues import outcome_summary

ROOT = Path(__file__).resolve().parents[1]
INK = "#18364b"
TEAL = "#087f8c"
BLUE = "#316cb0"


def chart_tables(matches, deliveries):
    """Use the same definitions and validation as the committed CSV tables."""
    validate_data(matches, deliveries)
    return {
        "matches_per_season": matches_per_season(matches),
        "top_10_batters": batter_runs(deliveries).head(10),
        "top_10_bowlers": bowler_wickets(deliveries).head(10),
        "season_chasing_outcomes": outcome_summary(matches, "season"),
        "team_win_rates": team_win_rates(matches),
        "toss_impact": toss_impact(matches),
        "venue_outcomes": outcome_summary(matches, "venue"),
        "match_outcomes": outcome_counts(matches),
        "toss_decision_by_season": toss_decision_by_season(matches),
        "scoring_rate_by_season": scoring_rate_by_season(deliveries),
    }


def top_venues_by_sample(table, n=10):
    """Largest decided-match samples first; alphabetical order breaks ties."""
    chosen = table.sort_values(
        ["decided_matches", "venue"], ascending=[False, True]
    ).head(n)
    # An undefined rate stays out of the ranking display, never a 0% bar.
    return chosen.dropna(subset=["chasing_win_pct"]).sort_values(
        ["chasing_win_pct", "venue"], ascending=[False, True]
    ).reset_index(drop=True)


def frame(title, subtitle, note):
    fig = Figure(figsize=(12, 7), dpi=150, facecolor="white")
    FigureCanvasAgg(fig)
    ax = fig.add_axes([0.19, 0.21, 0.76, 0.56])
    fig.text(0.06, 0.94, "IPL / SNAPSHOT EXPLORER", fontsize=10, color=TEAL, weight="bold")
    fig.text(0.06, 0.875, title, fontsize=23, color=INK, weight="bold")
    fig.text(0.06, 0.82, subtitle, fontsize=11, color=INK)
    fig.text(0.06, 0.09, note, fontsize=10, color=INK)
    fig.text(0.06, 0.045, "Source: Cricsheet (ODC-By) | Committed snapshot: 2008-2026, through 31 May 2026. Not live records.", fontsize=9, color="#586b78")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#b4c1c8")
    ax.tick_params(axis="both", length=0, labelcolor=INK, labelsize=10, pad=7)
    ax.set_axisbelow(True)
    return fig, ax


def ranking_chart(table, name, metric, title, subtitle, note):
    fig, ax = frame(title, subtitle, note)
    bars = ax.barh(table[name], table[metric], color=TEAL, height=0.65)
    ax.invert_yaxis()
    ax.set_xlim(0, max(table[metric]) * 1.18)
    ax.set_xlabel("Bat runs" if metric == "runs_batter" else "Credited wickets", color=INK)
    ax.xaxis.grid(True, color="#e6edf0")
    ax.bar_label(bars, labels=[f"{int(v):,}" for v in table[metric]], padding=6, color=INK, fontsize=10)
    return fig


def season_chart(table):
    fig, ax = frame(
        "Matches recorded by season", "Men's IPL | Counts include recorded ties and no-results.",
        "Counts describe this dataset's coverage, not a schedule-length adjustment.",
    )
    bars = ax.bar(table["season"].astype(str), table["matches"], color=BLUE, width=0.7)
    ax.set_ylim(0, max(table["matches"]) * 1.19)
    ax.set_ylabel("Recorded matches", color=INK)
    ax.set_xticks(range(len(table)), table["season"].astype(str), rotation=45, ha="right")
    ax.yaxis.grid(True, color="#e6edf0")
    ax.bar_label(bars, padding=4, fontsize=9, color=INK)
    return fig


def chasing_chart(table):
    fig, ax = frame(
        "Chasing win share by season", "Recorded wins by wickets / decided matches | D/L results retained.",
        "Ties and no-results excluded from the rate. Labels show decided-match counts (n).\nDescriptive association only: this does not estimate the effect of choosing to chase.",
    )
    # Compute from counts; undefined seasons stay as gaps rather than zeroes.
    denominator = table["decided_matches"].replace(0, float("nan"))
    rate = 100 * table["chasing_wins"] / denominator
    x = list(range(len(table)))
    ax.axhline(50, color="#9aa9b2", linestyle="--", linewidth=1)
    ax.plot(x, rate, color=TEAL, marker="o", linewidth=2)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Chasing wins / decided matches", color=INK)
    ax.set_xticks(x, table["season"].astype(str), rotation=45, ha="right")
    ax.yaxis.grid(True, color="#e6edf0")
    for position, value, n in zip(x, rate, table["decided_matches"]):
        if pd.notna(value):
            ax.annotate(f"n={int(n)}", (position, value), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=8, color=INK)
    return fig


def team_chart(table):
    fig, ax = frame(
        "Win share by recorded team label", "Men's IPL | Ties and no-results count as appearances, not wins.",
        "Snapshot totals across unequal team histories, not adjusted for era or squad strength.\nA rename across seasons is one label here. Equal rates ordered alphabetically.",
    )
    bars = ax.barh(table["team"], table["win_pct"], color=BLUE, height=0.65)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Wins / appearances (%)", color=INK)
    ax.xaxis.grid(True, color="#e6edf0")
    ax.bar_label(bars, labels=[f"{v}%  (n={int(n)})" for v, n in zip(table["win_pct"], table["matches"])], padding=6, color=INK, fontsize=10)
    return fig


def toss_chart(table):
    fig, ax = frame(
        "Toss winners' match win rate", "Men's IPL | Decided matches only, by what the toss winner chose.",
        "Ties and no-results excluded. Labels show decided-match counts (n).\nDescriptive association only: winning the toss does not pick the stronger team.",
    )
    labels = [f"{row.toss_decision}\n(n={int(row.decided_matches)})" for row in table.itertuples()]
    bars = ax.bar(labels, table["pct"], color=BLUE, width=0.5)
    ax.axhline(50, color="#9aa9b2", linestyle="--", linewidth=1)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Toss winner also won / decided matches", color=INK)
    ax.yaxis.grid(True, color="#e6edf0")
    ax.bar_label(bars, labels=[f"{v}%" for v in table["pct"]], padding=4, fontsize=10, color=INK)
    return fig


def venue_chart(table):
    fig, ax = frame(
        "Chasing win share at the most-used venues", "Men's IPL | Ten largest decided-match samples, exact recorded venue labels.",
        "Labels show chasing wins / decided matches and decided counts (n).\nDescriptive only: teams, eras and conditions differ; not a stadium ranking.",
    )
    ax.set_position([0.38, 0.21, 0.57, 0.56])
    bars = ax.barh(table["venue"], table["chasing_win_pct"], color=TEAL, height=0.65)
    ax.invert_yaxis()
    ax.axvline(50, color="#9aa9b2", linestyle="--", linewidth=1)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Chasing wins / decided matches (%)", color=INK)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.xaxis.grid(True, color="#e6edf0")
    ax.bar_label(bars, labels=[f"{v}%  (n={int(n)})" for v, n in zip(table["chasing_win_pct"], table["decided_matches"])], padding=6, color=INK, fontsize=9)
    return fig


def outcome_chart(table):
    fig, ax = frame(
        "How recorded matches finished", "Men's IPL | Share of every recorded match, including ties and no-results.",
        "Labels show the share of all recorded matches and match counts (n).",
    )
    labels = [f"{row.outcome}\n(n={int(row.matches)})" for row in table.itertuples()]
    bars = ax.bar(labels, table["percent_of_all_matches"], color=BLUE, width=0.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Share of all recorded matches", color=INK)
    ax.yaxis.grid(True, color="#e6edf0")
    ax.bar_label(bars, labels=[f"{v}%" for v in table["percent_of_all_matches"]], padding=4, fontsize=10, color=INK)
    return fig


def toss_decision_chart(table):
    fig, ax = frame(
        "Toss winners choosing to field first", "Men's IPL | Share of recorded tosses per season.",
        "Every recorded match has a toss decision, so ties and no-results count here.\nA descriptive strategy trend, not a claim about which choice is better.",
    )
    x = list(range(len(table)))
    ax.axhline(50, color="#9aa9b2", linestyle="--", linewidth=1)
    ax.plot(x, table["chose_field_pct"], color=TEAL, marker="o", linewidth=2)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Toss winner chose field / tosses", color=INK)
    ax.set_xticks(x, table["season"].astype(str), rotation=45, ha="right")
    ax.yaxis.grid(True, color="#e6edf0")
    for position, value, n in zip(x, table["chose_field_pct"], table["matches"]):
        ax.annotate(f"n={int(n)}", (position, value), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=8, color=INK)
    return fig


def scoring_chart(table):
    fig, ax = frame(
        "Scoring rate by season", "Men's IPL | Recorded runs per over, regular innings only.",
        "All recorded runs count, including extras; wides and no-balls are not legal balls.\nA league-wide descriptive rate, not a measure of any team or player.",
    )
    x = list(range(len(table)))
    ax.plot(x, table["runs_per_over"], color=TEAL, marker="o", linewidth=2)
    ax.set_ylim(0, max(table["runs_per_over"]) * 1.15)
    ax.set_ylabel("Runs per over", color=INK)
    ax.set_xticks(x, table["season"].astype(str), rotation=45, ha="right")
    ax.yaxis.grid(True, color="#e6edf0")
    for position, value in zip(x, table["runs_per_over"]):
        ax.annotate(f"{value}", (position, value), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=8, color=INK)
    return fig


def make_figures(tables):
    return {
        "matches_per_season": season_chart(tables["matches_per_season"]),
        "top_10_batters": ranking_chart(
            tables["top_10_batters"], "batter", "runs_batter", "Top ten batters by recorded runs",
            "Men's IPL | Regular innings only; extras and Super Overs excluded.",
            "Career totals in this snapshot, not scoring efficiency. Equal totals ordered alphabetically.",
        ),
        "top_10_bowlers": ranking_chart(
            tables["top_10_bowlers"], "bowler", "wickets", "Top ten bowlers by credited wickets",
            "Men's IPL | Regular innings only; run outs and non-bowler dismissals excluded.",
            "Career totals in this snapshot, not bowling efficiency. Equal totals ordered alphabetically.",
        ),
        "season_chasing_outcomes": chasing_chart(tables["season_chasing_outcomes"]),
        "team_win_rates": team_chart(tables["team_win_rates"]),
        "toss_impact": toss_chart(tables["toss_impact"]),
        "venue_chasing_top10": venue_chart(top_venues_by_sample(tables["venue_outcomes"])),
        "match_outcomes": outcome_chart(tables["match_outcomes"]),
        "toss_decision_by_season": toss_decision_chart(tables["toss_decision_by_season"]),
        "scoring_rate_by_season": scoring_chart(tables["scoring_rate_by_season"]),
    }


def main(output_dir=None):
    matches = pd.read_csv(ROOT / "data/processed/matches.csv")
    deliveries = pd.read_csv(ROOT / "data/processed/deliveries.csv")
    figures = make_figures(chart_tables(matches, deliveries))
    output = Path(output_dir) if output_dir is not None else ROOT / "figures"
    output.mkdir(parents=True, exist_ok=True)
    for name, fig in figures.items():
        path = output / f"{name}.png"
        fig.savefig(path, dpi=150, metadata={"Software": "IPL snapshot chart generator"})
        fig.clear()
        print(path)


if __name__ == "__main__":
    main()
