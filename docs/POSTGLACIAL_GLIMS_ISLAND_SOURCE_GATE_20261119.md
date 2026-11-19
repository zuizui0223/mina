# GLIMS / island retreat source-support pilot (2026-11-19)

## Objective and current boundary

Continue `ANTARCTIC_POSTGLACIAL_SOURCE_SUPPORT_V1.json` without rerunning frozen Paper2 A×H or the MAPPPD V41 same-/different-land gate. This phase tests whether public **dated** glacier outlines exist in source services near Antarctic penguin island landscapes. It does **not** test colonization or calculate new ice-free rock patch area.

## What was executed

- Code `scripts/audit_glims_antarctic_island_source.py` is on branch `analysis/postglacial-glims-sourcegate-20261119`; synthetic tests `tests/test_glims_antarctic_island_source.py`; isolated workflow `.github/workflows/postglacial-glims-source-gate.yml`.
- GLIMS / NSIDC original public WFS service uses `https://www.glims.org/geoserver/ows`; an outline represents glacier extent **at a source acquisition date** rather than true site-level absence/presence. [GLIMS official access](https://www.glims.org/glacierdata/) and [NSIDC GLIMS DOI](https://doi.org/10.7265/N5V98602).
- The source gate requests capabilities, identifies an unambiguous GLIMS glacier/outline layer, then uses WFS 1.0.0 GeoJSON with **300 maximum features per coarse pilot bounding box** near King George, Livingston and Anvers. It never treats the sampled first page as a complete island inventory, and never converts creation/publication date to image date.
- Only counts and source-date coverage, **no penguin nest counts**, are output. If the GIS service, layer semantics or GeoJSON is unavailable, it writes `HOLD` rather than filling zeroes. The actual status/years must be copied from the original Actions artifact, not assumed from the code.

## Geography and data: revised hard exclusions

1. **Loebel et al. 2025**: 4,817 calving fronts at 42 Antarctic Peninsula mainland marine-terminating glaciers 2013–2023; the paper explicitly **excludes glaciers on surrounding islands**. This dataset is not direct Anvers Point 8 ice-free patch exposure. DOI https://doi.org/10.5194/essd-17-65-2025 ; original archive https://doi.org/10.1594/PANGAEA.963725 .
2. **Thota et al. 2026**: *Geophysical Research Letters* DOI https://doi.org/10.1029/2026GL122660; 1989–2020 glacier outline comparison covers **Adelaide Island, Pourquoi Pas Island and Antarctic mainland** (203 glaciers; glacier area loss 207 km² across all three study subregions). The outlines assume **unchanged lateral boundaries**, hence retreated terminus area is not a census of newly suitable nest patches. Historic 1989 aerial images/DEMs are public via https://zenodo.org/records/17949026, but original interpreted 1989/2016/2020 glacier outlines are not yet ingested into this pipeline. This is a potentially suitable independent *island* source, but the published total must not be assigned to particular landmasses or Pygoscelis colony sites without site-level overlap.
3. **Cimino et al. 2026 Point 8** DOI https://doi.org/10.5038/2074-1235.54.2.1707: independent pre-existing biological demonstration on **Anvers Island**. Gentoo first appeared winter 2019, first nested 2020 and chicks were first successfully raised 2023 after 2018–2020 glacier retreat. Do not call first detection an absence transition unless pre-2019 visits with explicit negative results are verified. This is prior art / 1 landmass, not a whole-risk-set macro replication.
4. **GLIMS changing inventory semantics**: imagery dates and glacier IDs are not necessarily stable over RGI/GLIMS database migrations; reconcile polygons by source geometry, acquisition date, internal rocks and manual identities rather than assuming shared label equals identical glacier. An outline difference may be mapped change or methodology change.
5. **GLIMS island pilot spatial boxes**: chosen to test metadata retrieval, and contain potentially mainland, ocean and mixed island land. Site-level `landmass_id` must come from separately quality-controlled geography. First 300 returned features may omit years/glaciers; no species/sites inference permitted.

## Inference path only after real original metadata

A future genuine source-support gate must have (i) 2 original, independently dated polygons establishing patch was ice and later ice-free; (ii) exact same physical patch linked to an unambiguous penguin survey site; (iii) actual **visited** seasonal A/P records, with NR/missing excluded; (iv) multiple independent landmasses and repeated consecutive post-exposure survey seasons. Use the existing `scripts/audit_postglacial_support.py` unchanged to count these support events once source-backed CSVs exist. Its predetermined thresholds are >=5 landmasses, >=20 repeated site×species, >=10 verified A→P events across >=3 landmasses and >=30 A-risk season pairs. This is a source availability condition, **not** an ecological effect or a power calculation.

## Current decision

The GLIMS WFS source-gate run has been scheduled by push at [GitHub Actions run 44479750215](https://github.com/zuizui0223/mina/actions/runs/44479750215). Do not mark source data retrieved or report sample counts until a verified, completed artifact has been inspected. Keep Paper1, Paper2, main and previous STOPs unchanged.
