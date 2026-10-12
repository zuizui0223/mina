# V5: Live publisher archive access check — 2026-10-12

Direct public browser retrieval succeeded for:
- https://data.bas.ac.uk/full-record.php?id=GB%2FNERC%2FBAS%2FPDC%2F02256
- https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=7220dc6b-2f52-4160-a6c0-e57c50963308
- https://ramadda.data.bas.ac.uk/repository/a/GB-NERC-BAS-PDC-02256

The first is the full official metadata; the second and third resolve to the live UK Polar Data Centre archive entry titled "Mapping of higher predators from aerial and satellite imagery on Zavodovski Island, South Sandwich Islands, 2010 to 2025". The archive page confirms server-side files and OGL-UK-3.0, but **the browser's extracted page text and outbound-link listing do not expose individual file download URLs**, including layer_descriptions.csv. This is an *archive navigation/documentation retrieval HOLD*, not proof that the CSV is missing or that the 34 MB dataset is inaccessible. No archive bytes or colony geometry have been retrieved.

Official full-record metadata specifically calls layer_descriptions.csv an 8 KB data dictionary and validation.csv a 4 KB classifier validation file; 28 shapefiles and associated files total 34 MB. The record explicitly says cloud-obscured regions were substituted with polygons from the closest visible different-year image. No per-feature provenance masks have been verified.

Next action: use a real browser file-list/download interaction or request the 8 KB dictionary from UK PDC custodians, **without opening biological polygon layers**, then classify whether the original image date and substituted footprint are documented at feature/region resolution. Do not invent a direct CSV URL, use a page-level date as feature-level provenance, or claim any biological result.

PR189 scientific endpoints remain frozen.
