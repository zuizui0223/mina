# V12 — Order of past breeding outcomes: informative about *what*, exactly?

**2026-10-10, mina PR #193.** A fully **synthetic mathematical discriminability test**, not an Antarctic penguin result. No original Dryad individual rows or identifiers opened. Author's Kappes 2021 study already fitted 3,089 Adélie individuals with 9,603 records (1997–2013), age at recruitment, attempt experience, an individual ID random effect, year and colony effects and selective appearance/disappearance. These are already-prior-art adjustments and cannot be relabeled as our own methodological advance. Relevant source [Kappes et al. 2021, J Anim Ecol](https://doi.org/10.1111/1365-2656.13422).

## Why holding success counts fixed is stronger than V11 — but not enough

V11 compared two-history sequences `11` vs `01` with the same current success yet **different total successes** (2 vs 1). That comparison is intrinsically biased by *fixed latent individual quality*: highly successful individuals tend to have more successes.

V12 asks a less trivial comparison: at the same breeding-history length, compare `101` (success–fail–success) vs `011` (fail–success–success). They have **exactly two successes, one failure, and both currently succeed**. Predict the subsequent attempted reproductive outcome `Y4`, not survival, physical colony occupancy, or the probability of attempting to breed at all.

Four null/alternative patterns demonstrate a major identifiability boundary:

| Purely synthetic process | P(next success after `101`) | P(next success after `011`) | Truly causal second-previous-state effect? |
|---|---:|---:|---|
| Equal mix of fixed individual p=0.8 and p=0.2, iid yearly | **0.6800** | **0.6800** | **No** |
| Same fixed types, plus additive common `year` shocks on the logit scale | **0.7122** | **0.7122** | **No** |
| Fixed types with **different sensitivities to year/environment** | **0.6429** | **0.3571** | **No** |
| Fixed types with **different first-order state-transition probabilities** | **0.5154** | **0.6059** | **No direct second-order effect** |

All rows are exactly calculated from chosen probabilities, **not parameter estimates or evidence of real penguin phenotypes**.

The last row is ecologically important: each bird's breeding outcome in the next year depends on **only its present state**, through its own constant first-order transition matrix. Nevertheless, its *older* breeding outcome predicts its *future* outcome because the full observed sequence helps infer its transition type. This is distinct from (and potentially much more realistic than) an iid fixed-success mixture. Thus even an equal-success-count sequence-order signal **does not establish a genuinely second-order Markov or physiological memory process**.

## Exact mathematical argument for the additive-year control

For a bird with latent lifetime `alpha` and common seasonal environment `beta_t`,

`logit P(Y_t=1 | alpha) = alpha + beta_t`.

The likelihood of a complete observed binary success path `y_1,...,y_T` is

`L(alpha|y) = exp(alpha * sum(y_t) + sum(beta_t*y_t)) / product_t(1+exp(alpha+beta_t))`.

For any two histories on the same set of calendar years with the same **number of successes** `k=sum(y_t)`, their likelihood ratios between two candidate values of `alpha` are **equal**. Hence their posterior latent quality mixture and next-year predicted success are the same. Different environmental conditions can affect how frequently the two orders occur in the population, but they cannot make their relative posterior individual quality differ **within this strictly additive complete-observation model**.

This equivalence fails if true year reactions differ by individual quality: `logit P(Y_it=1)=alpha_i+beta_t+delta_i*beta_t`. It also fails when individual first-order transitions differ across types, even if no bird depends directly on `Y_{t-1}` after conditioning on its current `Y_t` and transition type. Informative dropout, individual mortality, missed attempts, changes in observer effort and age×individual interactions introduce more routes to apparent sequence memory.

## What a legitimate source analysis would require

The original Kappes Dryad `BreedingSuccess.csv` metadata provides attempts and successes, but **source-only retrieval currently HTTP 403**, as documented in [official source check #38012233947](https://github.com/zuizui0223/mina/actions/runs/38012233947). The authors request consultation for detailed reuse; IDs are recoded and should not be joined to differently coded Ross studies. We did not read any animal source records in this V12.

If it becomes appropriately available, a *descriptive/predictive* stage would need: source-valid exact within-study IDs; **three consecutive observed breeding attempts** in identical calendar/age risk sets; a next-year known breeding attempt and measured success (not automatically `0` for absence/nonbreeding); colony, annual food/ice conditions and detection; fit H0 first-order state-dependent transitions with **individual-specific heterogeneity and quality×environment response**, not just a random-intercept Bernoulli model; hold out entire later calendar years and check the gain from adding second/third lag history. Significant fitted lag coefficients in non-held-out data are not sufficient.

A **causal carry-over** claim still requires independently varied past reproductive investment, or an instrument/natural experiment that changes prior breeding outcome without simultaneously changing individual condition, food, site or detection. Simply fitting richer histories within three colonies on Ross Island neither identifies a penguin-specific carry-over mechanism nor independent inter-island dispersal.

## Actual implementation and scientific verdict

The frozen V12 contract, source-free script, synthetic tests and GitHub workflow provide a reproducible sequence-order **negative-control panel**:

- `contracts/ADELIE_SEQUENCE_ORDER_VS_QUALITY_YEAR_INTERACTION_GATE_V12.json`
- `scripts/audit_adelie_equal_count_order_frailty_v12.py`
- `tests/test_adelie_equal_count_order_frailty_v12.py`
- `.github/workflows/adelie-equal-count-order-frailty-v12.yml`

**Decision:** An order effect is stronger than a count effect against *simple iid* frailty and shared additive year shocks, but not a causal memory discovery. Quality-by-year interactions and heterogeneous first-order transitions can produce the same pattern with exactly zero direct higher-order effects. Do not present this as a new general statistical theorem (it follows standard mixture likelihoods), a measured penguin result or a new island-biogeographic mechanism.

Ecology manuscript [PR #189](https://github.com/zuizui0223/mina/pull/189), origin-gated mark-resight [PR #142](https://github.com/zuizui0223/mina/pull/142), and emperor georeference [PR #195](https://github.com/zuizui0223/mina/pull/195) remain scientifically unchanged.
