# Quantitative rules of breeding-space contraction — exploratory synthesis v1

**Status:** post-hoc exploration on `explore/contraction-scaling-law-v1`.  
**Submission boundary:** none of these results modifies the frozen Ecology Report.

## Question

Can the five declining penguin population trajectories be summarized by a
simple quantitative rule linking breeding-pair abundance (N) to effective
monitored breeding-component number (E=N_eff)?

## Rule 1 — long-term contraction is consistently sublinear

For each population we fitted

[
\log E_t = \alpha + \kappa \log N_t.
]

Observed annual-trajectory elasticities:

| Population | kappa | R2 |
|---|---:|---:|
| Cormorant Adélie | 0.069 | 0.586 |
| Humble Adélie | 0.203 | 0.906 |
| Litchfield Adélie | 0.465 | 0.898 |
| Signy Adélie | 0.289 | 0.344 |
| Signy chinstrap | 0.366 | 0.634 |

All five slopes are positive but below one.

A population-fixed-effect common slope is **0.250** with within-population
R2 = **0.585**. However, leave-one-population-out common slopes span
**0.139–0.354**, so 0.25 is not supported as a universal exponent.

**Candidate rule:** numerical decline is faster than loss of effective breeding
components; breeding-space contraction is long-term and sublinear.

## Rule 2 — no common collapse threshold

We compared a single power-law trajectory with:
- a quadratic acceleration model;
- hinges at 50%, 25%, and 10% abundance retention.

Whole-population leave-one-out prediction selected the **single power law
(M1)**. Equal-weight mean held-out RMSE:

| Model | LOO RMSE |
|---|---:|
| single power law | **0.337** |
| 50% hinge | 0.357 |
| 10% hinge | 0.366 |
| 25% hinge | 0.368 |
| quadratic | 0.390 |

Thus no frozen threshold or acceleration model generalized better than the
simplest power law.

The descriptive state at first crossing of 50% starting abundance also varies
widely: E retention is about **62–92%** across the five populations. At still
deeper decline the divergence is larger rather than smaller.

**Rejected candidate:** a universal terminal threshold at which breeding space
suddenly collapses.

## Rule 3 — the scaling is a long-term trajectory property, not an annual response law

The common level relationship is substantial (within R2 = **0.585**), whereas
the population-demeaned first-difference relation between annual changes in
log(E) and log(N) has slope **0.120** and R2 = **0.071**.

After removing linear calendar-year trends, residual abundance–E coupling is
weak in four populations and strong mainly in Litchfield:

- Cormorant residual R2 = 0.079
- Humble = 0.0001
- Litchfield = 0.617
- Signy Adélie = 0.048
- Signy chinstrap ≈ 0

The pooled detrended statistic is therefore not treated as a replicated rule;
it is strongly influenced by Litchfield.

**Candidate interpretation:** effective breeding-space organization behaves
more like a slowly changing state of long-term decline than an immediate
year-to-year response to abundance fluctuations.

## Rule 4 — simple starting conditions do not explain kappa

We froze four candidate predictors of population-specific kappa:
initial E, number of monitored components J, initial evenness E/J, and total
decline depth. With only five population units, we used no p-values and required
a predictor to beat an intercept-only leave-one-population-out baseline.

Intercept-only LOO RMSE: **0.170**.

| Predictor | LOO RMSE | Relative to baseline | Spearman rho |
|---|---:|---:|---:|
| initial E | 0.182 | 1.08 | 0.50 |
| initial evenness E/J | 0.184 | 1.08 | 0.40 |
| decline depth | 0.265 | 1.57 | 0.10 |
| component count J | 0.278 | 1.64 | 0.45 |

None improved prediction over the mean.

**Rejected candidate:** kappa is a simple function of initial breadth, number
of monitored components, evenness, or decline severity.

## Current best quantitative hypothesis

The strongest rule left standing is not a universal exponent but a **sign and
scale inequality**:

[
0 < \kappa < 1
]

for all five observed trajectories.

In words:

> **As penguin populations decline over decades, their effective breeding-space
> organization contracts in the same direction but more slowly than numerical
> abundance. The rate of that contraction is population-specific and is not
> explained by simple starting geometry or decline depth.**

This is a candidate rule for independent testing, not a confirmed penguin law.

## Biological reading

The pattern is consistent with **spatial inertia**: established breeding
structure persists through substantial numerical decline, while cumulative
redistribution gradually reduces the effective number of breeding components.
The weak first-difference relationship argues against interpreting kappa as an
instantaneous demographic response coefficient.

What determines kappa remains open. Candidate causes now need genuinely new
information, such as terrain/snow exposure, component-level reproductive
performance, predation, or individual movement histories, rather than further
transformations of the same five abundance trajectories.

## Provenance

Frozen exploration contracts:
- `contracts/CONTRACTION_SCALING_LAW_EXPLORATION_V1.json`
- `contracts/CONTRACTION_SCALING_SHAPE_EXPLORATION_V1.json`
- `contracts/KAPPA_PREDICTOR_EXPLORATION_V1.json`

Scripts:
- `scripts/explore_contraction_scaling_law.py`
- `scripts/explore_contraction_scaling_shape.py`
- `scripts/explore_kappa_predictors.py`

Latest successful workflow run: **37000039809**  
Artifact: **11223511401**  
Artifact digest:
`sha256:f1784a2075457f82ef4657dfef086eaba92b0adee24ca09eca389ec0349acdd3`
