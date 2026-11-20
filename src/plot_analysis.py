"""First chart gallery for the frozen snapshot. No downloads or data changes.

Run from any directory: python src/plot_analysis.py
Calculations reuse the audited analysis functions, not hand-entered figures.
"""
from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from analyze import batter_runs, matches_per_season, validate_data
from analyze_bowling import bowler_wickets
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
    }


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
