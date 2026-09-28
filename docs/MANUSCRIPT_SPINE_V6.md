# Manuscript spine v6 — count-error-bounded scale hierarchy

## Working title

**Common decline, divergent endpoints: scale-dependent demography across Antarctic penguin breeding islands**

## Central ecological contribution

The manuscript now separates three statements that must not be collapsed into one another.

1. **Island-state divergence is robust:** neighbouring islands share a strong regional decline but retain different abundance states, extinction endpoints and broader assembly outcomes.
2. **An observed nested variability hierarchy exists:** in the stable-roster subset, raw Wang–Loreau beta is larger from colony-code components to islands than from islands to the archipelago.
3. **The biological interpretation of that hierarchy is count-error sensitive:** it exceeds the frozen Poisson and CV10% independent-error nulls but is compatible with the frozen CV20% sensitivity.

The N_eff result is a separate line of evidence: a small conditional association that survives its own momentum, serial-structure and count-error diagnostics but does not provide robust held-out prediction.

## Frozen raw hierarchy

Primary colony-code inference is restricted to Cormorant, Humble and Litchfield because these are the only islands with unchanged reported colony-code rosters across 1991–2017.

Observed raw decomposition:

- beta within islands = **1.0737**
- beta among islands = **1.0112**
- beta total component to archipelago = **1.0858**
- observed within-island share on the additive log-beta scale = **86.4%**

The raw ordering persists before Litchfield extinction and after removing Litchfield. The component-count audit also retains the ordering, so it is not explained solely by the larger number of series within islands.

## Frozen count-error boundary

The measurement-error null forces every latent colony-code trajectory within an island to be exactly proportional to the island total and then adds independent observation error.

**Poisson**
- raw log-beta contrast p < **0.00001**
- mean null beta within = **1.0274**

**Gamma–Poisson CV10%**
- raw log-beta contrast p < **0.00001**
- mean null beta within = **1.0429**

**Gamma–Poisson CV20%**
- raw log-beta contrast p = **0.450**
- beta-within tail p = **0.924**
- mean null beta within = **1.0882**

Therefore the raw hierarchy is unusual under the frozen low-to-moderate error models but **not robust to the full frozen error family**.

The transformed sensitivities are explicitly demoted:
- detrended median within/among ratio: Poisson p = **0.054**
- annual-growth ratio: Poisson p = **0.448**
- under Poisson alone, all three within-island growth beta values exceed among-island beta in **99.85%** of error-only simulations

The stronger detrended/growth separation is therefore not independent evidence for biological buffering.

## Relationship to N_eff

N_eff remains:

> **conditional association, not prediction, not causality**

Frozen result:
- primary beta = **+0.1168**
- after two lagged growth terms = **+0.1126** (**96.4%** retained)
- two-lag held-out gain = **+0.000444**
- two-lag circular-shift p = **0.00102**
- exact joint shift p = **5/416 = 0.0120**
- original held-out-gain year-block test p = **0.262**
- fixed N_eff count-error sensitivities remain below p = 0.01

The hierarchy does not validate N_eff. The two results answer different questions and use different nulls.

## Allowed interpretation

- island demographic states and endpoints diverge under shared regional decline;
- the observed raw nested beta contrast is larger than expected under Poisson and CV10% independent count error;
- the same raw contrast is compatible with the frozen CV20% sensitivity;
- actual Palmer observer error is not calibrated in the public census table;
- component-count arithmetic does not explain the raw ordering;
- N_eff remains a small separately robust conditional association.

## Prohibited interpretation

- temporal buffering is proven to reside within islands;
- the hierarchy is measurement-error robust;
- CV20% is the true Palmer error rate;
- counting error caused the hierarchy;
- detrended/growth beta provides stronger confirmatory evidence;
- 86.4% is a causal mechanism fraction;
- beta variability proves spatial insurance or dispersal-mediated rescue;
- N_eff is predictive, causal, or an early-warning indicator.

## Discussion order

1. Common long-term decline and weaker annual synchrony are established context.
2. Show divergent island states/endpoints.
3. Present the exact raw nested beta decomposition.
4. Immediately apply the complete-synchrony count-error null.
5. State the boundary: Poisson/CV10 retained, CV20 not retained.
6. Explain why detrended/growth results are especially error-sensitive and are not promoted.
7. Keep the component-count audit as an orthogonal arithmetic check.
8. Report bounded environmental mechanism failures.
9. Position N_eff as a separate weak but robust conditional association.
10. End with two decisive external needs: empirical count-error calibration for the hierarchy and colony-code/GIS crosswalk or independent replication for N_eff.

## Journal position

**Ecosphere remains the first-shot target**, but the pitch changes.

The paper no longer sells a demonstrated buffering hierarchy. Its contribution is a scale-explicit long-term case study that identifies where an apparent hierarchy arises, subjects that result to an explicit measurement-error null, and shows exactly which ecological inference survives.

## Terminal rule

Same-census development is closed at v0.7.

Do not add:
- intermediate CV values;
- alternative pooled-composition definitions;
- correlated-error families;
- alternate beta definitions;
- extra transformations;
- colony-roster reconciliations;
- new climate windows or topology metrics

unless external empirical observer-error calibration or genuinely independent data become available.
