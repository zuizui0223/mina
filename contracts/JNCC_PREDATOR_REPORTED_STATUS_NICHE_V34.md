# V34 — Independent publisher-source island mammal *reported-status* niche screen

**Prepared 2026-10-27. This is a source-only extension to JNCC #201 V32/V33. The already seen 17-species JNCC V30 concentration outcomes are strictly untouched. This is NOT an island invasion causal model, predator occupancy estimate, or new seabird biological effect.**

## Exact original sources
- RSPB UK Islands public feature layer (2014 OS MasterMap derived; 9,688 mapped island **points**, not shoreline polygons), uniquely keyed by \`lowid\`. Original attributes are high/low tide area (ha), 2014 human population, ferry, \`group_\`, country and coast.
- Stanbury et al. (2017) ESM5 source XLSX (9,688 island rows plus two author header rows; original SHA256 \`3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5\`), with original island IDs in the unlabeled first column and named predator fields (American mink, Brown rat, etc.).
- The source-only V33 audit checked the two first-party inventories join on exactly 9,688 \`lowid\` values, rather than inferring a join from an island name. The original two-row ESM5 header is explicitly handled; code \`0\` is not certified field-survey absence.

## Estimand and fixed model
For each source predator (American mink and brown rat), fit **classification of the 2017 published categorical record** for the same 2014 island inventory. Two fully reported codings: \`confirmed_only = 1\` versus all other *reported* codes and \`confirmed_or_probable = 1 or 2\` versus reported codes \`0\` or \`3\`. The latter is **not** confirmed absence and cannot validate a true ecological presence/absence SDM. Always show literal four-category counts and sensitivity to these status definitions.

Independent source predictors chosen without JNCC data:
1. log(1 + RSPB high-tide physical island area in hectares);
2. log(1 + RSPB resident human population in 2014);
3. boolean RSPB ferry access.

The model is regularized logistic regression with standard-scaled predictors and fixed penalty \`C=1.0\`. Validate by **GroupKFold(n=5) holding out RSPB \`group_\` archipelago groups**; score Brier against a training-prevalence-only baseline and AUC where both classes are represented. Report separate five folds, positive labels in each test fold, standardized coefficients and five-fold mean Brier gain. Do not tune predictor variants, class threshold, holdout group or folds after results.

## Known confounders and non-identifiability
- A 2017 \`confirmed\` label may be driven by survey effort, island accessibility and management intervention; the comparison label is NOT field-tested nonoccupancy.
- Stanbury's predator source may impute/infer statuses from island geography and swimming ability; model can predict those *prior coding rules*, not independently predict true current mammals. Confirm code origin and coverage before interpreting.
- RSPB data points do not provide coastlines or actual seabird nest coordinates. Its mainland-connected/tidal-island exclusion differs from JNCC administrative Master sites and Antarctica.
- The 2014 island status cannot automatically be used for either JNCC Seabird 2000 (1998–2005) or Seabirds Count (2015–2021); extermination/recolonization and observation dates need independent history.
- No measured nest susceptibility, survival, local predator access, social attraction, observed bird movement, or within-network predator heterogeneity are available in V34.
- V34 fits predator-record reporting only, never opens JNCC adjusted breeding-count magnitudes or concentration \`E\`. A later H2 effect requires strict physical JNCC child-site-to-RSPB island linkage and the V32 mixed-exposure within-parent sample gate.

## Frozen source gates
- Exact original ESM5 SHA, 9,688 rows and two-row source layout.
- Exactly 9,688 original RSPB \`lowid\` values; one-to-one equality of key sets; differing island-name strings are quality metadata, not matching keys.
- Categorical codes only \`0,1,2,3\` for both mink and brown rat. Blank/unrecognized codes STOP, never impute absence.
- Source prediction gate: >=30 reported positives and >=30 comparison labels, >=5 independent RSPB archipelago groups, >=3 held-out folds with both reported classes. Failure is a support stop, not evidence of predator niche equality.
- Positive or negative Brier improvement is only model out-of-group skill for *published records*, not extinction/colonization risk.
- No predator-mechanism coefficients may be propagated into JNCC V30 as though source outcomes were independent/time-correct.

## Reproduce
\`python scripts/model_jncc_predator_reported_niche_v34.py --out /tmp/JNCC_PREDATOR_REPORTED_ISLAND_NICHE_V34.json\`

Workflow: \`.github/workflows/seabird-jncc-predator-reporting-niche-v34.yml\`; original-data JSON artifact, synthetic source tests. Results can be saved as a compact SHA-backed JSON record after CI, with no raw license-restricted bird or mammal rows committed.
