# South Orkney seal tracking source disposition (2026-11-24)

Decision: CLOSED_PUBLIC_RAATD_2016_SUPPORT. No spatiotemporal overlap calculation or ecological outcome model executed. Not an ecological null. V1/D1/D2 annual analyses remain closed. Keep frozen manuscripts and main unchanged.

## Verified execution receipts
- Filtered RAATD original archive MD5 168e5b9b5c4ed20bb84dd00145acb0a5, SHA256 0ae874dc75e36104dee26677fffdf402b13c008fdc2284f7fac7cda5e3f65c7a. Run 45383533760, artifact 14915775996, artifact digest sha256:711689aee9c835369f94a46e292110e21d79ffdbc9cb475bac2e1a36a2011fac. Strict cp1252 decode of RAATD_metadata.csv and UTF-8-sig of ANFS data succeeded; 313 unique IDs and 209472 filtered positions validated. Zero ANFS IDs in Jan–Feb 2016 / 58–63 S / 48–42 W. Deployment field mappings incomplete but immaterial to zero geographic/date support. Do not infer absence of animals.
- Publisher AntOBIS standardized DwCA v1.5 https://ipt.biodiversity.aq/resource?r=scar_raatd_trackingdata&v=1.5, source ZIP SHA256 b1f6e07dfa076008b29042b89153e2be3b1841bd0847144bc3abf9ec4d1acfe0. Run 45384387773, artifact 14915103736, digest sha256:29f5c6befc47b9f66363a0bd236a9a9acfded5300fd270825046c739de1df524. Read metadata and 4060 unique core events, 2331595 occurrences, 209785 A. gazella occurrences, 252 invalid date or coordinate rows, 209533 valid fixes, latest valid year 2015, zero target fixes/event IDs. Receipt status SOURCE_COMPLETENESS_REVIEW_REQUIRED (not a fully validated biological absence): cannot exclude a malformed record but no usable target support. Filtered and standardized forms are not independent cohorts.
- BAS GPS source collection independently pinned (canonical member content SHA256 e65a884341346a95ebb4a25de492d350716fde5f5cb77a669d66846811f6800a): 10 Adelie, 26 chinstrap, one gentoo unique deployments within same broad box Jan–Feb 2016. These are source-support counts, not necessarily simultaneous foraging individuals; no balanced gentoo contrast.

## Next input, not another model
Lowther et al. (2020) DOI 10.1038/s41598-020-75148-9 documents 20 male fur seals deployed on Powell Island 5–26 January 2016; public article and supplemental figures/tables found but no position-level data link located. Corresponding author official profile https://npolar.no/en/team/andrew-lowther/ lists professional contact. JR15004 cruise inventory https://www.bodc.ac.uk/resources/inventories/cruise_inventory/report/16040/ documents coordinated predator tracking, acoustic and ship observations. Cruise report table 13-20 indicates field parties held raw tracks; text extraction reviewed, page screenshot could not be fetched. Do not treat cruise navigation or CTD as animal positions. No verified public sighting-level file located. Request timestamped seal tracks (including error estimates, deployment metadata, dive data where available) from the original team. Existing Signy daily-count request remains a separate long-term input. No request sent by this repository action.

Retain fixed gate (>=5 common dates with >=3 independently tagged animals in each group and >=5 unique individuals per group across eligible dates). Require source stage/timezone/identity metadata, no selection by overlap direction. Stop if support fails. Same-day co-use cannot establish actual competition, causal effect of sea ice, or a warming trend. Additional prey data and comparable exposure windows would be needed.

## Draft request for original Powell Island telemetry (not sent)
Dear Dr Lowther,

I am working on an ecological analysis of marine predator co-use around the South Orkney Islands and read your 2020 Scientific Reports paper on male Antarctic fur seals (doi:10.1038/s41598-020-75148-9).

I have obtained the public BAS penguin GPS datasets from the 2015/16 breeding season, and checked the SCAR RAATD archive, but could not locate usable fur seal tracks for January–February 2016. Would the Powell Island telemetry records from the 20 males tagged in January 2016 be available for research reuse, or is there a repository or contact you recommend?

If feasible, I would be grateful for individual-level timestamped locations (raw Argos or the 2-hour state-space estimates, including uncertainty where available), deployment metadata, and dive summaries for the same dates. The aim is to assess same-date spatial co-use with the available penguin GPS tracks, while accounting for differences in sampling effort and breeding timing. I would not interpret overlap itself as evidence of competition. I would be happy to discuss data-use conditions, appropriate credit and potential collaboration.

Thank you for considering my request.

Best regards,
