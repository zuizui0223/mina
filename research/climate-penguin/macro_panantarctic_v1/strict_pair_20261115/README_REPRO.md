# Reproducing the strict original-citation pair audit (2026-11-15)

This is a post-result supplementary analysis within Antarctic macroecology Draft PR #214. The frozen Ecology Report and main branch are not changed.

Obtain the three previously verified public GitHub Actions ZIP artifacts from `zuizui0223/mina`:

- Run [#42775802254](https://github.com/zuizui0223/mina/actions/runs/42775802254), artifact **13744230591**: 277 strict same-source original two-species paired census rows (same site/season/citation/method).
- Run [#42961084667](https://github.com/zuizui0223/mina/actions/runs/42961084667), artifact **13829236358**: original 588 sites × 1993–2020 four-month SIC/GLORYS physical ocean panel.
- Run [#42610664607](https://github.com/zuizui0223/mina/actions/runs/42610664607), artifact **13669533413**: original 2,456 observed same-method site/species/year nest-count records.

The 2026-11-15 source reanalysis requires 5 or more genuine paired common-source census years over at least a ten-year span per pair/site, retains observed zeros, and never treats missing species as absent. Original matched support is 18 pair/site trajectories, 183 paired original site-years, 12 real sites, 2 reporting regions, 4 polar 250-km blocks, and 10 GLORYS source cells.

The downloadable user-facing reproducibility ZIP accompanying this analysis contains the complete independently run `analyze_strict_pairs.py`, `verify_independent.py`, exact cohort, source hashes, source-linked CSVs, and numerical verification, including the 34 triple-species algebra checks. Both scripts accept `PENGUIN_PAIR_SOURCE_DIR` to point to the three named source ZIPs; `PENGUIN_PAIR_OUTPUT_DIR` is optional.

**No new CI success is claimed.** This is not a new independent biological population dataset, a competition or dispersal test, or a calibrated Antarctic warming forecast.

## 2026-11-15 extension: observed nesting subtotals are not identical to ratios

The original strict source-matched 18 pair-site series and 183 pair site-years have now been algebraically decomposed into each species' independently observed nesting slopes, two-species summed nests, and a strict 34 site-year/3-site three-species subtotal subpanel.

- [Numerical result and limitations (Japanese)](REPLACEMENT_VS_COMMUNITY_TOTAL_JA_20261115.md)
- [18 pair-site decomposition CSV](strict_18_pairs_absolute_vs_relative_component_decomposition.csv)
- [34 genuine three-species site-year CSV](strict_34_three_species_siteyears_actual_counts.csv)
- [Three site-level subtotal sensitivity CSV](strict_three_species_total_sitelevel_sensitivity.csv)
- [Runnable decomposition](audit_component_replacement.py), [independent source-row verification](verify_decomposition_independent.py)

Recompute from the two strict source files already present in this directory:

```bash
python audit_component_replacement.py --source-dir . --out-dir .
python verify_decomposition_independent.py --source-dir . --out-dir .
```

Locally validated: original 18 source species slopes and 34 three-species rows were recovered; SciPy `linregress` independent calculation differs by at most 4.0×10⁻¹². Six gentoo/Adélie source-matched sites each have gentoo increase and Adélie decrease; two-species nest subtotals rise in five. Strict complete three-species subtotals rise at two of three sites although gentoo relative share rises in all three. This is not confirmation of causation, competition, a pan-Antarctic generality, or a climate-driven forecast. The biology remains geographically restricted to two original reporting regions.
