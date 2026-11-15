# Antarctic marine salinity synchrony: era-dependence sensitivity (2026-11-15)

**Status:** post-result descriptive stability audit; extension of Draft PR #214, not a new paper or biological p-value. Based on the existing 18-region × 28-year source-verified OSI SAF/GLORYS regional physical panel. No penguin outcomes were opened for this audit.

## Result

The already reported all-period equal-region annual synchrony is independently recovered from 504 original region-year rows: PC1 (warmer/low-ice thermal axis) **19.71%** versus PC2 (salinity axis) **52.14%**. The originally published physical PCA spatial variance fractions of PC1=60.37% and PC2=33.38% are different estimands.

New fixed sensitivity calculations standardize each region within each evaluated time window (each region one vote) and calculate n_regions × sum_t(mean_region_z_t²) / sum_(r,t)(z_rt²).

| Full 18-region panel | PC1 common-year fraction | PC2 common-year fraction | PC2−PC1 |
| --- | ---: | ---: | ---: |
| 1993–2020 (28y) | 19.71% | 52.14% | +32.43pp |
| 1993–2000 only (8y) | 16.64% | 16.39% | −0.25pp |
| 2001–2010 only (10y) | 17.55% | 27.75% | +10.19pp |
| 2011–2020 only (10y) | 22.12% | 71.28% | +49.15pp |
| 2011–2020 *omitted* (18y) | 20.25% | 27.46% | +7.21pp |

The stronger PC2 coherence in the 28-year aggregate is **not constant through time**; it is concentrated in the 2011–2020 decade. Omitting that decade reduces, but does not erase, the 28-year contrast.

Geographic replication sensitivity: for the 13 original regions with ≥3 colonies, ≥2 polar blocks, and ≥2 distinct ocean cells, common-year fractions are **17.80% PC1 and 58.74% PC2** over 1993–2020, and **18.42% PC1 versus 35.32% PC2** with 2011–2020 removed. Single-region omissions yield PC2−PC1 ranges of **+27.95–35.20pp** for all 18 regions and **+35.61–43.40pp** for 13 supported regions.

All single-era plus single-region omissions retain PC2>PC1: margin **+3.37–47.87pp** among 18 regions and **+12.72–52.38pp** among the 13 geography-supported regions. Reweighting unique GLORYS marine cells equally within each region gives the same qualitative outcome. In 2011–2020 alone, leave-one-calendar-year-out differences remain **+37.09–63.80pp** among all 18 regions; not one exceptional year.

## Source and validation

- Archived Actions run: https://github.com/zuizui0223/mina/actions/runs/43049546362, artifact 13869360730.
- Exact input: original_source_18_region_28year_PC1_PC2_site_vs_unique_cell.csv; 18 × 28 = 504 genuine region-years. SHA256: 99b794fa585ecf7b2ca6651456e0056f2e43c321a58daeb9e82d5b90eb3b3d29.
- A fresh Python/numpy independent implementation reproduced the archived all-period PC1 fraction to within 1e-12 and PC2 to rounding; verified original 18-year×28-region balance, each region's unchanged geographic support, 13 pre-existing multi-block eligibility and the mathematical 0–1 variance bound.
- Full audit grid contains 528 fixed-axis records (both axes, 18/13 region cohorts, site/cell weighting, all-period and each of three omitted eras, each single region omission). Results also inspected by within-era and late-era leave-one-year-out diagnostics.
- The source remains the **same GLORYS assimilation product** and observational marine SIC; no new independent in-situ salinity validation is claimed. Existing EN4 source coverage is insufficient for the 18-region 28-year independence test (2015 strict: 385 profiles, five regions).

## Interpretation boundary

This is an **episodic temporal covariance property of a marine reanalysis**, not evidence that greenhouse warming caused increasing salinity synchrony, that salinity acts as a demographic driver, or that penguin communities respond synchronously. The short 8–10-year within-era windows and temporal autocorrelation prevent formal era-to-era significance inference. GLORYS source assimilation procedures and changes in hydrographic observation coverage remain candidate explanations requiring independent verification. Retain in the single macro manuscript as a physical scale/time-resolution qualification to the warming–ice–salinity–vegetation–niche discussion. Do not turn the static 2017–2023 terrestrial map into a 28-year greening trajectory or reopen frozen Paper 1/2.
