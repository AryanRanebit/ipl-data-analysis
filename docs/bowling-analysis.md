# Bowling analysis: credited wickets, not every dismissal

This increment uses the same committed Cricsheet CSV snapshot as the first
analysis: 1,243 recorded matches across 2008-2026. Nothing was downloaded or
refreshed. These are snapshot calculations, not a live official leaderboard.

## Questions answered

1. Which bowler labels have the most credited wickets in regular innings?
2. How do wicket totals break down by season?

See [top ten bowlers](../results/top_10_bowlers.csv) and
[all season/bowler totals](../results/bowler_wickets_by_season.csv).

| Bowler label in data | Credited wickets | Innings bowled |
| --- | ---: | ---: |
| YS Chahal | 233 | 184 |
| B Kumar | 226 | 206 |
| SP Narine | 207 | 200 |
| PP Chawla | 192 | 191 |
| JJ Bumrah | 187 | 158 |
| R Ashwin | 187 | 217 |
| DJ Bravo | 183 | 158 |
| RA Jadeja | 180 | 237 |
| Rashid Khan | 179 | 153 |
| A Mishra | 174 | 162 |

There are 13,460 credited wickets across all regular innings,
with 577 distinct bowler labels and 2,201
season/bowler rows (including zero-wicket bowlers). For example, the recorded
2013 and 2021 season leaders are DJ Bravo and HV Patel respectively, each with
32 wickets. This does not make them equally effective or equally skilled.

## Definitions

- **Bowler wicket:** bowled, caught, caught and bowled, lbw, stumped or hit
  wicket. Run outs, retirements, obstructing the field, hit the ball twice,
  handled the ball and timed out are not credited to the bowler.
- **Regular innings:** innings 1 and 2 only. Exclude the same 175 later-innings
  delivery rows that the batting analysis excludes as Super Overs.
- **Innings bowled:** a distinct match/innings pair where that bowler label has
  at least one recorded delivery. It is not matches played, squad appearances,
  completed overs or a minimum-qualification filter. It includes innings in
  no-result matches if deliveries are recorded.
- **Season:** the calendar year already stored by the data pipeline.
- **Ties:** sort equal wicket totals alphabetically for stable output. No
  performance tie-break is implied. The top-ten display is limited to ten
  labels; the season table retains all labels and equal totals.

Do not sum `is_wicket` as the bowler's wickets: the regular innings contain
14,674 rows flagged with a dismissal/retirement, but only 13,460 credited
bowler wickets. The excluded rows are 1,185 run outs, 19 retired hurt, six
retired out and four obstructing the field. In particular, the field name
`is_wicket` also flags retired hurt; it is not a clean team wickets-lost count.

## One small pipeline correction

The initial builder wrongly included `hit the ball twice` among dismissals
credited to the bowler. This increment removes it and adds a synthetic JSON
regression test. No such dismissal occurs in the frozen CSVs, so this fix does
not change the committed data or any earlier result.

Sources checked for the definitions:

- [Queensland Cricket Scorers Association: wickets ready reckoner](https://www.cricketscorersqld.org/_files/ugd/832597_7d122475b4a74bb492751a0308d7ee92.pdf)
  identifies the credited and non-credited methods, including hit ball twice
  as non-credited.
- [Cricsheet JSON format](https://cricsheet.org/format/json/)
  documents the wicket-kind labels and the array of wicket entries.

## Checks and limits

`python src/analyze_bowling.py` validates dismissal labels and both flags before
writing its two CSVs. Unknown labels and inconsistent credit flags fail rather
than silently contributing a wicket. The existing match/delivery relationship
checks run too.

Tests use small examples for credit rules, Super Overs, repeated deliveries,
zero-wicket bowlers, sorting and invalid input. An independent Python
`csv`/`Counter` audit derives credits directly from dismissal labels, not the
stored credit flags, and compares every overall total, season total, innings
count and committed output cell with the Pandas calculation. All earlier
analysis tests are retained.

Names are used exactly as stored, without player-ID alias resolution. The
flattened CSV stores only the first wicket entry on a delivery; this increment
does not recover other entries from raw scorecards. Calculation checks cannot
prove upstream completeness or scorecard accuracy. Career wicket totals depend
on opportunity and are not bowling averages, economy rates or a causal measure
of bowling quality. No Purple Cap award claims are made from this table.

## Reproduce

```bash
python src/analyze.py
python src/analyze_bowling.py
python -m pytest -q
```

Data attribution: contains information from Cricsheet, made available under the
ODC Attribution License. See the main README for the source and license.
