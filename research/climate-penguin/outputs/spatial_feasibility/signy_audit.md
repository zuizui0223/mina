# Signy spatial feasibility audit (2026-10-29)

## Verdict

Colony-reference-point to vegetation linkage is **verified for all 14 penguin components** in the fixed 2012/13–2019/20 panel. GPS files were actually downloaded from original BAS attachments, not inferred from island centroids. This corrects any earlier statement that Signy colony coordinates were unavailable. Boundaries and penguin landing routes are not yet georeferenced, and no causal flight/predator effect is identified.

## Exact primary-source data

- Adélie: https://doi.org/10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d ; attachment `GPS Adelie Colony.csv`.
- Chinstrap: https://doi.org/10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9 ; attachment `GPS Chinstrap Colonies.csv`.
- Shag: https://doi.org/10.5285/ca60bfec-9070-4967-920e-0c42554ad649 ; attachment `Signy_map.pdf` visually inspected.
- UAV counts, actually downloaded: https://doi.org/10.5285/f3d9004a-e788-4104-a1a9-54fa80b533a1 .
- Public processed UAV photographs and mosaics: https://doi.org/10.5285/6f687000-8a7b-4207-9a5c-8d1429397c70 . RAMADDA exposes 2016_2017 and 2017_2018 folders and individual jpg/dng/count files.
- Survey methods: https://link.springer.com/article/10.1007/s00300-021-02831-6 . Important distinction: imagery GPS and recorded ground-control marks are not evidence that the public mosaics have a supplied GIS transform. The public metadata accidentally exchanges gentoo/chinstrap Latin names; use count CSV species and paper, not that metadata typo.

## Point crosswalk and vegetation join actually executed

`signy_gps_crosswalk.csv`: 5 Adélie components (A1+A60,A2,A3,A4,A64), all at North Point, and 9 chinstrap components (C15 Moyes Corrie; C16,C17,C18 Fyr Channel; C46,C47 Gourlay West; C79,C80,C81 Gourlay East). Exact textual ID matching, with spaces removed only. GPS instrument states Garmin GPS60 approximate accuracy20ft =6.096m; GPS coordinate measurement date is not supplied. These are reference points, not colony centroids or boundaries established by the source.

`signy_gps_vegetation_buffers.csv`: actual intersections at25,50,100,200m geodesic buffers with existing Plantarctica map in EPSG3031. Areas calculated back on WGS84 ellipsoid after clipping and union within each class. All14 points have mapped Vegetation within100m; Lichen absent within100m only for C16,C17,C18. No mapped polygon means unknown absence/coverage, not verified barren ground. Buffer area includes sea and is NOT a terrestrial percentage or colony vegetation cover. The product pools2017–2023 imagery, so it is not a2017 annual map and cannot yield annual greening or lagged feedback.

`signy_close_point_pairs.csv`: C16/C17 separated4.91m (less than nominal GPS accuracy and a10m vegetation pixel); A4/A64 16.23m; C16/C17–C18 approximately25m; C46/C47 35.51m; C79/C80/C81 approximately43–71m. Buffer overlaps and spatial autocorrelation rule out treating14 components as14 independent landscape replicates. Broad geographic groups number5, with species segregated at that group scale.

## Imagery and year audit

Fixed annual counts2012/13–2019/20 provide14 penguin components ×8seasons=112 component-seasons; the original matched panel adds2 shag areas ×8=16 more. Composite-period overlap2017/18,2018/19,2019/20 provides42 penguin component-seasons and6 shag-area-seasons, but only one vegetation composite.

2016/17 public UAV files: C16+C17+C18 on2016-12-12, C46,C47 on2016-12-12, C79,C80,C81 on2016-12-14. C15 is not included that season. These are filenames and count-date confirmations; not all raw images downloaded.

2017/18 public UAV files: C15; C16_C17; C46; C47; C79; C80; C81_C82; NorthPointShags; Shagnasty. Count dates: GourlayEast2017-12-12; FyrChannel andMoyes2017-12-18; GourlayWest2017-12-20; NorthPointShag2017-12-18; ShagnastyShag2017-12-20. C18 count=0 and no separate positive colony image identified. **C81+82 is pooled** in2017/18 counts and mosaic, so cannot silently match to long-termC81 alone. C16,C17 likewise share one image but retain separate census rows. Raw UAV counts and annual ground counts are different observations and must not be concatenated as duplicate years.

C79_GourlayNE.jpg actually downloaded and visually inspected: individual birds/nesting patch, guano/rock surface and orange/yellow lichen visible; no sea or landing shoreline in frame. CameraEXIF GPS exists, but this is not an image geotransform. C80/C81+82 mosaics downloaded; embedded cameraGPS persists in stitched JPGs, which must not be interpreted as geographic coordinates for every pixel. Image DateTime may be processing date, so survey CSV dates take precedence.

Shag map: one marker at NorthPoint, three at Shagnasty isletsI,II,III. This resolves approximate areas, not individual nests/annual boundaries. A coarse marker digitization cannot be presented with GPS precision.

## Penguin access: currently unresolved

No actual penguin landing coordinate or georeferenced path has been established in this audit. Human boat landings, drone takeoff pads, closest coast and coast-facing colony edges are not substitutes. The name PenguinHighway also is not proof: the British Antarctic Territory describes it as a demarcation between penguin colonies and fur-seal areas (https://www.britishantarcticterritory.org.uk/penguin-place-names/). Public UAV file `C48_PenguinHighway_stitch.jpg` is a colony photograph, not automatically a surveyed walking route. C48 is outside the fixed panel.

The public Signy tracking portal (https://signy.data.bas.ac.uk/) lists AdélieGPS2011–2016 and chinstrapGPS2011–2019; this is a promising independent source for shore crossing, but actual tracks and deployment-colony crosswalk have not been checked here. Merely having marine tracks does not establish land transit.

## Testable scope now

YES: compare historical abundance/change and mapped local vegetation association at identified fixed colony reference points, with site grouping and buffered-exposure sensitivity; use2017/18 public photographs to audit whether selected patches are visually identifiable. A useful pilot is C46/C47 and C79/C80, with exact IDs in both2016/17 and2017/18 imagery; C16/C17 must be grouped for exposure; C81 excluded untilC82 separation checked. These repeat images could examine within-patch concentration but need independent image registration and area calibration.

NOT YET: distinguish access-constrained nesting from vegetation-driven site selection, quantify walking distances from observed landings, measure occupied area change in square metres, or infer whether colonies caused vegetation. Both competing explanations need georeferenced boundaries, observed or validated landing points/routes, suitable unoccupied habitat, terrain/snow and independent vegetation timing. Flightlessness cannot be isolated from species and nest substrate with one flying taxon occupying cliff ledges, and predator absence has no variation within these sites. Signy is a conditional test setting without terrestrial mammalian carnivores, not a randomized predator-removal experiment or an ecosystem free of predators/disturbance (skuas, marine predation and fur seals remain relevant).


## Additional direct image inspection after download completion

All10 selected JPGs downloaded successfully; sourceURLs and exactbytes are in `work/spatial_feasibility/signy/downloaded_uav_manifest.json`.

- `C46_Lenton-Mid.jpg`: visibly labelled C46,2017-12-20. An occupied rocky nesting patch, patches of green cover/orange lichen, surrounding snow, and adjacent seawater/ice are all visible. This supports registering a breeding-patch boundary and nearby shoreline if external control can be obtained. It does **not** show repeated penguin use of any specific landing location; shoreline proximity is only an access proxy.
- `C48_PenguinHighway_stitch.jpg`: visibly labelled C48,2017-12-20. Two red outlines supplied in the original image enclose occupied nesting groups; a snow/ice-filled inlet separates portions. This is a useful visual example of local concentration near coast but C48 is outside the fixed annual panel, and the red outlines are not surveyed GIS polygons or animal-route annotations.
- `NORTHPOINT_Shags_Count.jpg`: an oblique image/screenshot of a steep rocky islet/ledge, labelled2017-12-18, with174 labelled nest points; sea surrounds much of the feature. It verifies the shag colony and strong nest-substrate differences. This image is unsuitable for direct planar area measurement without photogrammetric rectification; the screen display and counting overlay are not geospatial coordinates.

These inspections strengthen the spatial-pilot feasibility and simultaneously show why snow, rock architecture and image geometry must be handled before attributing differences to flight ability.

## Tracking follow-up: actual downloadable data confirmed

The earlier tracking-lead limitation is partially resolved. Direct RAMADDA access worked although the graphical portal timed out. Downloaded chinstrap V2 metadata, header and three GPS CSV samples from https://doi.org/10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92 . Local files are south_orkneys_chinstrap_tdr_gps_metadata.csv, sic_inventory.json, SIC007_29472_GPS.csv, SIC020_29421_GPS.csv and SIC132_14523_2375_GPS.csv.

- Metadata contains 132 Signy deployment rows; server exposes 121 Signy GPS files. These are not independent successfully tracked bird counts: failures and duplicate deployment names need reconciliation.
- Twenty Signy rows contain nest coordinates, all 2013/14. None of the 2018/19 deployments has nest coordinates. Location names state Signy or Gourlay, without fixed colony C-numbers.
- SIC007 (2011/12): 65 fixes; metadata explicitly says Never went to sea. Median interval 7199 seconds. Land-associated fixes are retained, but this individual cannot establish a shore crossing.
- SIC020 (2013/14): 1320 fixes; median interval 318 seconds; 15 fixes within 50 m and 22 within 100 m of the recorded nest. Offshore fixes are also present, so this is a candidate departure/arrival sequence. The nest is 230 m from the nearest fixed-panel reference point C47: nearest-point assignment is not an exact colony crosswalk.
- SIC132 (2019): 849 fixes, median interval 168 seconds, starts near Gourlay and later travels offshore; nest coordinate missing. This overlaps the 2018/19 count season, but cannot directly crosswalk to a C-number.

Thus public tracking is accessible and potentially useful, not access-blocked. No land/coast polygon overlay or repeated shore-crossing classification was performed here, so no verified landing coordinate or walking route is asserted. First classify land/sea with GPS uncertainty, identify repeated shore crossings, and connect terminal clusters to independently registered breeding polygons. Nominal four-minute sampling, with some much coarser intervals, cannot resolve every walking route. Tracking and UAV dates are not simultaneous: available Signy tracking includes 2013/14, 2015/16 and 2018/19, versus selected UAV images 2016/17 and 2017/18.
