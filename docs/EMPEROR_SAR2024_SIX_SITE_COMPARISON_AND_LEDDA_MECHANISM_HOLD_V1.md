# Six independent 2024 winter SAR colony site centroids: what they can and cannot resolve about Ledda

**2026-10-08 / PR195 / exploratory retrospective source audit.**

## Source and contrast

A separate public 2024 high-resolution SAR study, LaRue et al. (2026, doi:10.1002/rse2.70083), provides date-specific detected winter huddle centroids for **six** emperor penguin colonies. Its original source code/data are published at https://github.com/mla150/SAR-Emperor, `empe_sar_summary_20250801.csv`. We crosswalk each source colony to **LaRue et al. 2024**'s already published approximate location in `davidiles/EMPE_Global` (pinned `13f71112da43c1fd082273677757b41c550457ed`, `data/colony_attributes.csv`). Source 'Atka Bay' is the same named original roster item 'Atka'. No dynamic annual Ledda observations are supplied in SAR2024 and no inference about Ledda's actual movements is licensed.

SAR source has 64 image-date rows at six selected sites; **54** have positive mapped huddle area and finite huddle mean latitude and longitude. **Ten** zero-area rows have no usable source huddle centroid and must be excluded **rather than counted as confirmed ecological absences**.

Source-pinned **exploratory** original author-location to date-specific positive SAR mean-huddle location great-circle distance:

| Colony (2024 SAR) | Positive SAR dates | Maximum distance to source static site |
|---|---:|---:|
| Atka Bay | 9 | ~1.73 km |
| Cape Crozier | 7 | ~1.40 km |
| Cape Roget | 11 | ~0.78 km |
| Cape Washington | 10 | ~1.18 km |
| Coulman Island | 11 | ~1.18 km |
| Franklin Island | 6 | ~1.13 km |
| **Total** | **54** | **0/54 dates beyond 3 km** |

These figures are independent-source descriptive computations that require the dedicated GitHub workflow `.github/workflows/emperor-sar2024-six-colony-site-comparator-v1.yml` to pass before advertising reproducible CI status. Re-running the pinned comparison produces a machine-readable file with distances, medians and 1/2/3/5-km thresholds.

**Biological interpretation:** Ledda Bay's **14.692-km difference between two *publications*** is much larger than the source author-site versus SAR huddle mean positions across these six *selected winter-2024 colonies*. It therefore should not be dismissed as the inevitable scale of within-winter penguin movement. But the SAR six-colony sample cannot infer the absence of 14-km moves across a decade, and it cannot identify which Ledda coordinate was the 2014 nest location.

## Why this is a limit on the current ecological question

Both this comparison and the preceding ice-level source audit reinforce that:
- A named colony is **not** interchangeable with a single biologically verified colony-year nesting polygon;
- A high-resolution observed huddle centroid is a group average, not a colony boundary or tracked founder;
- A source label `bpresent=no`, `areasum=0`, or Bayesian latent posterior mean zero is **not** a proven physical vacancy or local ecological extinction;
- A 3-km MODIS class4 buffer is a physical indicator, not necessarily a platform permitting clutch survival or immigration.

**Already published, not new:** the LaRue 2026 paper established winter SAR huddle detection and broad phenological attendance patterns. It is not new that emperor colonies can change position seasonally (Macdonald et al. 2026 `10.1038/s43247-026-03906-0`). Nor is it new that fast-ice persistence shapes their habitat (Labrousse et al. 2023 `10.1126/sciadv.adg8340`). We claim none of these as a new biological process.

**Scientific status after this cross-check:** We have verified georeference uncertainty in historical Ledda comparisons, and a bounded independent source comparator, but **still cannot select a causal competition, social memory, immigration/rescue, or nesting-stage mechanism** without site-year dated nesting footprints and breeding outcomes. Freeze the current Ledda extension as a source-and-measurement audit rather than presenting it as a novel island-biogeographic law. PR189 Ecology science untouched.

Provenance:
- https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/colony_attributes.csv
- https://github.com/mla150/SAR-Emperor/blob/main/empe_sar_summary_20250801.csv
- https://doi.org/10.1002/rse2.70083
