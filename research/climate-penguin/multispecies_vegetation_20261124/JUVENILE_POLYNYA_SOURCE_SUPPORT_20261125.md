# Juvenile stage and winter polynya: exact source and exposure support audit, 2026-11-25 JST

Executed geographic/calendar linkage, not a biological outcome reanalysis. Source Hinke et al. 2020, DOI 10.1098/rsbl.2020.0645; [Dryad](https://doi.org/10.5061/dryad.2v6wwpzkh), [NOAA parent](https://www.fisheries.noaa.gov/inport/item/63282), [weight](https://www.fisheries.noaa.gov/inport/item/63288), [banded weight and reobservation](https://www.fisheries.noaa.gov/inport/item/63289), [cohort index](https://www.fisheries.noaa.gov/inport/item/63290), [carcass count](https://www.fisheries.noaa.gov/inport/item/63287). [Published supplement](https://repository.library.noaa.gov/view/noaa/53433/noaa_53433_DS2.pdf) text inspected; screenshot cache miss, no figure digitization. 

## Original file retrieval verdict
Official API dataset metadata SHA256 b68d8cafc8a720fdd08c22f5758d2a0cf543fe16fb04b7f7b98bcbe133734ac7, version 106988, version file list SHA256 dab0720239859a721f2a0b4c1b315900cbb4e46912c6e25cc5093277eb43120a. File 489106 (original version link 92658), FledglingBottleneck_Data.zip, 99827 bytes, publisher SHA256 84e8a4ddd736dfcbb8050b38a4391714b7a283f3b00d42afef1f84f4d0b49df8, CC0. API file endpoint 401 in [run 45422558997](https://github.com/zuizui0223/mina/actions/runs/45422558997), corrected public routes all 403 in [run 45422720264](https://github.com/zuizui0223/mina/actions/runs/45422720264). Both acquisitions failed; no original ZIP, no fitted outcomes. Stop repeating blocked routes. 

## Executed WGS84 source-centre proximity and exposure sensitivity
Local original-source archives 13669533413, 14926710177, 13829236358 match GitHub artifact SHA256 values add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a, b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8, 64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5; ZIP CRC verified. Metadata coordinates match nearby atlas centres, not necessarily identical monitoring footprints.

|NOAA locality|Atlas candidate(s) and geodesic distance km|
|---|---|
|ADB (-62.175,-58.44)|LLAN 0.331853; PTHO 1.736089|
|CAS (-62.46,-60.79)|SHIR 0.309259|
|ESP (-63.4,-57.01)|HOPE 0.685000|
|CRV (-64.14,-60.984)|PING 0.398859 (CHPE); CIER 2.226236 (GEPE); KAYR 2.851319 (CHPE)|

Candidates within 3 km retained, not relabelled as observed colony identity. On all 15 complete winters ADB LLAN/PTHO P100 r=.999862, mean/max abs difference .033001/.092423 pp; P25 r=.999694, mean/max .089403/.405700 pp. CRV PING/CIER P100 r=.999975, mean/max .019757/.063317 pp; P25 r=.998768, mean/max .329849/1.061980 pp. Strong exposure similarity does not resolve source identity or justify two independent samples. Candidate-centre exposure, not newly extracted exact NOAA coordinates.

## Year mapping and maximum potential support
NOAA YEAR explicitly denotes austral season end year. Match June-Oct P from YEAR-1, not YEAR. Published supplement: ADB Adélie weights 5833 over 34 years 1982–2019; CAS chinstrap 4942 over 23 years 1997–2019; CAS gentoo 3427 over 21 years 1998–2019. Gentoo measurement standardized age 85 days from median laying date, not departure. Published banded weighed Adélie cohort 3909 in 1981–2010, 446 later reobserved; InPort entity description gives differing range 1997–2019, resolve with original raw file, use analyzed original paper range for conservative support. Return to natal colony is not true survival or entry into breeding population. Cohort index adjusted for likely band loss; not binomial data without counts. Carcass ratio not mortality probability. Satellite tracking stops may be tag failure.

Potential year intersections only, not observed join counts: each main mass series at most 13 (2005–11, 2014–19), published banded mass/reobservation window at most 6 (2005–10), cohort index through 2016 at most 10 (2005–11, 2014–16), carcass/chick ratio through 2018 at most 12. No imputation across the missing 2003/2011/2012 winter records. Source metadata vs paper years require verification. Next model after raw receipt: equal-year annual mean weight within species/locality, same-year CHPE/GEPE comparison at CAS if support permits, P100 and trend, P25 fixed sensitivity; cohort-level reobservation with follow-up audit, not thousands of independent climate replicates. No new claim of known mass-return relation, no full model with insufficient df, no demographic forecast or mediation.

Local reproducibility bundle juvenile_polynya_source_support_20261125.zip SHA256 981f2ea798d26bb9b84b5abcc997b5f12891ce2bed2023a2a2423aa5afb5e2ad; executed audit_geo.py SHA256 82e6d164471cacf9e498bf0b1bbeff607afe624ccb106c472e492113aca8081d, four CSVs and README. Public source metadata and physical results only; no restricted source published. Main and frozen manuscripts unchanged.
