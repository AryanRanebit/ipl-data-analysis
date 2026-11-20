# IPL Data Analysis

Exploratory data analysis of Indian Premier League cricket: 19 seasons,
2008-2026, from 1,243 men's matches / 295,732 ball-by-ball deliveries
(snapshot current through 31 May 2026; men's IPL only, no duplicate
matches - verified from the dataset fields).

**Status: work in progress, built in stages.**

- Stage 1 (done): reproducible data pipeline - fetch raw Cricsheet data and
  build flat CSV tables (`matches.csv`, `deliveries.csv`) with integrity checks.
- Stage 2 (started): first analysis tables and tests - matches per season,
  top-ten batters by runs, and recorded outcome categories.
  [First analysis methods](docs/first-analysis.md). Bowler wicket rankings and
  season totals are also ready: [bowling methods and findings](docs/bowling-analysis.md).
  Team win rates and toss impact are ready too:
  [team and toss findings](docs/team-and-toss-analysis.md).
  Venue and season chasing/defending tables are ready:
  [venue and chasing findings](docs/venue-and-chasing-analysis.md).
- Stage 3 (started): [first chart gallery](docs/chart-gallery.md) with season
  match counts, top-ten batters/bowlers and chasing shares by season.
  Further charts, final findings and a measured resume bullet remain.

## Data source and license

- Raw data: [Cricsheet](https://cricsheet.org/), IPL JSON download
  (<https://cricsheet.org/downloads/ipl_json.zip>), ball-by-ball, updated regularly.
- Licensed under the [ODC Attribution License (ODC-By)](https://opendatacommons.org/licenses/by/1-0/)
  (a copy is in `data/ODC-BY-LICENSE.txt`). Attribution: contains information
  from Cricsheet, made available under the ODC Attribution License.
- Player name register: <https://cricsheet.org/register/people.csv>

## Reproduce

```bash
pip install -r requirements.txt
python src/fetch_data.py     # downloads raw data from cricsheet.org
python src/build_dataset.py  # JSON -> data/processed/{matches,deliveries}.csv
python src/analyze.py        # first three descriptive tables
python src/analyze_bowling.py # bowler wickets overall and by season
python src/analyze_teams_toss.py # team win rates and toss impact
python src/analyze_venues.py # exact venue labels and season chasing outcomes
python src/plot_analysis.py  # four headless PNG charts from the frozen snapshot
python -m pytest -q          # calculation and snapshot checks
```

To reproduce only the analysis, skip the download/build commands and run
`python src/analyze.py`, `python src/analyze_bowling.py` and
`python src/analyze_teams_toss.py` and `python src/analyze_venues.py` on the committed CSVs. Fetching and rebuilding may
change the snapshot, so review any data changes before replacing it.

The processed CSVs under `data/processed/` are the frozen snapshot this
project's results are computed from.

## Layout

- `src/fetch_data.py` - download raw data
- `src/build_dataset.py` - parse JSON into flat CSVs
- `src/analyze.py` - produce the first three descriptive tables
- `src/analyze_bowling.py` - credited wicket totals and innings bowled
- `src/analyze_teams_toss.py` - team win rates and toss-win splits
- `src/analyze_venues.py` - venue and season chasing/defending outcomes
- `src/plot_analysis.py` - reproducible headless chart gallery
- `tests/` - examples, input checks and independent CSV recounts

- `data/processed/` - frozen dataset snapshot
- `results/` - reproducible analysis tables
- `docs/first-analysis.md` - first findings, definitions and limitations
- `docs/bowling-analysis.md` - bowling findings, wicket-credit rules and limits
- `docs/team-and-toss-analysis.md` - team win rates, toss findings and limits
- `docs/venue-and-chasing-analysis.md` - venue labels, chasing outcomes and limits
- `docs/chart-gallery.md` - chart previews, definitions and reproduction steps
- `figures/` - four generated PNG charts, not live IPL records
