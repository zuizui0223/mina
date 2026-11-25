# Same-place Adélie–gentoo comparison: executed result (2026-11-25 JST)

Status: **NO_GO_FOR_MOBILITY_CONTRAST_FROM_THE_CURRENT_MATCHED_COUNTS**. Contract feb248795020a94d12a77b14f644295e87361388 frozen before effect computation. Original v5 source and three original-derived environment/atlas archives verified by SHA256 and CRC. Same exact script rerun reproduced result.json and marine_support.csv byte-for-byte. Code commit e1ffe56e20883516bc3258500935c3cb8371f46c; Git blob de3828644419c194f733dbf40530b107307d6ddf verified identical to local executed script; local script SHA256 c522d6b8d365bf6b4ad863a6b5eb38c1f957fb5080b9bab3c15b1e77eb44696b; result SHA256 9e432ce2ba3b72bd2a12f74488f9fef11ef3d64e1f6dd8f410999e235afbded2; marine_support.csv SHA256 77d69e6304dcf8d999795a2a85596d3523be430b130c478d44e520c60869e6ec.

## Primary data support and decisions

112 same-site, same-season, same-vantage, same-citation observations at 27 sites (all seasons); 85 at 23 sites, 1993–2020; 55 adjacent jointly observed 1–5-year intervals at 7 sites with same vantage across endpoints. Adjacent jointly observed does not imply both species have no intervening separate observations. Observed zeros retained for compensation. Unobserved != zero. All 55 intervals pass positive endpoint and no intervening observed zero rules for marine contrast.

Strict network: zero synchronous multi-site annual windows at either 50 or 100 km if cross-site citation also required. Secondary relaxation of cross-site citation only yields 11 annual windows (1994,1995,1997–2004,2011), one region South Shetland Islands, changing roster drawn from ARDL/LION/LLAN/PTHO. 50/100 km results exactly equal. No estimate of strict cross-site compensation. Secondary C=min(loss,gain)/loss, calculated only in windows with some observed loss. Not movement probability, no assumption of a closed population or complete regional census.

| Start year | ADPE loss | ADPE gain | GEPE loss | GEPE gain |
|---|---:|---:|---:|---:|
|1994|0|1771|1333|0|
|1995|1887|1057|483|0|
|1997|0|1499|48|203|
|1998|1878|0|0|789|
|1999|373|0|0|898|
|2000|720|0|121|0|
|2001|665|0|0|1077|
|2002|1023|0|200|0|
|2003|538|0|159|321|
|2004|360|0|163|10|
|2011|847|0|0|1166|

In five paired-loss windows (at least one declining measured site for each species), ADPE loss 4528, gain 1057, capped loss-weighted compensation .2334363957597173; GEPE loss1126, gain331, capped .15008880994671403 (uncapped .29396092362344584). Equal-window mean ADPE .11202967673555908, GEPE .21226993865030674; difference +.10024026191474766, G>A 2/5, ties 2/5, G<A 1/5. Five differences [-.5601483836777954,0,0,1,.06134969325153374]. Year-deletion range [-.12469967260656542,.26533742331288346]; omit 2003 reverses. Site-deletion differences ARDL -.6672979797979798, LION +.21226993865030677, LLAN -.5601483836777954, PTHO +.012269938650306749. All loss-window pool (not matched): ADPE 9 windows, L8291 G1057 C.12748763719696055; GEPE 7 windows, L2507 G534 C.08655763861188671. Uncapped GEPE .2130035899481452. Different denominators, not an inferential comparison. Do not sum changing rosters across years into a population trend.

Marine: 31/55 intervals incomplete P100/hydro, 24 complete. Annual primary 18 intervals/5 sites before repeat gate, 17/4 afterward; FE rank13, physical rank4, residual df0; secondary 24/5, FE rank18, physical rank4, df2. Both two-region models fail frozen df>=5; **no P100 or other physical contrast coefficient fitted**, no simplified model rescue.

## Interpretation and decision

No stable evidence that gentoo's local numerical loss is more compensated than Adélie's under matched support. Neither rejection nor confirmation of true differential breeding dispersal. No claim of reverse species effect from pooled estimates. Existing strict 6-site/66-year same-census result of opposite trends (PR214) remains a descriptive same-site contrast, not a test of movement. Same site/year/citation/vantage does not guarantee identical survey dates, detection, footprint or foraging exposure. Positive productivity and negative count change are distinct demographic outcomes, not necessarily conflicting. No causal chain or individual movement inferred; no further same-data radius/lag/roster searches. No new independent observations, main and frozen manuscripts unchanged.

Reproduce: OPENBLAS_NUM_THREADS=1 python research/signy_seal_spatial_pressure_v1/sympatric_adpe_gepe.py ARTIFACT_DIRECTORY OUTPUT_DIRECTORY. Input pins embedded. Result regenerates complete 50/100km window rosters, omissions and marine gates. Raw observations are not committed.
