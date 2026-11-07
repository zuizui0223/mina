# Signy diet components v1

Exploratory explanation of the already observed sea-ice association, dated 2026-11-06. Nine Signy gentoo seasons (2001/02–2009/10), 73 valid stomachs, the same cohort and food denominator as the completed external comparison. The response decomposed here is the **single-species mean fish fraction**, not the original three-species absolute distance.

## Result and scope

Recorded positive-fish-mass frequency is associated with antecedent August–November SIC: r = 0.7829; exact two-component max-|r| adjusted p = 0.02293. The fish fraction conditional on positive mass has r = 0.6241 and adjusted p = 0.12956. The mean-response slope is exactly the sum of the frequency, conditional-composition and covariation terms. This is observational accounting, not causal attribution or individual switching.

Read [REPORT_JA.md](REPORT_JA.md), view [Figure 1](Figure_1_diet_components.png) or its [PDF](Figure_1_diet_components.pdf), and consult [summary.json](summary.json). The [design](../../work/signy_diet_components_v1/DESIGN.md) was written before component associations were computed, with the overall association already known; it is not a preregistration.

## Reproduce

Run from the repository root in the project Python environment (numpy, pandas, scipy, matplotlib; statsmodels for the independent verifier). The source directory is a cache of the BAS CSVs. The main program downloads their source archives if they are absent, then requires the pinned CSV hashes. The sea-ice input and the Palmer extraction are already tracked in this repository.

```bash
python research/climate-penguin/work/signy_diet_components_v1/analyze.py --source-dir build/signy_diet_raw
python research/climate-penguin/work/signy_diet_components_v1/plot.py
python research/climate-penguin/work/signy_diet_components_v1/independent/recalculate.py --source-dir build/signy_diet_raw
python research/climate-penguin/work/signy_diet_components_v1/independent/compare_primary.py
python -m pytest tests/test_signy_diet_components_v1.py -q
python research/climate-penguin/work/diet_niche_manuscript_v1/verify_assets.py
```

The independent implementation is in [work/signy_diet_components_v1/independent](../../work/signy_diet_components_v1/independent). Its command and comparison record are documented in [VALIDATION.json](VALIDATION.json). No individual Palmer data are reconstructed.

## Outputs

| File | Contents |
|---|---|
| [gentoo_primary_nine_seasons.csv](gentoo_primary_nine_seasons.csv) | Primary year-level p, c, m, recovered masses and SIC |
| [species_season_components.csv](species_season_components.csv) | Gentoo primary cohort and Adélie descriptive support; undefined conditional means stay empty |
| [annual_accounting_terms.csv](annual_accounting_terms.csv) | Three varying terms; add the constant mean(p) × mean(c) to recover m |
| [leave_one_season_accounting.csv](leave_one_season_accounting.csv) | Re-centred three-term slopes for all nine omissions |
| [palmer_reported_detection_reference.csv](palmer_reported_detection_reference.csv) | Assumption-dependent reported-detection ratios and rounding bounds; not a harmonized positive-mass comparison |
| [source_manifest.json](source_manifest.json) | Source DOI/URL and SHA-256 values |
| [SOURCE_METHODS.md](../../work/signy_diet_components_v1/SOURCE_METHODS.md) | Primary-source definitions and unresolved measurement issues |
| [VALIDATION.json](VALIDATION.json) | Numerical, software, figure and link checks, including the pre-existing repository failures |

The component family contains exactly p and c and uses the same 9! SIC permutations. It does not adjust prior project-wide exploration. Recovered grams are one-time stomach contents, not intake rates. The retained [three-species manuscript](../diet_niche_manuscript_v1/MANUSCRIPT_JA.md) and [Palmer external comparison](../palmer_signy_diet_external_v1/REPORT_JA.md) establish the scope within which this additional description is used.
