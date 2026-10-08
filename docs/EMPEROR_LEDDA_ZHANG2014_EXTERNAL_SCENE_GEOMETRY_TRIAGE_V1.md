# Ledda 2014 source triage: a year-labelled colony list is not same-day biological occupancy

**Date 2026-10-08.** Exploratory observational crosswalk in PR195. No 2014 Zhang/Li shapefile or Landsat-scene dates read. This is a **source-availability discovery**, NOT a new confirmed 2014 nesting event or a causal explanation. Ecology submission PR189 remains scientifically frozen.

## Three different meanings currently coexisting under the same Ledda Bay label

1. **LaRue et al. (2024)** original high-resolution satellite image dated **2014-10-13** at the historical `LEDD` colony label was marked `bpresent=no` and annotated `fast ice available no birds`. This is a **single scene**, not a whole-season census proving true local extinction or no breeding in Ledda Bay.
2. **Fraser/Massom v2.2 independent MODIS physical ice** for the *nominally preceding* 2014-09-28 to 2014-10-12 15-day interval shows **0/28 class4 pixels within 3 km of LaRue et al.'s coordinate (−74.228, −130.784)** versus **30/30 within 3 km of Fretwell et al. 2021's Ledda coordinate (−74.272, −131.243)**. The geodesic center separation is 14.692 km. This is a **physical landfast-ice classification** at *two different locations*, not penguin biological detection. Class0 combines ocean/pack/uncertain fill; and source maps may use adjacent-date retrospective imagery.
3. **Zhang and Li (2020)** *Pan-Antarctic Emperor Penguin Colony Dataset (2000, 2014, 2018)* explicitly includes **Ledda Bay** in the published list of **49 colony locations in the 2014 component** (Table 4). Their source data are derived from Landsat 2014 September–October visual assessment of **guano staining**, *guided by historical high-resolution colony locations*. The 2014 list entry alone cannot tell whether a genuine positive **2014-specific** guano polygon exists, whether the authors carried forward a known colony location, exactly when the source Landsat scene was acquired, or whether **live birds** were present on Oct 13.

These three are neither logically independent individual-level censuses nor necessarily in contradiction: `source historical colony`, `current guano`, `currently visible live birds`, `landfast ice available`, `viable breeding platform`, and `successful fledging` are distinct states.

## What could actually change the science

The original Zhang/Li dataset is advertised as `PanAnta.PenguinColony.rar`, about 142 KB, containing .xlsx colony geolocation and Landsat scene catalogs and .shp point/polygon representations (44 packaged files). It is linked at [official geodoi dataset](https://www.geodoi.ac.cn/WebEn/doi.aspx?Id=1540), doi [10.3974/geodb.2020.05.06.V1](https://doi.org/10.3974/geodb.2020.05.06.V1). This archive has **not** yet been opened here. The dataset paper includes the *2014 Ledda Bay* label in Table 4, but supplies no feature coordinates or image dates for this label on its text page.

Before inspecting ANY Ledda 2014 polygon feature, freeze:
- Feature 2014 membership must be verified in the .dbf, no interpolation from Table 4.
- Source .prj must be validated and geographic coordinate transformed without guessing CRS.
- Reproduce **distance to both precommitted Ledda anchors** independently, using nearest polygon boundary as well as centroid.
- If available, link **source Landsat acquisition date**. If no scene date, location-only evidence cannot be interpreted as cooccurrence on October 13.
- Presence of **guano** does not prove currently visible birds, active nesting that day, successful reproduction, or immigration.
- If 2014 Ledda has **no source polygon**, explicitly report '2014 table entry not a dated independent biological presence', not 'absent colony' or 'no movement'.

No archive or shapefile should be redistributed from the source without permission; use only necessary aggregate diagnostics, cite the original source, and honor the repository's reuse terms.

### Discriminating outcomes and interpretations

| Source-level result if original 2014 archive can be opened | Allowed conclusion | Not allowed |
|---|---|---|
| 2014 Ledda polygon and exact Landsat date; maps close to Fretwell coordinate | Different observation footprints plausibly help explain October-source discordance | 14.7-km tracked penguin movement or socially chosen alternative |
| 2014 polygon close to LaRue coordinate | Source discrepancy still exists at similar geographic support; investigate modality, date, guano persistence and detection | Independently verified live same-day birds |
| Multiple spatially distinct Ledda 2014 features | Need explicit whether one split colony or multiple site labels; geometry checks | Treat number of polygons as number of founded colonies |
| 2014 label with no identifiable feature or timestamp | HOLD: 2014 table cannot resolve biological occupancy or position | Publish a 2014 recolonization finding |

**Novelty verdict:** Access to a year-matched 2014 independently georeferenced observation could validate a particular mismatch and potentially identify how fixed site locations can alias physical habitat. That alone is **not yet a new ecological causal mechanism**: contemporaneous nesting success, individual origin or an exogenous habitat-choice perturbation still remain missing.

## Existing reproducibility

- [Source six-year paired physical ice, 1/3/5 km](https://github.com/zuizui0223/mina/actions/runs/37771210709) — successful
- [Source-pinned six selected winter 2024 SAR colony positions](https://github.com/zuizui0223/mina/actions/runs/37772511782) — successful, 54 positive scene positions, max 1.7272 km from author site
- `contracts/EMPEROR_LEDDA_ZHANG2014_GEOMETRY_AND_SCENE_GATE_V1.json` — 2014 feature-level gate, fixed before archive access
- `scripts/probe_zhang2014_official_archive_structure_v1.py` — official HTML/source link metadata only, no biological feature read

References: Zhang and Li 2020 [paper](https://www.geodoi.ac.cn/WebEn/HTML_INFO.aspx?Id=931e6a56-4cc6-46f1-a858-9d9f3792cd05) / [data](https://www.geodoi.ac.cn/WebEn/doi.aspx?Id=1540); LaRue et al 2024 [source](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/empe_satellite_2023-05-25.xlsx); Fraser/Massom [physical dataset](https://doi.org/10.26179/5d267d1ceb60c).
