# V24b–c decision: matched annual marine–terrestrial reallocation
2026-11-27 JST. Executed original V5 source and historical marine archives under the frozen V24 design. No manuscript or main change.

## Source and support
V5 four publisher payloads SHA-verified, 771 exact adjacent-year focal same-citation/vantage pairs reproduced. All 771 nominal site IDs and region labels join the old atlas and the V23 1-km fixed mapped area; this is not 771 independently replicated locations. All marine data ZIP hashes/CRC, original hydro and winter-polynya coordinate/region matches, monthly SIC 71,400 rows, and common SIC values verified. Primary coordinate separation <=1km, ending <=2018 to exclude the known 2019 GLORYS forcing transition. SIC Aug–Nov 100km field, salinity/SST same months, P100 June–Oct. Same-year observations and climate seasons not exact timing or causal ordering.
| Support | Site transitions before >=5 site group gate | After gate | Sites | Groups | Regions/250km blocks |
|---|---:|---:|---:|---:|---:|
| SIC |603|275|64|42|3/7|
| SIC+SSS+SST |432|113|55|19|3/7|
| joint P100 |214|83|51|13|3/7|
The broad initial SIC support spans ten reporting regions, joint six, but the >=5 matched site group gate leaves three. All pre-fixed growth regressions fail the >=8 spatial block support criterion (or other support gates); no regression coefficient, p-value or causal mechanism. No relaxed thresholds.

## Observed count allocation × fixed marine fields and map
Alignment=sum((p1-p0)*(x1-x0)); negative means the new observed allocation weights smaller increases or larger decreases in that field. It is a small, retrospective arithmetic contrast, not a change in actual movements, habitat preference, adaptation or total weighted sea ice. For primary SIC cohort:
| species | groups | negative alignment | median pp | median change in fixed 1km mapped vegetation proximity |
|---|---:|---:|---:|---:|
| ADPE |25|16|-0.010849|+0.5944%|
| CHPE |7|4|-0.017391|+2.9870%|
| GEPE |10|7|-0.034552|-1.5901%|
All three medians negative but magnitudes small, no inferential replication. CHPE vegetation allocation 7/7 positive reproduces same V23 groups, not new independent evidence. GEPE has 4/10 positive vegetation contrasts. In joint 13 groups: ADPE SIC alignment median +0.022733 pp (1/2 negative), CHPE -0.042571 (2/2), GEPE -0.035831 (7/9); GEPE SSS alignment median +0.000182 native units (6/9 positive), P100 median -0.014259 pp (6/9 negative). Other species only 2 joint groups each; no robust common marine–land mechanism. The static map is not historical vegetation, nutrient deposition or a measured plant response.

## Pre-fixed sensitivities
At 1m coordinate tolerance no eligible >=5-site strata in either SIC or joint comparisons. Do not claim exact-coordinate replication. At 5km vs 1km the eligible SIC/joint results and medians identical for the tested windows. Extending to 2020 adds one ADPE SIC stratum (26 total; 16 negative), negative median remains; joint groups unchanged. Excluding NZ aerial source removes all ADPE eligible strata; other species unchanged, leaving two regions/four blocks. No geography-wide species contrast; a change of coordinate metadata is not movement.

## Execution and repair
Original run https://github.com/zuizui0223/mina/actions/runs/45932212926 successfully downloaded and validated source bytes, produced exact 771 joined rows. Initial species label overwritten by info(v) dictionary in aggregation (empty per-species summaries); do not use original aggregate. V24b repairs only the label and preserves all original windows, variables and support criteria. Corrected replay https://github.com/zuizui0223/mina/actions/runs/45932350160; 1568 independent arithmetic and group-count checks, max discrepancy 4.2292e-11, source_join.csv SHA256 c08da8c0424224ac47412106b6ef27cc28629eb3fdee4718642eff8e158d02c7; result artifact 15168249196 digest 29f9e6bb8ccd28cf5074ce4e43359e686cec788bc2da0da5e2466f586c15ce1b. Readback https://github.com/zuizui0223/mina/actions/runs/45932444028 verified archive and predeclared SIC/joint sensitivities. RESULT_V24B.json archives primary receipts; full strata, all sensitivity summaries and exclusions in the corrected artifact. No independent ecological replication.

## Direction
Do not continue shrinking the temporal sample or relaxing support to obtain significant effects. Keep V22 continental observed distribution–map intersection and V23/V24 annual outcomes as descriptive modules, with polynya optical association and earlier marine physical niche findings retained separately. To extend macroecology, use full continental geography as sampling frame: independently mapped ice-free land and coastal available habitat; verify geometry/availability and plant mapping support, separate occupied-location atlas from censused absences, test spatial marine niche × terrestrial opportunity across all regions, and use historical counts for independent temporal evaluation only where supported. Future scenario calculations should be physical exposure/habitat opportunity conditional scenarios, not predicted populations absent validated response. No local nutrient search as main line. No main merge or submission.
