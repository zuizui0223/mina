# CMIP6 data citation mapping

Checked: 2026-11-06.

## Outcome

All nine frozen stores have an official, verified experiment-level ESGF data DOI. Use the nine experiment citations in CMIP6_CITATIONS.csv and retain each analysed member, variable, grid and original store version in Table S6. This is a citation/provenance task; it introduces no new climate extraction, model fit, or analytical gate.

## Source of truth

- Input manifest: `research/climate-penguin/outputs/diet_niche_manuscript_v1/CMIP6_SOURCE_STORES.csv`.
- SHA-256: `c71b4f19c3f8bcd402645be27e593afba4e94391f622aa3bebd2ffa89459e694`.
- Creator names, title, publication year, publisher, experiment scope, and parent DOI: the individual [DataCite registration records](https://api.datacite.org/dois/10.22033/ESGF/CMIP6.4271), linked per row in the CSV and reproduced as selected metadata in the JSON.
- Additional official citation cross-check: [WCRP CMIP6 experiment citation table](https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_source_id_experiment_citation.html) and [DKRZ experiment data references, 2021-03-09](https://redmine.dkrz.de/projects/cmip6-lta-and-data-citation/wiki/CMIP6_Data_References_-_Experiment). All nine model/activity/experiment/DOI mappings agree.
- The original CERA links resolve to the dedicated WDCC CMIP6 citation pages; these are linked per row in the CSV.

## Citation, member and version mapping

| Model | Experiment | Member used | Source version used | Creator and citation year | Selected experiment DOI |
| --- | --- | --- | --- | --- | --- |
| ACCESS-CM2 | historical | r1i1p1f1 | v20200817 | Dix et al. (2019) | [10.22033/ESGF/CMIP6.4271](https://doi.org/10.22033/ESGF/CMIP6.4271) |
| ACCESS-CM2 | ssp245 | r1i1p1f1 | v20200817 | Dix et al. (2019) | [10.22033/ESGF/CMIP6.4321](https://doi.org/10.22033/ESGF/CMIP6.4321) |
| ACCESS-CM2 | ssp585 | r1i1p1f1 | v20210317 | Dix et al. (2019) | [10.22033/ESGF/CMIP6.4332](https://doi.org/10.22033/ESGF/CMIP6.4332) |
| BCC-CSM2-MR | historical | r1i1p1f1 | v20200218 | Wu et al. (2018) | [10.22033/ESGF/CMIP6.2948](https://doi.org/10.22033/ESGF/CMIP6.2948) |
| BCC-CSM2-MR | ssp245 | r1i1p1f1 | v20200219 | Xin et al. (2019) | [10.22033/ESGF/CMIP6.3030](https://doi.org/10.22033/ESGF/CMIP6.3030) |
| BCC-CSM2-MR | ssp585 | r1i1p1f1 | v20200219 | Xin et al. (2019) | [10.22033/ESGF/CMIP6.3050](https://doi.org/10.22033/ESGF/CMIP6.3050) |
| CESM2 | historical | r4i1p1f1 | v20190308 | Danabasoglu (2019) | [10.22033/ESGF/CMIP6.7627](https://doi.org/10.22033/ESGF/CMIP6.7627) |
| CESM2 | ssp245 | r4i1p1f1 | v20200528 | Danabasoglu (2019) | [10.22033/ESGF/CMIP6.7748](https://doi.org/10.22033/ESGF/CMIP6.7748) |
| CESM2 | ssp585 | r4i1p1f1 | v20200528 | Danabasoglu (2019) | [10.22033/ESGF/CMIP6.7768](https://doi.org/10.22033/ESGF/CMIP6.7768) |

## DOI granularity

Each selected DOI describes all published datasets for one exact CMIP6 activity/institution/model/experiment prefix. The DataCite abstracts explicitly extend this prefix with member_id, table_id, variable_id, grid_label and version. Thus these are experiment collections, not member-, variable-, or individual-file DOIs.

The parent records below are broader model-by-activity collections. They are retained to explain hierarchy, not substituted for the selected experiment citations.

| Model | Activity | Parent collection DOI |
| --- | --- | --- |
| ACCESS-CM2 | CMIP | [10.22033/ESGF/CMIP6.2281](https://doi.org/10.22033/ESGF/CMIP6.2281) |
| ACCESS-CM2 | ScenarioMIP | [10.22033/ESGF/CMIP6.2285](https://doi.org/10.22033/ESGF/CMIP6.2285) |
| BCC-CSM2-MR | CMIP | [10.22033/ESGF/CMIP6.1725](https://doi.org/10.22033/ESGF/CMIP6.1725) |
| BCC-CSM2-MR | ScenarioMIP | [10.22033/ESGF/CMIP6.1732](https://doi.org/10.22033/ESGF/CMIP6.1732) |
| CESM2 | CMIP | [10.22033/ESGF/CMIP6.2185](https://doi.org/10.22033/ESGF/CMIP6.2185) |
| CESM2 | ScenarioMIP | [10.22033/ESGF/CMIP6.2201](https://doi.org/10.22033/ESGF/CMIP6.2201) |

## Version and member handling

The original member is r1i1p1f1 for ACCESS-CM2 and BCC-CSM2-MR, and r4i1p1f1 for CESM2. All original source columns are copied unchanged. The complete source DRS is included in the CSV and checked against each official experiment prefix. The DOI supplies the collective experiment citation; the frozen source manifest supplies the selected member and exact SImon/siconc/gn store.

The CERA citation template includes an explicit Version YYYYMMDD field and explains that CMIP6 collections evolve. Here the citation version is the actual archived source path used by this analysis, not a newly retrieved provider version. For example, ACCESS-CM2 ssp585 remains v20210317; CESM2 historical remains v20190308. Current DataCite records report 20250528 (most rows) or 20250527 (CESM2 scenarios). Those record-level values are stored in a separate column and do not replace the analysed versions.

This establishes citation-level correspondence. The task did not re-download model arrays, independently re-test every provider file, or claim byte-level identity between GCS and a WDCC/IPCC archival replica. No new analysis is required by this citation task.

## Corrections and distinctions for the manuscript

1. BCC-CSM2-MR historical is Wu et al. (2018); ssp245 and ssp585 are Xin et al. (2019). Do not assign the historical author/year to the future experiments.
2. The DRS source_id is BCC-CSM2-MR; the registered titles spell the model BCC-CSM2MR. The CSV preserves the official title and the source identifier separately.
3. Full author lists follow the current DataCite registrations, including Bi, Daohua and Domingues, Catia M. The 2021 DKRZ table contains older spellings (Doahua and Catia); these are retained only in provenance evidence.
4. The selected 10.22033/ESGF/CMIP6 DOIs cite the original model experiment outputs. Separate 10.26050/WDCC/AR6 DOIs identify IPCC DDC archives. They are not used here because the analysed sources are the frozen GCS stores. For example, the [CESM2 ssp245 WDCC archive](https://www.wdc-climate.de/ui/entry?acronym=C6SPNRCESs245) has a 2023 archive citation; it does not replace the verified 2019 ESGF experiment citation.

## Verification performed

- Nine input rows map one-to-one to nine output rows and nine distinct experiment DOIs.
- All input source fields, including GCS path, member and store version, are preserved.
- All nine citations match DataCite plus the WCRP and DKRZ experiment reference tables.
- Six parent DOIs were read separately and verified as broader model-by-activity collections.
- No commits, publication, new scientific analysis, manuscript author edits, or source data changes were made.
