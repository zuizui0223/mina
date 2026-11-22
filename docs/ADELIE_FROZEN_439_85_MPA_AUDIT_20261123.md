# Frozen 439 colony-season / 85-colony MPA overlay — source audit, 2026-11-23

**Status: COMPLETE descriptive geographic reconstruction. No new ecological model was fitted.**

The original 439 observations are reproduced from Draft PR #214's pinned commit c67e55c9f4f657ef308c02a85c6ff366dce8e1f4, using original matched_isotope860.csv, polynya_physical860.csv and colony_geography.csv. Their original Git blob hashes are tested in scripts/reconcile_frozen_adelie439_mpa.py.

## Exact denominator lineage

| Stage | Site×years | Sites |
|---|---:|---:|
| Youngflesh RDS original site-level pixel support, 2004–2010 | 583 | 113 |
| Matched optical isotope + summer-marine-source records, 2004–2010 | **439** | **85** |
| Nonmissing historical winter-polynya exposure | **439** | **85** |

Thus the 583→439 loss of **144 site-years** (28 sites) occurred entirely upstream, in the original isotope and marine-source matching stage, not in the winter-polynya exposure gate. Which individual matching variable excluded each source row remains unresolved. Exact site×year keys are preserved in the successful Actions artifact.

The frozen 439 observations cover 11 source regions and seven winter starts (2004–2010), have 34 valid measured zero-polynya records, winter polynya fraction mean **7.030444%** and SD **6.318696 percentage points**. The frozen isotope response and existing model coefficient are untouched.

## Frozen 85-site spatial overlay

Official source: https://github.com/ccamlr/data/blob/main/geographical_data/mpa/CCAMLR_MPA.json (EPSG:6932; five Ross Sea sub-zones and one South Orkney southern shelf zone). Original site coordinates come from PR #214's pinned colony_geography.csv at 100 km, not approximate raw-pixel centroids.

- 15 / 85 sites have a **100-km geodesic full circle** intersecting currently designated MPA polygons; all 15 are in Victoria Land (Ross Sea). 70 do not intersect.
- 79 / 85 sites have at least four observed winters and can be colour-mapped by their within-site winter polynya fraction SD; six sites are grey crosses, not ranked.
- Among the 79 sufficiently observed sites, median within-colony SD is 2.82547 percentage points. There are 13 MPA-intersection sites in this subgroup.
- Current MPA intersection is NOT the observed marine foraging area protected, NOT the colony diet's sensitivity, and NOT protection effectiveness. The Ross Sea MPA was designated in 2016, after the 2004–2010 observations.

## Why the old 472/88 map must be superseded

Only **69 sites** overlap between the former approximate 88-site source panel and the true frozen 85-site cohort. **16** frozen sites were absent from the former 88, and **19** former sites are absent from the frozen 85. Only **371** site×years share the exact keys. Approximate versus original polynya fraction on these common rows correlated r=0.999812 but have 0.14970 percentage-point RMSE. Never describe the frozen 85 as the preliminary 88 minus three arbitrary sites.

## Reproduction and manuscript scope

Successful workflow and artifact: https://github.com/zuizui0223/mina/actions/runs/45082480478 . Script: scripts/reconcile_frozen_adelie439_mpa.py. Original manuscript Draft PR #214 remains unchanged.

Suggested optional Figure Sx caption: Historical winter coastal-polynya exposure variability at the 85 source-matched Adélie colonies in the frozen 439-season optical isotope-proxy analysis. Colours show within-colony annual SD for the 79 sites with at least four observed winters (2004–2010); grey crosses indicate six unranked sites. Lines show currently designated CCAMLR MPAs. For 15 sites the 100-km analysis circles intersect a current MPA polygon, all on the Ross Sea coast. These retrospective geographic intersections do not establish feeding locations or causal conservation effects.
