# V12 independently digitized 2011 same-scene polygon: pre-schema contract

Before looking at the historic GIS geometry or original DBF coding, the authentic BAS `layer_descriptions.csv` reports `mac_and_chinstrap_colony_boundaries_2011` as a distinct Heather Lynch digitization published in Lynch et al. 2016, Polar Biology 39:1615–1625, using 2011 imagery. It is **not an independent observation date or independent experiment**, but may independently audit human interpretation/label boundaries on the same image.

Frozen objective: compare each species' original Lynch 2011 mapped polygon with the recently supplied 2011 species-specific polygon for co-registration, Jaccard area overlap, and the V10 2011→2016 transition E under alternate 2011 digitization. Restrict both to the documented cloud-free 2011/2016 footprint; don't change 2016 map or gain/loss definitions. Report both estimates even if the earlier one reduces the apparent overlap. No causal inference, competition or social information claims.

**Stage A only:** inspect original source DBF header (field names, types, number of records) with strict source name and SHA256; do not read original DBF row values or SHP geometries. If coding is ambiguous or appears to be mixed-species within a single polygon, stop and document. A species value crosswalk must be justified by data dictionary or clear original labels before inspecting geometry.

All original satellite-derived 2011 and 2016 maps remain under source DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308. The 2011 historic boundaries are prior art: their existence is not a discovery.
