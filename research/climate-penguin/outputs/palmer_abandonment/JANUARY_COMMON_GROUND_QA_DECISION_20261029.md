# Palmer January 2007/2008 QA matched ground-point gate — executed

**Observed result: only spatial QA feasibility, not vegetation succession.** [Successful real-source workflow](https://github.com/zuizui0223/mina/actions/runs/40860291095) used STAC Landsat Collection 2 Level 2 QA_PIXEL, six Jan-2007 scene records and three Jan-2008 records, all 18 combinations per island. Original downloadable Actions artifact **12891775316**, ZIP SHA-256 **d0b1450e9422f0b376b31bc704470ed0aa393ba33261dd5533ef4d071ddbb979**. All 27 site×scene original QA reads succeeded. The January window was added **post hoc to remedy February–March 2008 missing support**, not a preregistered fixed ecological outcome test.

Each site has 25 **unchanged projected EPSG:3031 ground probes** at dx,dy = ±80, ±40, 0 metres around its published registration coordinate. Each acquisition was sampled at exactly those geographic locations in the native Landsat QA grid; cloud, shadow, fill, snow and water were rejected. Pair selection used only the maximum overlap of QA-valid probes, with tie-breaking by nearest seasonal day and deterministic scene ID.

| Site | 2007/2008 pair with most shared QA-clear ground probes | Dates | Spatially identical sample coordinates |
| --- | ---: | --- | ---: |
| Litchfield, LITC | 25 early QA-clear / 7 late QA-clear | 2007-01-05 versus 2008-01-15 | **7/25** |
| Humble, HUMB | 0 prior QA-clear | no valid paired site grid | **0/25** |
| Torgersen, TORG | 17 early QA-clear / 3 late QA-clear | 2007-01-05 versus 2008-01-15 | **3/25** |

For Litchfield, matching fixed grid-point indices are **[9, 11, 15, 16, 20, 22, 23]**; Torgersen **[9, 12, 13]**. These counts identify *probes*, not distinct biological plots; native sensor pixel footprints can be offset across scene geometries even when the sampled physical location is fixed. All 54 image-pair rows, the 675 fixed sample-point QA records, individual source IDs and reading error reports are preserved in the linked artifact. The fixed pair rule was applied after all QA arrays were read; **no NDVI or surface-reflectance band was accessed**.

## Scientific decision

- **Resolved:** the late-summer 2008 source-wide cloud/QA gap is partly seasonal. January 2008 has original QA-valid land at fixed Litchfield and Torgersen ground points; 2008 March did not.
- **Still failed / unverified:** no authenticated 1998/99 geospatial historic sub-colony polygons and stable non-colony controls, no terrestrial plant classification, no temporal replica series, and no source-specific nutrient signatures. The 7 Litchfield ground probes are NOT verified historical nesting ground. No evidence yet that Litchfield greened *after* its 2007 census zero.
- **Operational next scientific gate:** get historic colony polygons from original field/GIS sources or georeference independent original nest maps with accuracy; then locate measured common QA ground points relative to polygon boundaries. Only after matching plots and enough repeated years should Landsat red/NIR values be extracted or greening inferential statistics fitted.

The corresponding executable code and offline deterministic tests reside at \`research/climate-penguin/work/abandonment/palmer_january_common_qa.py\`, \`tests/test_palmer_january_common_qa.py\`; independent original STAC code in the same folder. Frozen manuscript branches remain unchanged. This is a **post-exploration feasibility result** only.
