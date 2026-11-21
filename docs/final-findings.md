# Final findings: IPL snapshot analysis, 2008-2026

This is the closing summary of the staged analysis. Every number below comes
from the committed, frozen Cricsheet snapshot: 1,243 men's IPL matches and
295,732 ball-by-ball deliveries across 19 seasons (2008-2026), current
through 31 May 2026. These are snapshot totals, not live official records.
Contains information from [Cricsheet](https://cricsheet.org/), made available
under the [ODC Attribution License](https://opendatacommons.org/licenses/by/1-0/).

Reproduce everything:

```bash
pip install -r requirements.txt
python src/analyze.py
python src/analyze_bowling.py
python src/analyze_teams_toss.py
python src/analyze_venues.py
python src/analyze_scoring.py
python src/plot_analysis.py   # ten PNG charts under figures/
python -m pytest -q           # 101 checks
```

## Headline findings

**How matches finish.** Of 1,243 recorded matches, 660 (53.10%) were won by
the chasing side (win by wickets) and 558 (44.89%) by the defending side
(win by runs); 16 (1.29%) were ties and 9 (0.72%) no-results. Of the 1,218
decided matches, chases won 54.19%.

**The toss matters less than its reputation.** Toss winners also won the
match in 628 of 1,218 decided matches: 51.56%. The split by choice is wider:
toss winners who batted first won 45.34% (n=408), while those who fielded
first won 54.69% (n=810). This is a descriptive association; team strength,
venues and conditions are not controlled for.

**Captains moved to field first.** The share of toss winners choosing to
field rose from 55.17% in 2008 (dipping to 35.00% in 2010) to 83.33% in both
2018 and 2019, sitting at 82.43% in 2026. Every recorded match has a toss
decision, so ties and no-results count in these shares.

**Scoring inflated sharply in recent seasons.** League scoring rate stayed in
a 7.48-8.65 runs-per-over band from 2008 to 2021, then climbed every recent
season: 8.99 (2023), 9.56 (2024), 9.63 (2025) and 9.88 (2026), against 8.31
in 2008. All recorded runs count, including extras; wides and no-balls are
excluded from the ball count, and Super Overs are excluded.

**Teams.** Gujarat Titans hold the highest win share at 61.04% (n=77
appearances), ahead of Chennai Super Kings at 55.64% (n=266) and Mumbai
Indians at 53.26% (n=291). Team histories are unequal and labels are used
exactly as recorded (a rename across seasons is one label), so this ranks
snapshot records, not franchise quality.

**Players.** V Kohli leads recorded bat runs with 9,336, ahead of RG Sharma
(7,329) and S Dhawan (6,769). YS Chahal leads credited wickets with 233,
ahead of B Kumar (226) and SP Narine (207). Career totals only: not scoring
or bowling efficiency, and career lengths differ.

**Venues.** The exact label `Wankhede Stadium, Mumbai` has the largest
sample: 132 matches, 131 decided, with chasing wins at 54.96%. Among the ten
largest decided-match samples, `Sawai Mansingh Stadium, Jaipur` has the
highest chasing share at 64.71% (n=68). Venue labels are exact as recorded;
spellings and historical names are not combined.

## Limitations

- Descriptive, not causal: no chart proves that chasing, fielding first or a
  venue causes wins. Team strength, conditions and eras are uncontrolled.
- The snapshot ends 31 May 2026 and is not updated live; season 2026 is
  complete in this dataset's terms, not necessarily the official calendar.
- Sample sizes differ across teams, venues and seasons; every percentage in
  the gallery shows its denominator.
- D/L results are retained (23 decided matches) and counted explicitly.
- Ties remain ties even where a Super Over later settled the fixture.

## Measured resume bullet

> Built a reproducible Python/Pandas analysis of 19 IPL seasons (1,243
> matches, 295,732 ball-by-ball deliveries, Cricsheet): automated data
> pipeline, ten-chart Matplotlib gallery and findings report backed by 101
> pytest checks, quantifying league trends including scoring-rate inflation
> from 8.31 to 9.88 runs per over (2008-2026) and the shift to field-first
> toss decisions (55% to 82% of tosses).

Shorter variant:

> Analyzed 1,243 IPL matches (295,732 deliveries) with Python/Pandas and
> Matplotlib; built a tested, reproducible pipeline (101 pytest checks) and a
> ten-chart findings gallery covering outcomes, toss strategy and scoring
> trends across 19 seasons.
