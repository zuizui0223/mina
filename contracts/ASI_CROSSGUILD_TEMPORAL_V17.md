# V17 — Repeated penguin–flying-bird nest counts within the same original ASI sites

2026-10-20; pre-response-effect contract fixed using only V16 structural sample support. This is a *new time-differenced* biological comparison, not a cross-sectional raw count correlation and not a revised V14/V15 environmental gate.

Source is the exact ASI 2013 Ecology original CSV, publisher MD5 00871bd47b6ec30cda68d1506120bfb3 and SHA256 e01ee9bfbd8337bcaca7c71aea0b00162f9015cf4954d3ad76eed536cad37634; official DOI 10.1890/13-1108.1. Same strict V16 source-row filter: source=ASI, original NESTS only, accuracy 1–3, exact day, original season clock, 7 predeclared species, entire conflicting Site_ID/Region and duplicate same-species/day groups excluded.

## What would be new, and rival explanations
Contrast seasonal **within-source-site annual changes** in penguin nesting counts against fish- or other marine-foraging flying bird nesting counts on the *same dated survey footprint*, rather than simple cross-site richness, unconditional count scaling, or the already reported Antarctic Peninsula population trends. Candidate Hshared: forcing shared at breeding sites yields same-sign growth; candidate Hguild: species with distinct foraging ecology show weaker or opposing changes. Rivals include site-specific observer effort, phenology, colony delineation, fishing, relocation and imperfect breeding count precision. Neither sign identifies competition or causal marine resource coupling, and source not proven independent from overlapping MAPPPD observations.

## Temporal eligibility frozen before Count outcomes
- Pair each of ADPE/CHPE/GEPE/MCPE with each of BESH/KEGU/SOGP **at exact common original Site_ID+Season+Date** in both seasons; never make an unreported species a zero.
- A site/species-pair/season with >1 genuinely co-dated survey is **excluded in full**, no maximum, median, or favorable count/date selection.
- Require two **consecutive** source seasons y,y+1 and same original paired species; do not construct a growth rate across arbitrary multi-year gaps.
- Survey calendar time-of-year in the two seasons must be **within 21 days**, assessed before looking at Count. This reduces nest chronology exposure but does not prove perfectly matched breeding stage.
- Pair counts must be original nonnegative numeric nest counts with no blank, textual qualifier or invalid value. Validity is checked only after structural gate passes; no value-based outcome selection. Drop invalid Count transitions completely and recheck numeric support without threshold relaxation.
- A spatially transferable comparative biological test requires at least **20** distinct site×species-pair consecutive-year transitions from **10** original Site_IDs across **3** original ASI Regions. No report of all Antarctica or independent true islands follows even if pass.
- Report additional unmodelled yearly co-dated pairs, temporal support by flying guild and region, fraction held out due >21 days, and site count. These are metadata sample counts, not effects.

## If, and ONLY IF, the frozen gate passes
Compute one exploratory equally site-weighted Pearson correlation between penguin and flying-bird log(1+nest_count) adjacent-season changes. Use all 4×3 prespecified species pairs, do not select the best partner. Weighted across all site-pair transitions so each distinct Site_ID gets total weight 1. Report site-block bootstrap 90% interval (fixed seed 20261020, 300 resamples), leave-one-source-region-out correlation, cross-guild sign concordance, original sample size, and source precision/season limits. A correlation is an association of reported nest counts, not evidence of predation or island capacity. Do not change thresholds, season windows, taxon groups, weighting or correlation after seeing any original Count values. No causal p-value or 2026 environmental inference.

If the gate fails, stop before using Count values: this original programme contributes co-dated observations but cannot establish interannual cross-taxon dynamics on several geographically distinct sites. Neither species interaction nor biological null is identified.
