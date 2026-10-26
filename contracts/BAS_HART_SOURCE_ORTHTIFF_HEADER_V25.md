# V25 bounded first-party UAV GeoTIFF metadata-only source check

**2026-10-26, post-V21/V22 ecology exploratory.** First-party BAS Hart original source archive DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b. Original V23/V24 proved the four nest-coordinate study localities have 100 TIFF files in the publisher archive, with filename date markers ASHE 05JAN2019 and BELG/BEAC/HEWI 09JAN2020. File labels do NOT prove original nest acquisition dates or source-common survey footprint.

Read at most **128 KiB** of response body via explicit HTTP `Range: bytes=0-131071` from exactly four V24 predefined representative original image files, one per locale:
- `Ashen_Hills/tiff_images/ASHE_05JAN2019_tile1.tif`
- `Bellingshausen/tiff_images/BELG_09JAN2020_TIF.tif`
- `Beach_Point/tiff_images/BEAC_09JAN2020_TIF.tif`
- `Hewison_Point/tiff_images/HEWI_09JAN2020_tile1.tif`.

Original V16 real publisher manifest provides exact source-ID-backed HTTPS URLs; do not invent locations. If the server does not return **206 Partial Content** with a valid Content-Range prefix starting byte 0, record **SOURCE_RANGE_UNAVAILABLE** and stop; never fetch the entire TIFF. Inspect TIFF IFD tags (image dimensions and optional GeoTIFF model pixel scale, tiepoint and geokeys) from only the bounded byte span. A missing original projection or georeferenced bounding tag results in **SOURCE_GEOREFERENCE_UNVERIFIED**, never inferred CRS or spatial footprint.

Even if one representative GeoTIFF has trustworthy georeferencing, that does NOT verify the whole mosaic's survey/search mask, original photo time, or whether every species was annotated in the same set of images. To claim surveyed-absence and habitat patch accessibility, require original complete multiframe field polygon footprints and a documented common search effort for each species. V25 cannot be used to rescue a specific species-island ecological effect, fit another model, or claim interspecific competition.
