# Team win rates and toss impact: who wins, and does the toss matter?

Same committed Cricsheet snapshot as the earlier analyses: 1,243 recorded
matches, 2008-2026, nothing downloaded or refreshed. These are snapshot
calculations, not live official standings.

## Questions answered

1. How many recorded matches has each team played and won, and at what rate?
2. How often does the toss winner go on to win, overall and by toss decision?

See [team win rates](../results/team_win_rates.csv) and
[toss impact](../results/toss_impact.csv).

## Team win rates

Appearances count every recorded match, including ties and no-results; wins
need a recorded winner, so only the 1,218 decided matches contribute.

| Team | Matches | Wins | Win % |
| --- | ---: | ---: | ---: |
| Gujarat Titans | 77 | 47 | 61.04 |
| Chennai Super Kings | 266 | 148 | 55.64 |
| Mumbai Indians | 291 | 155 | 53.26 |
| Kolkata Knight Riders | 278 | 140 | 50.36 |
| Royal Challengers Bengaluru | 286 | 143 | 50.00 |
| Rising Pune Supergiant | 30 | 15 | 50.00 |
| Rajasthan Royals | 251 | 123 | 49.00 |
| Sunrisers Hyderabad | 211 | 102 | 48.34 |
| Lucknow Super Giants | 72 | 34 | 47.22 |
| Punjab Kings | 278 | 126 | 45.32 |
| Delhi Capitals | 281 | 125 | 44.48 |
| Gujarat Lions | 30 | 13 | 43.33 |
| Kochi Tuskers Kerala | 14 | 6 | 42.86 |
| Deccan Chargers | 75 | 29 | 38.67 |
| Pune Warriors | 46 | 12 | 26.09 |

Mumbai Indians have the most recorded wins (155 in 291 matches) and Chennai
Super Kings the best rate among the ever-present teams (55.64%). Gujarat
Titans lead on rate (61.04%) but from only 77 matches since 2022, and the
short-lived franchises (Rising Pune Supergiant, Gujarat Lions, Kochi Tuskers
Kerala) played 30 or 14 matches, so their rates move a lot per match.

Team labels are the snapshot's current franchise names: a franchise that
changed its name across seasons is one label here, and defunct franchises
appear under the name the dataset records.

## Toss impact

Of the 1,218 decided matches, the toss winner won 628 (51.56%) - close to a
coin flip. Split by what the toss winner chose:

| Toss decision | Decided matches | Toss winner won | % |
| --- | ---: | ---: | ---: |
| bat | 408 | 185 | 45.34 |
| field | 810 | 443 | 54.69 |
| overall | 1218 | 628 | 51.56 |

Captains chose to field in 825 of 1,243 tosses (about two thirds), and teams
that chose to field won 54.69% of their decided matches, against 45.34% for
teams that chose to bat. This is a descriptive split, not proof that fielding
first causes wins: ground, dew, team strength and era all sit behind these
numbers, and 23 decided matches used D/L. Ties and no-results are excluded
from every toss row because they have no winner.

## Limitations

- Snapshot through 31 May 2026; not refreshed for this increment.
- Win % is wins over all recorded appearances, ties and no-results included,
  so unbeaten-in-terms-of-defeats is not measured here.
- Descriptive only. No significance testing, no per-venue or per-era split
  yet; venue trends and chasing vs defending are later stages.
