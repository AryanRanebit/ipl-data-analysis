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
  [Methods and findings](docs/first-analysis.md). Bowler rankings, team win
  rates, toss impact, venue trends and chasing vs defending are still to come.
- Stage 3 (later): charts, findings write-up, resume bullet from measured results.

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
python src/analyze.py        # frozen CSVs -> results/*.csv
python -m pytest -q          # calculation and snapshot checks
```

To reproduce only the analysis, skip the download/build commands and run
`python src/analyze.py` on the committed CSVs. Fetching and rebuilding may
change the snapshot, so review any data changes before replacing it.

The processed CSVs under `data/processed/` are the frozen snapshot this
project's results are computed from.

## Layout

- `src/fetch_data.py` - download raw data
- `src/build_dataset.py` - parse JSON into flat CSVs
- `src/analyze.py` - produce the first three descriptive tables
- `tests/test_analysis.py` - examples, input checks and independent CSV recount

- `data/processed/` - frozen dataset snapshot
- `results/` - reproducible analysis tables
- `docs/first-analysis.md` - measured findings, definitions and limitations
- `figures/` - planned chart output (not added yet)
