# Venue and chasing/defending outcomes

This increment uses the same frozen Cricsheet snapshot as the earlier analyses:
1,243 matches across 2008-2026. It does not fetch new data or claim live official
records. Contains information from Cricsheet, made available under the ODC
Attribution License. Source: https://cricsheet.org/.

## Reproduce

```bash
python src/analyze_venues.py
python -m pytest -q
```

Outputs:

- `results/venue_outcomes.csv`: 41 exact recorded venue labels, alphabetically.
- `results/season_chasing_outcomes.csv`: 19 seasons, chronologically.

Both tables report total matches, decided matches, chasing wins, defending
wins, ties, no-results, D/L decided matches and chasing win percentage.

## Definitions

A recorded normal result with a positive wickets margin counts as a chasing
win. A positive runs margin counts as a defending win. Ties and no-results
remain in total matches but are excluded from the chasing win percentage:

`100 * chasing_wins / decided_matches`

A group with zero decided matches has a blank percentage, not a 0% success
rate. Ties remain ties even if a later Super Over settled the fixture. D/L
results stay in the analysis; the separate count makes their presence visible.
Inputs must have unique nonmissing match IDs, valid team/result fields,
nonblank venues, nonnegative whole-number margins and known adjustment labels.

Venue names are used exactly as recorded. Different spellings, city suffixes
and historical names are NOT combined into a single physical ground. For
example, the snapshot has separate Bangalore/Bengaluru venue labels. These
are venue-label summaries, not an authoritative stadium ranking. A future
normalisation step would need an explicit, reviewed alias map.

## Measured findings

- Chasing teams won 660 of 1,218 decided matches: **54.19%**. Defending teams
  won 558. The other 25 matches are 16 recorded ties and nine no-results.
- There are 23 D/L decided matches included in those totals.
- The exact label `Wankhede Stadium, Mumbai` has the largest recorded sample:
  132 matches, 131 decided, 72 chasing wins and 59 defending wins. Its chasing
  win rate is 54.96% of decided matches, not of all 132 fixtures.
- In 2026, chasing teams won 45 of 72 decided matches, or 62.50%, in this
  snapshot. This is a descriptive season comparison, not a forecast.

## Limits and checks

Different sample sizes, team strength, playing conditions, shortened matches
and changes across seasons can affect these percentages. The tables do not
establish that choosing to chase causes more wins or that a particular ground
is better for chasing. Small venue samples are retained rather than silently
filtered, with the denominator shown beside each percentage.

Tests include small worked examples, undefined-rate and exact-label behavior,
invalid inputs, and an independent plain-CSV recount of every table cell.
They also check that chasing plus defending wins equal decided matches and
that decided matches plus ties plus no-results equal all matches. The full
suite has 71 passing tests, including all 53 earlier regression tests.

Charts and venue alias normalisation are not included in this increment.
