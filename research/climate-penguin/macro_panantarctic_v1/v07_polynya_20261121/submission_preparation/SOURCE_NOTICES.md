# Source notices and dataset citations

Prepared 21 November 2026 for the v0.7 polynya manuscript and its compact derived-data reproduction package. Provider observations were checked against source commit `7867969c640e9e1fce627ed0e172e549fb6b4f0f`. Exact retrieval fields, response hashes and package inventory are recorded in [SOURCE_REUSE_REGISTER.json](SOURCE_REUSE_REGISTER.json) and [provider_metadata_receipt.json](evidence/provider_metadata_receipt.json).

These notices identify the sources and transformations of supplied derived values. They do **not** place a new licence on third-party data, the combined package, or project-created scripts. The rights holder's code-licence choice remains pending in the author preparation process.

## 1. Optical observations and calibration

**Dataset citation:** Youngflesh C (2025) *Data for Youngflesh et al. Submitted*. Zenodo. https://doi.org/10.5281/zenodo.17409948.

**Verified source licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. The DOI's DataCite registration supplies the creator, title, issue date of 21 October 2025 and licence. It gives no separate version label; the exact deposited record is identified by the DOI. The dataset title and year are retained as registered. They differ from the subsequently published Youngflesh et al. (2026) journal article, which remains separately cited in the manuscript.

**Changes made:** The project selected the documented quality-flagged image pixels, matched colony identifiers, reconstructed optical isotope values, gave observed image days equal weight in seasonal aggregation, and examined calibration splits. The package supplies derived seasonal proxies, calibration coefficient ensembles and iteration-level validation summaries. These outputs are not direct chemical measurements at every colony-season and are not the published multistage diet posterior.

The original reflectance RDS, individual laboratory isotope/spectral observations and complete original provider archive are not included in the compact package. No endorsement by the source author or article authors is implied. Source CC BY terms apply to covered source material; they do not automatically license this project's independently created analysis scripts.

## 2. Coastal-polynya exposure

**Dataset citation:** Lin Y, Nakayama Y, Liang K, Huang Y, Chen D, Yang Q (2024) *Daily Edge of Each Polynya in Antarctic (DEEP-AA)*. Version 1.1.0-2023. Zenodo. https://doi.org/10.5281/zenodo.13358042.

**Verified source licence:** CC BY 4.0, https://creativecommons.org/licenses/by/4.0/, as specified by the version-specific Zenodo record. This is the **dataset's** licence, distinct from the licence of the associated Scientific Data article.

**Source file:** The recommended `SIC60_6.25km_20d.zip`; provider MD5 `f3f958389cc5e67ac1c4e3a6ee164318`.

**Changes made:** The project aggregated positive even coastal-polynya IDs inside colony-centred geodesic buffers, corrected native-pixel area distortion, calculated area fractions using the documented marine denominator, applied monthly coverage requirements, and averaged June–October monthly exposures. The compact package retains daily/monthly/winter derived fractions and geography summaries. The 25-km tables are provenance/QA; the frozen ecological inference uses 100 km. Original daily grid files are not included. No source-author endorsement is implied.

## 3. Historical sea-ice concentration

**Dataset citation:** Meier WN, Fetterer F, Windnagel AK, Stewart JS (2021) *NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 4*. [Data set]. National Snow and Ice Data Center, Boulder, Colorado, USA. https://doi.org/10.7265/efmz-2t65.

**Subset and processing:** Historical version 4 values were aggregated over November–February, using the documented approximation based on native pixel centres within 150 km of source colonies. Derived seasonal values occur in the joined 860/358 tables. Original NSIDC grids are not included. The historical version is retained for reproducibility; a current product version has not been substituted.

**Observed source conditions:** The exact version-4 landing page requires data citation. Its official `G02202.004` DIF record reports retirement and points prior/planned uses to the citation policy. The retrieved DataCite registration supplies no rights entry. Accordingly, this register records the v4-specific redistribution licence as **not established from the retrieved metadata**, without assigning CC0 or another licence inferred from newer products.

Official policies: https://nsidc.org/about/data-use-and-copyright and https://nsidc.org/data/data-policies. The general data policy distinguishes broadly accessible/public-domain holdings from data carrying specific restrictions; it is not blanket evidence of a version-specific licence for every NSIDC product. The current manuscript's historical data citation and provenance must travel with these derived values.

## 4. Ocean reanalysis

**Product citation:** *Global Ocean Physics Reanalysis*. E.U. Copernicus Marine Service Information (CMEMS), Marine Data Store. Product `GLOBAL_MULTIYEAR_PHY_001_030`; GLORYS12V1 release 202311 used in this study. https://doi.org/10.48670/moi-00021. Product citation and terms verified 21 November 2026.

The release identifier is provided to identify the used data; it is not presented as the publication year of this evolving product. The Lellouche et al. (2021) scientific-method reference remains a separate citation.

**Publication credit:** This study has been conducted using E.U. Copernicus Marine Service Information; https://doi.org/10.48670/moi-00021.

**Derived-table credit:** Generated using E.U. Copernicus Marine Service Information; https://doi.org/10.48670/moi-00021.

**Source terms:** https://marine.copernicus.eu/user-corner/service-commitments-and-licence. The English Marine licence permits derivative creation/distribution and original redistribution under its conditions (Annex 2.2). It specifies service credit and product DOI (2.4), and maintenance of traceable use records (2.6). These conditions are retained by reference; no alternative licence is assigned to original Copernicus material.

**Changes made:** The project matched colony coordinates to validated wet grid cells within 25 km and aggregated surface practical salinity and potential temperature over November–February. Seasonal values and source-cell indices are supplied in joined tables. Original global reanalysis grids are not included.

## 5. Map context and complementary datasets

### Natural Earth land

**Source:** Natural Earth, 1:110m land geometry; principal authors named by the provider are Tom Patterson and Nathaniel Vaughn Kelso. Public domain under https://www.naturalearthdata.com/about/terms-of-use/.

**Included files and changes:** `ne_110m_land.geojson` is the raw generalized land layer pinned to Git blob `04811d72fff2701ec67587e30ad8942675b511e3` in `nvkelso/natural-earth-vector`. `antarctic_land_EPSG3031.json` is the documented southern display projection. The map's pale land layer supplies geographic context; it is not the exposure mask or the source of colony locations. Detailed geometry handling and checksums remain in `source_manifest.json`.

### BAS Signy diet observations

**Dataset citation:** Dunn M, Waluda C, Adlard S, Lynnes A, Morley T, Fox D (2022) *Annual samples and measurements of diet composition of Adelie penguins at Signy Island, from 1997 to 2020.* Version 1.0. [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/eb421e6d-b93b-4174-904b-9a7b0b401403.

**Verified terms:** The exact dataset page, https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01549, states Open Government Licence v3 and no access restrictions. Licence: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/.

Supplement S4 reports the project's aggregation/matching check and its inconclusive outcome. The compact reproduction package does not include the raw stomach-content table or executable reconstruction of that auxiliary check. Source period in the dataset title and the project's actually retained 2002–2020 sample are deliberately distinguished.

### Amino-acid and bulk feather isotopes

**Dataset citation:** Michelson C, Emslie SD, Hart T, McCarthy M, McMahon K, Patterson W, Polito M (2026) *Bulk tissue and amino acid stable isotope values of modern and historical Adélie penguin (Pygoscelis adeliae) feathers from the Ross Sea and Antarctic Peninsula regions (1840s to 2010s).* Version 1. U.S. Antarctic Program Data Center. https://doi.org/10.15784/602094.

**Verified terms:** CC BY 4.0, https://creativecommons.org/licenses/by/4.0/, explicitly reported by https://www.usap-dc.org/view/dataset/602094. Creator ordering above follows the dataset's supplied citation, rather than substituting the associated paper's author order.

The compact package reports the geographical and temporal matching audit; it does not contain the 108-row feather source table or claim an independent matched trophic-position validation. If that table is later redistributed, retain the dataset attribution, licence and transformation description.

### Reaves chick-bone context

**Dataset citation:** Reaves M, Powers S, Emslie SD (2025) *Stable isotopes of Adelie Penguin chick bone collagen*. Version 1. U.S. Antarctic Program Data Center. https://doi.org/10.15784/601913.

**Verified terms:** CC BY 4.0, https://creativecommons.org/licenses/by/4.0/, explicitly reported by https://www.usap-dc.org/view/dataset/601913.

This dataset's metadata informed the literature comparison. The compact package does not redistribute its chick-bone table. The manuscript cites the associated Reaves et al. (2025) article for its scientific findings.

## Remaining scope of the package

The notices above describe the sources represented in the compact v0.7.1 reproduction materials and cited auxiliary checks. The four small ZIPs contain 24 members and supply the inputs for reproducing the frozen 439/358 model results and five main figures. They do not reproduce the complete satellite ingestion chain, the original authors' full model, or all S4–S6 auxiliary workflows. Selected census/CMIP6 accounting in S6 remains linked to its historical repository provenance, with no original census or CMIP6 archive added to this compact package.

Final archival metadata should retain this source-level distinction, select a licence only for material the depositor has authority to license, and cite the final code/archive identifier once assigned. No DOI publication or new project licence is asserted here.
