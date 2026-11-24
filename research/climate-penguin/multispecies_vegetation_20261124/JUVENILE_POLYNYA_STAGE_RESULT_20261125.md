# Juvenile body mass and winter coastal polynya — original source recovered, 2026-11-25 JST

Executed locally after user supplied the original Dryad download. Hinke et al. (2020), DOI 10.1098/rsbl.2020.0645, data DOI 10.5061/dryad.2v6wwpzkh, CC0. Outer ZIP doi_10_5061_dryad_2v6wwpzkh__v20201120.zip SHA256 e05d7e20d46e4a943ff2ad0cfbfed6b8a454efd33e1061916bea07089f3e9a2e; inner FledglingBottleneck_Data.zip 99827 bytes, SHA256 84e8a4ddd736dfcbb8050b38a4391714b7a283f3b00d42afef1f84f4d0b49df8 exact match to previous official publisher metadata. Both CRCs pass. Eight CSV and README inspected. Original all-species mass rows 14198 (ADPE 5831, CHPE 4942, GEPE 3425), 76 species-colony-years (32,23,21); actual row counts differ slightly from published prose. Recruitment index 113 rows. Banded Adélie 3840 rows, 3837 unique year/ID (433 reobserved), three duplicate IDs with conflicting weights but agreeing RECRUIT; average for descriptive band-cohort weight, not an individual-level outcome fit. Carcass/chick counts 19 years (1997–2019 with missing years), actual count ratios verified against published numeric column. README: YEAR = end year of austral summer, RECRUIT = observed at age >=1 vs never reobserved, not true survival or actual entry to breeding population. Gentoo age-standardized weight and chinstrap departure weight are different measurement endpoints.

Original-source-derived exposure archives 13669533413 SHA256 add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a, 14926710177 b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8, 13829236358 64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5 all reopened, hash/CRC checked. Exact colony-year join via candidate atlas centre, geodesic distances ADB LLAN .332km, PTHO 1.736km, CAS SHIR .309km. Join P June-Oct of YEAR-1; hydro Aug-Nov YEAR-1. ADB alternatives never treated as independent data. No observation in missing winters 2003/2011/2012.

## Primary exploratory Cape Shirreff paired weight contrast

12 exact common years (2005–08, 2010–11, 2014–19 end-year labels); 2424 CHPE and 1662 GEPE observed weights. Equal-year OLS of log(mean gentoo grams) minus log(mean chinstrap grams) on native P100 percentage points and centered year. Separate matching species slopes on identical 12 years: CHPE -.000360951, GEPE -.029228211, contrast -.028867260. Within-trend partial R2 .418341. P100 range 0–6.590138 pp, SD 2.056954 pp; after full covariate adjustment identifying SD only .747638 pp. No extrapolation.

| Contrast sensitivity | n | beta | Leave-one-year range |
|---|---:|---:|---:|
|mean mass, P100 + time|12|-.028867|[-.036828,-.013516]|
|mean mass, P25 + time|12|-.032283|[-.037828,-.011514]|
|mean mass, P100 + time/SIC/SSS/SST|12|-.020933|[-.041001,+.005275]|
|mean mass, P25 + time/SIC/SSS/SST|12|-.018003|[-.089889,+.000552]|
|median mass, P100 + time/SIC/SSS/SST|12|-.023847|[-.039674,-.005455]|
|adjacent actual-year first differences, mean mass P100|9|-.015524|not used|

Full covariate model residual df6, P100 partial R2 .096092; no claim of robust independent physical effect. Deletion range is not CI, no p-values. One locality, two species, and different measurement timing. Direction differs from earlier gentoo-positive associations for other outcomes/species/regions; cannot claim proven life-stage tradeoff. ADB Adélie mean mass +.009040 (LLAN, 11 years, time-adjusted), deletion crosses zero. 

## Stage bridge and limits

CAS recruitment index paired contrast GEPE minus CHPE, 10 complete years, trend-adjusted P100 +.002741, deletion [-.019939,+.010886]; full controls df4 insufficient (minimum 5). ADB paired index 7 years, trend model df4 not fitted. Banded Adélie 6 complete years, 505 unique observed individuals/102 reobserved; trend+P df3 not fitted. Common CAS mass/index paired years n18; trend-adjusted index difference vs log mass ratio +.012915, year deletion [-.242331,.231874]; restrict to nine complete P years +.219490, deletion [-.655611,.480860]. No supported relative mass-to-index bridge. Separate CAS species associations on broader common mass-index years: CHPE +1.256214, n20, deletion [1.016861,1.565009]; GEPE +.719957, n18, deletion [.606372,.837734]; these use different years and cannot prove differential mechanism or mass mediation. 

Secondary CHPE observed carcass/chick ratio (not mortality probability): 13 years, trend-adjusted log ratio P100 -.129476, deletion [-.218725,-.025449], full controls -.269832, deletion [-.507761,-.157949]; P25 time-only omission changes sign. No predation attribution, no new inference that bodies not seen imply survival.

## Reproduction and disposition

All 76 annual source means independently verified with stdlib statistics, max difference 0; all 463 fitted coefficient checks via QR/FWL vs direct least squares max error 3.073e-14. Arithmetic reproduction, not ecological replication. Local result archive juvenile_polynya_stage_results_20261125.zip SHA256 a26b003b182facab03989a0d023d39ab76ba245ed92e4656a8e0a05d5044079f; executed analyze.py 203262f41f41c1e8223f55c2e86b53454153eb21f1e82d66f6c83acb4b97934c, verify_stage_bridge.py e189f5f1aaf0b3e8307541192c695968075e9d7c01ed39b9dedeb59d5d995b4b. 20 files include annual inputs/outputs, paired contrasts, all omissions, receipts and code. No original source or individual ID rows republished. Previous main/frozen papers unchanged. Do not tune more radii/lags or fit saturated survival models. Preserve measured weight contrast and distinct lack of a supported recruitment bridge, and prioritize independent matched long-term life-stage series if pursuing mechanism.