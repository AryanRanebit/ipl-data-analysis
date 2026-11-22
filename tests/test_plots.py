"""Verify chart data, displayed marks, undefined rates and PNG generation."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from plot_analysis import (
    chart_tables,
    chasing_chart,
    main,
    make_figures,
    top_venues_by_sample,
)


@pytest.fixture(scope="module")
def tables():
    return chart_tables(
        pd.read_csv(ROOT / "data/processed/matches.csv"),
        pd.read_csv(ROOT / "data/processed/deliveries.csv"),
    )


@pytest.mark.parametrize("name", [
    "matches_per_season", "top_10_batters", "top_10_bowlers", "season_chasing_outcomes",
    "team_win_rates", "toss_impact", "venue_outcomes", "match_outcomes",
    "toss_decision_by_season", "scoring_rate_by_season",
])
def test_chart_tables_match_audited_csvs(tables, name):
    pd.testing.assert_frame_equal(tables[name], pd.read_csv(ROOT / f"results/{name}.csv"))


@pytest.mark.parametrize("name,metric", [
    ("top_10_batters", "runs_batter"), ("top_10_bowlers", "wickets"),
])
def test_ranking_bar_widths_labels_and_zero_axis(tables, name, metric):
    figures = make_figures(tables)
    ax = figures[name].axes[0]
    assert [p.get_width() for p in ax.patches] == tables[name][metric].tolist()
    assert [t.get_text() for t in ax.get_yticklabels()] == tables[name].iloc[:, 0].tolist()
    assert ax.get_xlim()[0] == 0
    assert ax.yaxis_inverted()
    assert [t.get_text() for t in ax.texts] == [f"{v:,}" for v in tables[name][metric]]
    for fig in figures.values():
        fig.clear()


def test_season_marks_include_every_season(tables):
    figures = make_figures(tables)
    ax = figures["matches_per_season"].axes[0]
    assert [p.get_height() for p in ax.patches] == tables["matches_per_season"]["matches"].tolist()
    assert len(ax.get_xticklabels()) == len(tables["matches_per_season"])
    assert ax.get_ylim()[0] == 0
    for fig in figures.values():
        fig.clear()


def test_team_chart_uses_rates_and_appearance_counts(tables):
    figures = make_figures(tables)
    ax = figures["team_win_rates"].axes[0]
    table = tables["team_win_rates"]
    assert [p.get_width() for p in ax.patches] == table["win_pct"].tolist()
    assert [t.get_text() for t in ax.get_yticklabels()] == table["team"].tolist()
    assert ax.get_xlim() == (0, 100)
    assert [t.get_text() for t in ax.texts] == [
        f"{v}%  (n={int(n)})" for v, n in zip(table["win_pct"], table["matches"])
    ]
    for fig in figures.values():
        fig.clear()


def test_toss_chart_marks_and_reference_line(tables):
    figures = make_figures(tables)
    ax = figures["toss_impact"].axes[0]
    table = tables["toss_impact"]
    assert [p.get_height() for p in ax.patches] == table["pct"].tolist()
    assert ax.get_ylim() == (0, 100)
    assert ax.lines[0].get_ydata()[0] == 50
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        f"{d}\n(n={n})" for d, n in zip(table["toss_decision"], table["decided_matches"])
    ]
    for fig in figures.values():
        fig.clear()


def test_venue_chart_selects_largest_decided_samples(tables):
    chosen = top_venues_by_sample(tables["venue_outcomes"])
    expected = tables["venue_outcomes"].sort_values(
        ["decided_matches", "venue"], ascending=[False, True]
    ).head(10)
    assert set(chosen["venue"]) == set(expected["venue"])
    assert chosen["chasing_win_pct"].notna().all()
    assert chosen["chasing_win_pct"].is_monotonic_decreasing
    figures = make_figures(tables)
    ax = figures["venue_chasing_top10"].axes[0]
    assert [p.get_width() for p in ax.patches] == chosen["chasing_win_pct"].tolist()
    assert ax.get_xlim() == (0, 100)
    for fig in figures.values():
        fig.clear()


def test_outcome_chart_marks_cover_every_recorded_match(tables):
    figures = make_figures(tables)
    ax = figures["match_outcomes"].axes[0]
    table = tables["match_outcomes"]
    assert [p.get_height() for p in ax.patches] == table["percent_of_all_matches"].tolist()
    assert table["percent_of_all_matches"].sum() == pytest.approx(100.0)
    assert ax.get_ylim() == (0, 100)
    for fig in figures.values():
        fig.clear()


def test_toss_decision_and_scoring_lines(tables):
    figures = make_figures(tables)
    ax = figures["toss_decision_by_season"].axes[0]
    table = tables["toss_decision_by_season"]
    np.testing.assert_allclose(ax.lines[1].get_ydata(), table["chose_field_pct"])
    assert ax.get_ylim() == (0, 100)
    ax = figures["scoring_rate_by_season"].axes[0]
    table = tables["scoring_rate_by_season"]
    np.testing.assert_allclose(ax.lines[0].get_ydata(), table["runs_per_over"])
    assert ax.get_ylim()[0] == 0
    for fig in figures.values():
        fig.clear()


def test_chasing_uses_decided_counts_and_preserves_zero_denominator():
    table = pd.DataFrame({
        "season": [2024, 2025, 2026], "decided_matches": [4, 0, 5],
        "chasing_wins": [3, 0, 2], "matches": [6, 2, 8],
    })
    fig = chasing_chart(table)
    ax = fig.axes[0]
    values = ax.lines[1].get_ydata()
    assert values[0] == 75
    assert np.isnan(values[1])
    assert values[2] == 40
    assert ax.get_ylim() == (0, 100)
    assert [t.get_text() for t in ax.texts] == ["n=4", "n=5"]
    fig.clear()


def test_chasing_snapshot_marks(tables):
    table = tables["season_chasing_outcomes"]
    fig = chasing_chart(table)
    np.testing.assert_allclose(fig.axes[0].lines[1].get_ydata(), 100 * table.chasing_wins / table.decided_matches)
    fig.clear()


def test_headless_generation_is_repeatable_and_nonempty(tmp_path):
    main(tmp_path)
    files = sorted(tmp_path.glob("*.png"))
    assert len(files) == 10
    first = {p.name: p.read_bytes() for p in files}
    assert all(data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) > 10_000 for data in first.values())
    main(tmp_path)
    assert first == {p.name: p.read_bytes() for p in files}
