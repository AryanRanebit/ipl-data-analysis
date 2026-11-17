# First analysis: season size, batting runs and match outcomes

These are descriptive results from the committed Cricsheet snapshot, not
claims about a live leaderboard or a complete official IPL record. The snapshot
contains 1,243 matches dated 18 April 2008 to 31 May 2026 and 295,732 delivery
rows. All 19 calendar-year seasons from 2008 through 2026 are represented.
The source and ODC-By attribution are in the main README.

## 1. How many matches are recorded per season?

See [the full season table](../results/matches_per_season.csv).

- The largest recorded season is 2013 with 76 matches.
- The smallest is 2009 with 57 matches.
- Each of 2022, 2023, 2025 and 2026 has 74 recorded matches; 2024 has 71.

Count one row in `matches.csv` as one match, including ties and no-results.
A smaller count does not by itself explain why matches are absent. Coverage,
cancellations and schedule changes need separate investigation before claiming
that these are the numbers of matches scheduled or played in the competition.

## 2. Which batters have the most runs in this snapshot?

See [the top-ten table](../results/top_10_batters.csv).

| Batter label in data | Runs |
| --- | ---: |
| V Kohli | 9,336 |
| RG Sharma | 7,329 |
| S Dhawan | 6,769 |
| DA Warner | 6,565 |
| KL Rahul | 5,815 |
| SK Raina | 5,528 |
| MS Dhoni | 5,439 |
| AM Rahane | 5,367 |
| SV Samson | 5,181 |
| AB de Villiers | 5,162 |

Sum `runs_batter`, not `total_runs`: extras are not the batter's runs. Use
innings 1 and 2 only, excluding 175 delivery rows in later Super Over innings.
The retained innings contain 381,235 batter runs across all batter labels.
Names are grouped exactly as stored; this increment does not resolve aliases.
Career totals reflect opportunity as well as performance, so this is not a
ranking of skill, strike rate or efficiency.

## 3. How are recorded match outcomes split?

See [the outcome table](../results/match_outcomes.csv).

| Recorded category | Matches | % of all 1,243 matches |
| --- | ---: | ---: |
| Win by runs | 558 | 44.89 |
| Win by wickets | 660 | 53.10 |
| Tie | 16 | 1.29 |
| No result | 9 | 0.72 |

Ordinary wins must have exactly one positive margin. Ties and no-results stay
separate, so the denominator does not silently drop them. A recorded tie can
have a later Super Over winner: this table preserves `result` and does not
reconstruct that winner. These categories are not a causal test of whether
chasing is better. Rain-adjusted games and playing conditions need their own
handling in a chasing-versus-defending analysis.

## Reproduce and check

```bash
python src/analyze.py
python -m pytest -q
```

The tests independently recount every season, every batter total and each
outcome with Python's `csv` and `Counter`, then compare the results with the
Pandas outputs and all committed CSV cells. Small examples check Super Over
exclusion, extras, tied totals, outcome denominators and invalid inputs.
This checks calculation correctness against the frozen CSVs, not upstream
source completeness or the accuracy of every raw scorecard.
