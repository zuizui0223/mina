# Palmer–Signy diet comparison: reproducible external-region diagnostic

Read [REPORT_JA.md](REPORT_JA.md) for the findings, [summary.json](summary.json) for full numerical results, and [VALIDATION.json](VALIDATION.json) for independent verification and test status. The unchanged three-species Signy result is in [the main manuscript](../diet_niche_manuscript_v1/MANUSCRIPT_JA.md).

## Re-run from the repository root

The project's Python environment requires NumPy, pandas, SciPy and matplotlib. The independent verification also uses statsmodels. The complete project test suite has further optional dependencies documented in the project configuration.

```bash
python research/climate-penguin/work/palmer_signy_diet_external_v1/sources/extract_pickett2018.py
python research/climate-penguin/work/palmer_signy_diet_external_v1/analyze.py \
  --source-dir build/palmer_signy_signy_sources \
  --palmer-table research/climate-penguin/work/palmer_signy_diet_external_v1/sources/pickett2018_palmer_diet_species_season.csv \
  --out research/climate-penguin/outputs/palmer_signy_diet_external_v1
python research/climate-penguin/work/palmer_signy_diet_external_v1/plot.py
python research/climate-penguin/work/palmer_signy_diet_external_v1/independent/recalculate.py \
  --source-dir build/palmer_signy_signy_sources
python research/climate-penguin/work/palmer_signy_diet_external_v1/independent/compare_primary.py
python -m pytest tests/test_palmer_signy_diet_external_v1.py -q
```

The analysis downloads the two Signy CSV archives from BAS if absent and requires their pinned SHA-256 hashes. Existing local copies with changed hashes are rejected. Palmer source re-extraction is offline from the stored CC BY 4.0 article XML and publisher table excerpt. Sea ice uses the pinned repository monthly source; it does not redownload satellite grids. Running the analysis regenerates numeric outputs, not the manually maintained report or verification record.

## Files and units

| File | Content |
| --- | --- |
| `signy_species_seasons.csv` | 18 species-season means; valid/source stomach counts and denominator sensitivities |
| `palmer_species_seasons.csv` | 12 published species-season means in fraction units; no reconstructed individuals |
| `annual_pair_comparison.csv` | 15 region-season rows, species means, signed gap, absolute gap and matched SIC |
| `annual_ice_proxies.csv` | GOPT 9 seasons; BISC and LITC 6 each |
| `monthly_ice_source_subset.csv` | 84 checked site-month records supporting the comparison |
| `region_effects.csv` | Primary regional effects, HC3 coefficient intervals, exact permutations and sensitivities |
| `signy_to_palmer_transport.csv` | Six unaltered predictions, source-mean predictions, support flags and errors |
| `summary.json` | Full diagnostics, sensitivity results, exclusions and transfer scores |
| `source_manifest.json` | Primary source identifiers and exact input hashes |
| `VALIDATION.json` | Independent calculation comparison and tests; retained baseline failures disclosed |
| `independent/` | Separate raw-source calculation, annual CSVs and exact comparison record |
| `Figure_1_external_comparison.png/.pdf` | Common-scale regional view, Palmer enlargement, and external predictions |

All stored fish values and `distance` use fractions (0–1); `sic_aug_nov` is percent (0–100); slopes are per 10 SIC percentage points. Figures show diet differences in percentage points by multiplying D by 100. `year` always means the starting year of the breeding season. Nine plus six region-seasons span 14 unique calendar starting years, not 15 independent years.

## Interpretation boundaries

This is an exploratory retrospective comparison with a published target cohort, not a prospective forecast trial or causal test. The Palmer species were sampled primarily at different colonies. Its rounded annual means do not provide individual sampling dates or masses, and the published gentoo sample count is inconsistent between table and text. Six seasons cannot establish a zero association or a significant regional slope difference. No local slope is used to predict competition, whole-niche overlap, or population size.
