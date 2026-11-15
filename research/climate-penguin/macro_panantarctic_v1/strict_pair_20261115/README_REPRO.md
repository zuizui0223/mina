# Reproducing the strict original-citation pair audit (2026-11-15)

This is a post-result supplementary analysis within Antarctic macroecology Draft PR #214. The frozen Ecology Report and main branch are not changed.

Obtain the three previously verified public GitHub Actions ZIP artifacts from `zuizui0223/mina`:

- Run [#42775802254](https://github.com/zuizui0223/mina/actions/runs/42775802254), artifact **13744230591**: 277 strict same-source original two-species paired census rows (same site/season/citation/method).
- Run [#42961084667](https://github.com/zuizui0223/mina/actions/runs/42961084667), artifact **13829236358**: original 588 sites × 1993–2020 four-month SIC/GLORYS physical ocean panel.
- Run [#42610664607](https://github.com/zuizui0223/mina/actions/runs/42610664607), artifact **13669533413**: original 2,456 observed same-method site/species/year nest-count records.

The 2026-11-15 source reanalysis requires 5 or more genuine paired common-source census years over at least a ten-year span per pair/site, retains observed zeros, and never treats missing species as absent. Original matched support is 18 pair/site trajectories, 183 paired original site-years, 12 real sites, 2 reporting regions, 4 polar 250-km blocks, and 10 GLORYS source cells.

The downloadable user-facing reproducibility ZIP accompanying this analysis contains the complete independently run `analyze_strict_pairs.py`, `verify_independent.py`, exact cohort, source hashes, source-linked CSVs, and numerical verification, including the 34 triple-species algebra checks. Both scripts accept `PENGUIN_PAIR_SOURCE_DIR` to point to the three named source ZIPs; `PENGUIN_PAIR_OUTPUT_DIR` is optional.

**No new CI success is claimed.** This is not a new independent biological population dataset, a competition or dispersal test, or a calibrated Antarctic warming forecast.
