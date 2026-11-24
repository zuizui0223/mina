# Conditional soil water–nitrogen associations: public-source cross-study diagnostic

Executed locally **after** synchronization commit bf62eae5ce48c93a8a644205795a45387d15e0d5. Reproducer: [recheck_carbon_conditioning.py](recheck_carbon_conditioning.py), commit b687ba687f120843252ad4f7cd43c3deb149895e. Original public sources and exact MD5 checks are specified in the script and [synchronization ledger](TERRESTRIAL_EXTENSION_SYNC_20261124.md). No restricted AADC inputs or original data uploaded.

## Design

Natural-log nitrogen outcome vs natural-log water, before and after adjustment for log organic carbon (same complete-case sample). Between-group regressions use means of log values, with species + year FE for the colony soil data (Iannuzzi et al. 2025, DOI 10.5281/zenodo.17742676) or site×stage + cover FE for the succession soil data (Ball 2025, DOI 10.15784/602015). Within-group regressions demean by sampling group, equal total group weights. Leave-one-named-site-out sensitivity for both specifications, no new inferential p-values or formal difference between studies. Values rounded to five decimals; independent residualization reproduces all ten adjusted water slopes.

| Study | Outcome | Level | n | Groups | Sites | Water before carbon | Water after carbon | Carbon conditional on water | Adjusted water LOSO range |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Colony | NH4 | between |29|29|23|0.10894|-0.03856|0.21059|[-0.36522,0.17751]|
| Colony | NH4 | within |87|29|23|0.11417|-0.13320|0.45950|[-0.22508,0.09462]|
| Colony | NO3 | between |18|18|14|-0.01529|-0.31432|0.55445|[-0.57054,0.00808]|
| Colony | NO3 | within |54|18|14|-0.01220|-0.15256|0.38633|[-0.21626,-0.09373]|
| Succession | NH4 | between |44|44|3|0.51336|-0.22038|0.82280|[-0.60849,1.23504]|
| Succession | NH4 | within |131|44|3|1.19474|0.81175|0.44649|[0.47741,1.35445]|
| Succession | NO3 | between |44|44|3|0.39465|0.54947|-0.17361|[-0.23855,1.78339]|
| Succession | NO3 | within |131|44|3|0.41884|0.77670|-0.41719|[0.66689,0.81164]|
| Succession | Total N | between |44|44|3|0.71267|-0.17560|0.99608|[-0.27672,-0.10524]|
| Succession | Total N | within |131|44|3|0.80231|0.06261|0.86235|[-0.00515,0.08187]|

Interpretation: positive water–ammonium association is not robust to carbon conditioning between groups in either source. Succession within-group water–NH4 and water–NO3 remain positive in all three site deletions; colony within-group NH4 is sign-unstable and nitrate negative after adjustment. Succession total N slope strongly attenuates at both levels. These are conditional associations, not causal mediation, and the two sources differ in sampling design, geography, covariates and measurement context. No plant abundance response, marine-origin isotope or matched colony and non-colony controls. No evidence that penguin-derived nutrients cause the contrast, or that one population-level slope differs significantly from another.

Next: obtain paired moss trait / plant tissue N records with verified sample identity (USAP 602038 and 602039); if no shared sampling units, do not merge on species names alone. Distinguish soil moisture from plant relative water content. The known literature already reports moss N-gradient effects; test a genuinely new contrast only if data support it. No merge or manuscript submission.
