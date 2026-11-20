"""Verify chart data, displayed marks, undefined rates and PNG generation."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from plot_analysis import chart_tables, chasing_chart, main, make_figures


@pytest.fixture(scope="module")
def tables():
    return chart_tables(
        pd.read_csv(ROOT / "data/processed/matches.csv"),
        pd.read_csv(ROOT / "data/processed/deliveries.csv"),
    )


@pytest.mark.parametrize("name", [
    "matches_per_season", "top_10_batters", "top_10_bowlers", "season_chasing_outcomes",
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
    assert len(files) == 4
    first = {p.name: p.read_bytes() for p in files}
    assert all(data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) > 10_000 for data in first.values())
    main(tmp_path)
    assert first == {p.name: p.read_bytes() for p in files}
