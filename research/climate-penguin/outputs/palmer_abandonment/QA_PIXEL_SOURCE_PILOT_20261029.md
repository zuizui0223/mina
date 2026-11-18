# Palmer original QA_PIXEL measured source pilot and next observation window

**Measured source results, not inferred vegetation change.** Run [40859343220](https://github.com/zuizui0223/mina/actions/runs/40859343220) read 30 actual local QA_PIXEL samples (3 Palmer site-centroid grids × 4/1/5 original Landsat scenes in February–March 2007/2008/2012) without asset read errors. Five-by-five fixed 40 m grid points within ±80 m in EPSG:3031 were sampled at Landsat source native resolution, not colony polygons. Original artifact: **12890413153**. ZIP SHA-256: \`00d57dc48769a4b4362e92838639379a928a59b1c3299ad20f139702b995f11b\`. Original \`local_qa.csv\` SHA-256 \`464b1aefece9f705b53ee30ffc12b61b7b0e15bcb8c092c407f64b94ac586163\` and \`checks.json\` SHA-256 \`910070559821d596d5b967feb4f7661d1f43fee36c8b711d2c24524a8c609928\`.

Values are the *maximum number of QA-clear, non-water, non-snow, non-cloud/shadow pixel samples in any single acquired scene*, out of up to 25 unique point-neighborhood native pixels:

| Site | 2007 Feb–Mar, 4 scenes | 2008 Feb–Mar, 1 scene | 2012 Feb–Mar, 5 scenes |
| --- | ---: | ---: | ---: |
| Litchfield | **11** (2007-02-22) | **0** | **15** (2012-02-20) |
| Humble | 1 | 0 | 0 |
| Torgersen | 0 | 0 | **12** (2012-02-20) |

The one 2008 image, 2008-03-10 (\`LE07_L2SR_220105_20080310_02_T2\`, scene-global 94% cloud), yielded *zero locally QA-clear pixels in all three fixed neighborhoods*. All 9 source image×site reads (and 30 source records across years) succeeded; 2008 is **observationally uninformative under this window and source**. One may not infer zero land, zero moss, or no vegetation greening. The 2007 and 2012 QA-clear pixels need not be the same physical footprints or stable colony/subcolony plots; source geolocation and valid-land masks must be checked before spectral comparisons. Existing 2019/2024 January Sentinel common pixels at Litchfield were also zero in the earlier source audit, a different comparison.

## Post-hoc observational rescue (no greening outcome looked at)

Because the predefined February–March 2008 window failed actual local pixel support, additionally inspect **January 2007 and January 2008** as a source-only diagnostic. January 2008 is still the 2007/08 first observed-zero breeding season; January 2007 belongs to the 2006/07 last-positive season. This is **post-hoc scene-quality feasibility**, not a confirmatory replacement for the original fixed seasonal window. Any later plant-trend analysis must use comparable calendar windows across all included pre/post years and cannot choose dates using NDVI signs.

All January original source queries, asset read failures, QA and summary are retained in a separate artifact. The historic colony polygon crosswalk remains unverified and independently required. Avoid using site centroids or 2km plant-detection buffers as the colony footprint.

Primary source QA flag interpretation: USGS Landsat C2 QA_PIXEL bits 0 fill, 1 dilated cloud, 3 cloud, 4 shadow, 5 snow, 7 water; \`clear\` bit 6 alone should not be trusted on some historic Landsat4-7 scenes (known issue). Original Landsat7 SLC-off gaps are masked as missing.
