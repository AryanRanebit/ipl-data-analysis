# IPL Data Analysis

Exploratory data analysis of Indian Premier League cricket: 19 seasons,
2008-2026, from 1,243 men's matches / 295,732 ball-by-ball deliveries
(snapshot current through 31 May 2026; men's IPL only, no duplicate
matches - verified from the dataset fields).

**Status: work in progress, built in stages.**

- Stage 1 (done): reproducible data pipeline - fetch raw Cricsheet data and
  build flat CSV tables (`matches.csv`, `deliveries.csv`) with integrity checks.
- Stage 2 (next, not started in this package): core analysis tables -
  top batsmen/bowlers, team win rates, toss impact, venue trends,
  chasing vs defending.
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
```

The processed CSVs under `data/processed/` are the frozen snapshot this
project's results are computed from.

## Layout

- `src/fetch_data.py` - download raw data
- `src/build_dataset.py` - parse JSON into flat CSVs

- `data/processed/` - frozen dataset snapshot
- `results/`, `figures/`, `docs/` - stage 2/3 outputs
