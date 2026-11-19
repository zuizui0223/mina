# V32 — Original 2009/10 versus 2019/20 AADC western Mac. Robertson Land spatial-grain audit

Frozen on 2026-10-22 before opening any new population estimate, original bootstrap magnitude, or local-island effect.

## Origin and decision question
AADC EDS 5516, DOI 10.26179/s2qa-s344, original member W Mac. Robertson Land Adelie penguin population estimates.xlsx, listed size 51,218 bytes by AADC's original 2026-10-21 public object manifest. Download the exact published source via AADC original REST API at dataset UUID 7673853e-9360-4563-a0e9-324300cfa0b7, not a synthesized record or article table.

Question: Does this original file contain a geographically explicit island/colony-ID × census-year panel suitable for a distinct set of true physical islands in BOTH 2009/10 and 2019/20? Or does it provide one or a few regional aggregate population estimates with ~1000 bootstrap uncertainty draws?

A bootstrap row is not one surveyed physical island. The original dataset includes Béchervaise Island demographic information, and is likely not independent from EDS1103, APBP or MAPPPD. Do not claim source independence without checking original census/event identifiers.

## Fixed, no-outcome initial gate
1. Exact trusted AADC HTTPS dataset+object member URL and exact original published byte length (51,218). Verify ZIP signature, record SHA256 and size.
2. Inspect original sheet names and declared rows/columns. Read up to the FIRST EIGHT source ROWS in each sheet and display only clearly literal text labels, with purely numeric strings or Excel numbers completely redacted. No nest-count value, percentile value, resampled draw or source animal magnitude may be opened in this stage.
3. Identify literal original text field names for island_id/island name, site/colony and region/group. Identify publisher-text references to 2009, 2019, occupancy, bootstrap and aggregation. A sheet row count by itself does not imply number of islands.
4. Gate for a future new multi-region island distribution analysis: original row-level permanent physical island identifiers, matched original nesting estimates at the same named islands for both census seasons, at least 10 distinct verified physical islands and at least 3 distinct geographic monitoring regions. Any missing geographic ID, unknown unit, or single regional aggregate is HOLD, not a new island-count effect. Frozen before any biological estimates.
5. The two surveys are 10 years apart, NOT an annual synchrony time series. Uncertainty from 1000 bootstrap draws belongs to each original aggregate. Do not convert draws to independent sites or original measurement count.
6. Do NOT fit, regress, or publish any penguin population, occupancy-change, migration, area, connectivity, rock, climate or between-island effect during V32.

If no physical island ID is shown in first eight header/text rows, classification must remain HOLD_UNKNOWN_GRAIN rather than asserting no island-level data exist elsewhere in the workbook. A subsequent independently frozen Stage-2 source metadata audit may inspect *only ID columns* without numerical animal responses.

Separate from V31 east Antarctic Béchervaise–Verner descriptive r=+0.754 and V27 broad APBP spatial-synchrony gate failure; both unchanged. Paper1 Ecology PR189 scientifically frozen.
