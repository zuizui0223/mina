# Antarctic penguin colony sea-ice future: physical source compatibility audit

Goal: verify whether CMIP6 native historical 1995–2014 August–November coastal-cell mean SIC matches the observed OSI SAF nearshore 1995–2014 August–November mean at the fixed 39 Adélie source breeding-site codes. This **does not** infer warming effects on penguin nesting.

The historical native model and satellite observed sites have **different spatial supports** (model ocean grid cell vs 0–100 km coastal satellite mean). Comparing their absolute seasonal levels measures baseline mismatch, not the skill of future model anomalies.

The prior original scenario builds *delta-adjusted* future SIC = observed 1995–2014 SIC + (model 2041–2060 / 2081–2100 mean − model historical 1995–2014 mean). Our raw future sensitivity compares model-native **uncorrected absolute future** SIC against an observed past envelope. That is an **intentionally invalid same-scale forecast**, used only to expose reliance on bias adjustment, never to choose a superior model.

This analysis:
- pins all five input Git blobs (39 historical sites, original OSI monthly 1991–2020, 3-model original historical climatology, 3-model future change, original MAPPPD counts);
- audits baseline bias, historical interannual SD, model coastal cell distance, site/spatial rank, count-weighted errors and regional differences;
- compares raw-vs-delta history-novel classifications under margins 0/2/5 pp as a sensitivity *diagnostic*, NOT alternative future penguin demographic outcomes;
- tests how a site support mask of all three models within 25/50 km and absolute historical mismatch ≤10/15 pp changes coverage and original-denominator climate novelty;
- matches observed **20-year mean against 20-year mean** using 1991–2010 vs 2001–2020 shifts (the two windows overlap by 10 years and there is only one shift per site). This is a time-window comparability sensitivity, not a physical change statistical test.

Keep existing physical novel-SIC observations and the threshold-uncertainty scenario. If a classification is contingent on the delta correction or source mask, report this explicitly. The original 39 source-site latest census weights are noncontemporaneous (2001–2025) and mixed metrics. The 3 CMIP6 models are single members. None of this yields a future count forecast or extinction probability.
