# Ross differential recovery — causal process map v1

**Date:** 2026-10-07  
**Status:** future mechanism lane; outside frozen Ecology submission.

## Target quantity

For colony \(i\),

\[
q_i=\frac{\text{2001→2002 rebound}}{\text{1999→2001 loss}}.
\]

At three-colony grain:

\[
q_{\mathrm{Crozier}}=1.052,\quad
q_{\mathrm{Bird}}=0.683,\quad
q_{\mathrm{Royds}}=0.387.
\]

The objective is to explain variation in \(q_i\), not merely its weighted aggregate.

---

## Causal decomposition

Observed breeding-pair count near 1 December can be represented conceptually as

\[
B_{i,t}
=
A_{i,t}
\times
P_{i,t}
\times
O_{i,t},
\]

where:

- \(A_{i,t}\): adults / recruits alive and locally available to breed;
- \(P_{i,t}\): probability of entering and persisting in the breeding state through census;
- \(O_{i,t}\): probability that a breeding territory is observable/occupied at the census date.

This is only a conceptual factorization, not an estimated statistical model.

A longer-term breeding population also depends on the demographic pipeline:

\[
A_{i,t+1}
=
f(
S_i,
R_i,
F_i,
D_i,
M_i,
H_i,
X_t
),
\]

with:
- \(S\): survival;
- \(R\): recruitment;
- \(F\): reproductive output;
- \(D\): density-dependent costs/benefits;
- \(M\): movement;
- \(H\): habitat / nesting geometry;
- \(X\): environmental state.

---

## Fast causal graph: focal rebound

    iceberg position + fast ice
              |
              v
    open-water / polynya access cost
              |
       +------+------+
       |             |
       v             v
    arrival       foraging/body
    timing         condition
       |             |
       +------v------+
              |
              v
      breeding propensity
              |
              v
       occupied territories
              |
              v
      Dec-1 breeding count

Parallel fast routes:

    pre-existing prebreeder age structure
              |
              v
      recruitment in 2002
              |
              v
      breeding count

    iceberg / colony conditions
              |
              v
      breeder dispersal / emigration
              |
              v
      breeding count

    adult survival
              |
              v
      locally available breeders
              |
              v
      breeding count

---

## Slow causal graph: persistent divergence

    initial disturbance
          |
          v
    colony shrinkage
          |
          v
    subcolony fragmentation
          |
          +----------------------+
          |                      |
          v                      v
    perimeter:area ↑       social information ↓
          |                      |
          v                      v
    edge predation ↑       site-fidelity trap
          |                      |
          +----------v-----------+
                     |
                     v
             reproductive success ↓
                     |
              3–7 year lag
                     |
                     v
               recruitment ↓
                     |
                     v
            persistent low growth

Opposing large-colony pathway:

    colony size ↑
       |
       +--------------------+
       |                    |
       v                    v
    food competition ↑    compact nesting / predator dilution ↑
       |                    |
       v                    v
    foraging cost ↑       reproductive success ↑
       |                    |
       +--------- balance --+
                 |
                 v
        integrated local growth

---

## Disturbance-induced limiting-factor switch

### Normal years

Candidate dominant constraint:

> **negative density dependence through central-place foraging and local prey competition**

Prediction:
- large Crozier should pay greater energetic costs;
- smaller Royds/Bird can have shorter/easier foraging under favorable access.

Published evidence is consistent with this: chick mass and foraging efficiency show costs of large colony size / local prey depletion.

### Iceberg years

Candidate dominant constraints:

> **access reliability + breeding participation + small-colony fragmentation**

Prediction:
- the usual foraging advantage of small colonies is overwhelmed;
- Royds is disproportionately penalized by access and fragmentation;
- Crozier remains costly in terms of competition but less vulnerable to the same access/social bottlenecks.

The disturbance therefore changes the **identity of the limiting factor**, not merely its magnitude.

---

## Additional candidate modifiers

### Phenological slack

Ross Island colony breeding schedules differ substantially; Crozier is closest to wintering areas and Royds is the southernmost colony.

An extreme delay in arrival/access may therefore have unequal fitness consequences because the southern breeding season has little room for compensatory delay.

Prediction:
- colonies with less phenological slack should show stronger skipping / early failure under access disturbance.

### Age and experience

Older Adélie penguins forage more efficiently, and reproductive experience can affect performance.

If colony age structures differ, environmental stress can turn age structure into a resilience mechanism.

Status:
- plausible;
- no colony-specific focal-year age distribution yet linked to q_i.

### Sex composition

Male-biased breeder sex ratios vary among Ross colonies.

Potential mechanisms:
- mate limitation;
- sex-specific foraging efficiency;
- sex-specific recruitment/dispersal.

Status:
- secondary;
- long-run sex-ratio ranking does not reproduce focal recovery ranking.

### Individual-quality filtering

Extreme conditions reduce behavioral plasticity and can expose between-individual differences in performance.

Chronic high competition at Crozier may select for efficient/experienced breeders, creating a possible “filtering before disturbance” effect.

Status:
- biologically interesting but not directly demonstrated across colonies.

### Marine predator/prey interactions

Potential modifiers:
- leopard seal predation;
- cetacean competition;
- local prey depletion;
- marginal-ice-zone prey concentration.

Status:
- likely contributes to foraging costs;
- focal colony-specific causal evidence insufficient.

### Human disturbance

No current evidence suggests that human activity explains the focal Crozier > Bird > Royds recovery order.

Keep low priority unless independent evidence emerges.

---

## Mechanism ranking by focal explanatory value

### Tier A — strongest for 2001→2002

1. **access geometry / persistence of fast ice**
2. **arrival + breeding propensity**
3. **age-specific recruitment of pre-existing prebreeders**
4. **disturbance-induced movement / Royds emigration**

### Tier B — partial fast explanation

5. adult survival
6. phenological slack
7. age/experience composition
8. sex composition

### Tier A — strongest for multi-year divergence

1. **fragmentation → edge-predation / Allee feedback**
2. **reproductive success → delayed cohort recruitment**
3. **site fidelity preserving suboptimal fragmented states**
4. **opposing positive and negative density dependence**

### Tier B — multi-year modifiers

5. metapopulation movement
6. foraging competition / prey depletion
7. age/sex pipeline
8. Beaufort capacity changing regional dispersal

---

## Falsifiable predictions

### H1. Access-gating hypothesis

\[
q_i \downarrow \quad \text{as access cost / distance to open water increases.}
\]

Strongest expected under iceberg years.

### H2. Limiting-factor-switch hypothesis

\[
\frac{\partial r_i}{\partial N_i}
\]

changes with disturbance regime.

Prediction:
- normal years: larger colony size carries stronger competition costs;
- extreme access years: small-colony vulnerability / positive-density feedback dominates.

### H3. Fragmentation-trap hypothesis

A sharp breeding-population crash should predict persistent low growth through increased perimeter:area and predator exposure, even after physical access improves.

Expected strongest at Royds.

### H4. Recruitment-pipeline hypothesis

Iceberg-era reproductive failure should appear again several years later as reduced recruitment because first breeding occurs after a multi-year delay.

### H5. Movement-escape hypothesis

Colonies with the strongest local productivity/access deterioration should show greater emigration or prospecting elsewhere.

Expected strongest at Royds during iceberg years.

### H6. Quality-filtering hypothesis

Under extreme conditions, recovery should be disproportionately carried by experienced/high-efficiency individuals if environmental plasticity becomes constrained.

---

## What would distinguish the hypotheses

| Observation | Access gate | Recruitment | Survival | Fragmentation/Allee | Movement | Foraging competition |
|---|---:|---:|---:|---:|---:|---:|
| Immediate 1-year rebound | High | Medium | Medium | Low–medium | Medium | Medium |
| Royds uniquely weak | High | Medium | High | High | High | Low |
| Crozier > Bird | Medium–high | High | Low | Medium | Low–medium | **Opposite prediction if acting alone** |
| Persistence after access returns | Low alone | High | Medium | **High** | Medium | Medium |
| 3–7 yr delayed effect | Low | **High** | Medium | High through reproduction | Medium | Medium |

No single candidate explains every row.

---

## Main synthesis

The strongest mechanistic story is therefore two-stage:

> **The iceberg first created colony-specific access and breeding-participation shocks; those short-term differences were then amplified or prolonged by colony-specific demographic and social feedbacks.**

The deeper hypothesis is:

> **extreme disturbance changes which form of density dependence dominates.**

That can produce a rank reversal in apparent colony quality:

- a large colony that is costly under normal competition can be resilient under access disturbance;
- a small colony that performs well when access is easy can become trapped after fragmentation.

This is the most promising route beyond the descriptive path/state paper.
