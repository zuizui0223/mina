# Global emperor penguin decline route — support audit v1

**Status:** SUPPORT PASS; effect remains unopened at this commit.

The pre-effect contract `EMPEROR_GLOBAL_DECLINE_SPATIAL_REDUNDANCY_V1` was committed before colony-level abundance-index magnitudes were summarized.

## Audited source

    davidiles/EMPE_Global
    analysis/output/model_results/3_Colony_Level/colony_summary.csv

## Structure

The file contains:

- 50 colony/site series;
- annual rows from 2009 through 2018;
- one row per colony per year;
- explicit site IDs and site names;
- fixed ice-region membership;
- posterior colony abundance summaries.

The frozen primary abundance column is:

    N_median

which is explicitly the posterior median colony-level abundance index.

## Frozen endpoint support

2009:

    50 rows
    50 unique colonies
    N_median present for 50/50.

2018:

    50 rows
    50 unique colonies
    N_median present for 50/50.

Thus the paired roster is mechanically:

    all 50 modelled colonies.

No colony is dropped.

## Fixed regional structure

Eight source-defined ice regions are represented:

- Amundsen Sea
- Australia
- Bellingshausen Sea
- Dronning Maud Land
- East Indian Ocean
- Victoria Oates Land
- Weddell Sea
- West Indian Ocean

Regional analysis remains secondary and must report every region with >=3 paired colonies.

## Decision

    source support: PASS
    paired roster: 50/50 colonies
    frozen years: 2009, 2018
    primary value: N_median
    effect: not yet summarized at this support commit.

The next step may now open all 50 paired endpoint medians once and apply the frozen contract without changing years, roster, region definitions or summary column.
