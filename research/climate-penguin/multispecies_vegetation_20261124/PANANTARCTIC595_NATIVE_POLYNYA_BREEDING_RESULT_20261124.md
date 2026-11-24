# Completed native 595-colony winter polynya source and observed breeding responses

Executed 2026-11-24. Source workflow [45405469441](https://github.com/zuizui0223/mina/actions/runs/45405469441), job 138484885360 SUCCESS; [artifact 14926710177](https://github.com/zuizui0223/mina/actions/runs/45405469441/artifacts/14926710177), SHA256 b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8, verified locally. DEEP-AA publisher archive MD5 f3f958389cc5e67ac1c4e3a6ee164318 and SHA256 b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9. All 595 sites / 18 source regions / 15 complete June-Oct winters (2004–10, 2013–20), 8925 site-winters per radius. Measured zero at 100km 1084, 25km 3062. Missing 2003/2011/2012 not filled. 44300 selected native pixels, independent prior 23-site check max winter/month error 1.11e-16/3.33e-16. Local monthly-to-winter independent reaggregation max error 1.11e-16, all coordinates and regions match exact atlas. Frozen preflight commit 43570d4d47884d70ec970a5f16c6421f47f08fed. Atlas artifact 13669533413 (add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a); marine artifact 13829236358 (64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5).

## Fixed-period physical comparison, 2004–10 versus 2013–20

| Radius | Early site mean % | Late site mean % | Increasing sites | Equal-site delta pp | Equal-region delta pp | Equal-250km-block delta pp |
|---|---:|---:|---:|---:|---:|---:|
|25km|4.714101|6.390468|483/595|+1.676366|+0.826386|-0.325009|
|100km|3.048149|3.681888|408/595|+0.633739|+0.463122|-0.035533|

Site-equal winter-deletion ranges (25/100km) +1.327076..+2.061331 / +0.376061..+0.904580 pp. Block-equal ranges -0.578121..-0.167001 / -0.161396..+0.134147 pp. 43 blocks, not an equal-area continent-wide ocean sample. Known-colony exposure increases on average but not universal geographic increase. 100km region examples central-west peninsula +2.354287 (106/106 increase), South Shetland +1.223742 (118/118), Wilkes +1.557903, Victoria -0.810574, southwest peninsula -0.453224; South Orkney 25km +1.407917 vs 100km -0.240840. The 588 exact common hydro sites show 354 both increased SIC and P100; cross-site correlation of differences +0.044264 (different seasonal supports), not causal independence. No inference treating overlapping radii as independent samples.

## Frozen breeding model execution

460 exact positive-endpoint consecutive observed 1–5 year intervals before repeat support; no jumping over observed zeros, no missing-year imputation. Same known census method, not necessarily coverage/date/effort. Response annualized ln(N_end/N_start); site-equal weighting, site and end-year FE, controls Aug-Nov SIC /10pp, salinity /0.1, temperature /C. Native winter fraction mean in pp over years start+1..end, all observed. Primary annual, secondary 1–5 years; full rank and >=5 residual df. Separate species panels.

| Interval | Species | n/sites/regions | P100 beta per pp | P25 beta per pp | Ground-only P100 | Baseline/full within-FE R2 |
|---|---|---|---:|---:|---:|---:|
|annual|ADPE|45/11/4|-0.005674|-0.014180|+0.085466|.271917/.274077|
|annual|CHPE|87/19/3|+0.040350|+0.022473|+0.040350|.031134/.069449|
|annual|GEPE|128/30/3|-0.003577|+0.020744|+0.021094|.088960/.089004|
|1–5 years|ADPE|89/27/5|-0.035761|-0.020603|-0.036083|.050221/.136014|
|1–5 years|CHPE|131/25/3|+0.045630|+0.003630|+0.045630|.034695/.089290|
|1–5 years|GEPE|199/39/4|+0.059801|+0.010724|+0.044520|.049452/.073707|

All primary annual fits fail estimable region omission sign stability. Secondary ADPE site/block/region deletion ranges respectively [-.055589,-.023205],[-.055589,-.021112],[-.055589,-.018339] (all 27/9/5 estimable negative). GEPE [.044704,.072123],[.043933,.088996],[.020308,.102524] (39/6/4 all positive). CHPE region deletion [-.028060,.084318] and block omission slight negative. Deletion ranges are not confidence intervals. Site geography differs by species; multi-year ADPE 14/27 Victoria Land, CHPE 24/25 and GEPE 37/39 South Shetland or central-west Peninsula. No formal species-by-exposure interaction or causal effect established; secondary estimates do not replace weak primary. No new p-values or future demographic forecast.

## Forward transfer, fixed 2004–10 train / 2013–20 test

| Interval | Species | Train/test n | Sites | Site-only RMSE | Base RMSE | P100 RMSE |
|---|---|---:|---:|---:|---:|---:|
|annual|ADPE|16/11|3|.414874|.374525|.507686|
|annual|CHPE|20/19|5|.287949|.281091|.352202|
|annual|GEPE|34/38|10|.366615|.608015|.611208|
|1–5 years|ADPE|23/19|5|.280022|.285466|.402644|
|1–5 years|CHPE|49/39|12|.334436|.338874|.337907|
|1–5 years|GEPE|70/69|20|.198412|.278577|.321764|

All annual P100 worse than base. All secondary P100 worse than site-only; CHPE tiny improvement vs base not established transfer gain. Do not use fitted slopes for future population forecast.

## Reproduction and decision

Unchanged preflight/full script analyze.py SHA256 f8c80ea8b98e1b2d0cf95eab2ce35c1a100c66fedd904a6113bcc42d52567da8, executed in full mode. Separate verification script verify_full.py SHA256 72be1b5b6813ccf19682cde8d99668c699ef007af848290595c53bc9d57a47c9. Independently rechecked 1190 site/radius differences (stdlib mean max 1.421e-14 pp) and all 36 fitted models via centered weighted full dummy SVD regression (max 3.063e-13). Numeric reproduction is not new biological replication. Local bundle panantarctic595_polynya_breeding_results_20261124.zip SHA256 6e87b7cf139689396db7fe9c970f5b2cf2f5318208709804162b8430edc64f50 contains exact derived source artifact, executed scripts, physical changes, 460 intervals, 36 fits, all deletion and forward checks, receipts and source IDs. Do not claim main merged or publication. No restricted AADC data used. Candidate next test: assess matched same-site and same-observed-interval cross-species support before any species contrast; no further radius/lag optimization. Retain physical change and secondary species-specific association as explicitly distinct evidence levels.
