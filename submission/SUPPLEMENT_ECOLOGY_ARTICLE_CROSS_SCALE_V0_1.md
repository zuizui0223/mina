# Appendix S1

**Authors:** [SAME AUTHOR LIST AS MAIN MANUSCRIPT]

**Manuscript title:** Breeding-space concentration recurs across spatial scales in Antarctic penguins

**Journal:** Ecology

This appendix records the inferential provenance and complete bounded result tables supporting the manuscript. It introduces no new ecological endpoint.

## Section S1: Evidence provenance

The manuscript combines analyses with different inferential status.

**Table S1. Evidence layers and inferential roles.**

| Evidence layer | Status | Role in manuscript |
|---|---|---|
| Palmer Adélie concentration | discovery / post-hoc ecological extension with frozen count-error family | establishes the phenomenon within one monitoring system |
| Signy Adélie concentration | prospectively frozen after Palmer discovery | independent geographic replication |
| Signy chinstrap concentration | separately prospectively frozen | cross-species replication |
| Five-trajectory abundance–E scaling | bounded post-hoc exploration, now closed | describes timescale and candidate scaling only |
| MAPPPD regional concentration | bounded existing-data extension; regional contract frozen before regional concentration outcomes | declining subset tests abundance-linked recurrence; increasing subset constrains a decline-specific interpretation |
| Dominance-route decomposition | post-hoc descriptive | constrains mechanism; no p-values |
| Increasing MAPPPD networks | descriptive outcome with no frozen trend-asymmetry test | main interpretive boundary showing that lower E is not restricted to declining abundance trajectories |

No p-values are pooled across these evidence layers.

## Section S2: Effective breeding-component number

For every panel,

**Equation S1. Effective breeding-component number.**

\[
E_t = \frac{1}{\sum_j p_{jt}^2},
\qquad
p_{jt} = \frac{n_{jt}}{\sum_j n_{jt}}.
\]

The metric is the inverse-Simpson effective number of monitored breeding components. It is not genetic effective population size, effective number of breeders, occupied area or a count of equal-area habitat patches.

Component meanings differ among data sets:

- Palmer: stable colony-code census units within island breeding systems.
- Signy: frozen monitored breeding colonies or canonical monitoring units.
- MAPPPD: repeatedly monitored breeding sites within published APBP regions.

The manuscript therefore uses “effective monitored breeding components” unless a data-set-specific term is required.

## Section S3: Palmer fixed-composition inference

The primary Palmer analysis is restricted to Cormorant, Humble and Litchfield, the three synchronized Adélie island populations with unchanged reported colony-code rosters.

Observed first-to-last change in E:

**Table S2. Palmer fixed-composition concentration results.**

| Population | First E | Last E | Change | Slope / year | CV20 p |
|---|---:|---:|---:|---:|---:|
| Cormorant | 3.535 | 2.859 | −19.1% | −0.03098 | 0.0380 |
| Humble | 4.625 | 2.285 | −50.6% | −0.08550 | 0.000010 |
| Litchfield | 5.783 | 1.000 | −82.7% | −0.36808 | 0.000010 |

The null fixes one time-invariant cumulative component-share vector within each island, imposes each empirical island-total abundance trajectory, and adds Poisson or Gamma–Poisson count error. The severe 20%-CV sensitivity is deliberately stylized and is not an empirical estimate of observer error.

No simulated replicate among 100,000 was simultaneously as negative as all three observed slopes under CV20 (plus-one joint p = 0.000010).

## Section S4: Prospectively frozen Signy replications

### S4.1 Adélie

Primary years:

1996, 1998–2009, 2011–2019 (22 complete seasons).

Canonical units:

A1+A60, A2, A3, A4, A64.

A1, A60, A1 + A60 and A1+A60 were harmonized under a rule frozen before effect inspection because the source changed from separate to pooled reporting.

Stable-roster breeding pairs declined from 2,342 to 1,217. E declined from 3.081 to 1.936 (−37.2%), with slope −0.04396 yr−1. The one-sided probability was 0.000010 under Poisson, CV10% and CV20% nulls.

### S4.2 Chinstrap

The same 22 complete seasons were used with nine literal units:

C15, C16, C17, C18, C46, C47, C79, C80, C81.

Stable-roster breeding pairs declined from 1,642 to 581. E declined from 4.438 to 2.191 (−50.6%), with slope −0.07179 yr−1. Under CV20, one of 100,000 simulated slopes was at least as negative as observed, giving plus-one p = 0.000020.

## Section S5: Closed five-trajectory scaling exploration

The five local population trajectories gave annual log–log abundance–E elasticities:

**Table S3. Post-hoc local abundance–E elasticities.**

| Population | κ |
|---|---:|
| Cormorant Adélie | 0.069 |
| Humble Adélie | 0.203 |
| Litchfield Adélie | 0.465 |
| Signy Adélie | 0.289 |
| Signy chinstrap | 0.366 |

The descriptive population-fixed-effect common κ was 0.250; leave-one-population-out estimates ranged 0.139–0.354.

This value is not used as a universal prediction. The same bounded search showed:

- level relationship: common κ = 0.250, within-population R2 = 0.585;
- first differences: κ = 0.120, R2 = 0.071;
- no frozen 50%, 25% or 10% abundance hinge improved held-out prediction over a single log-linear relation;
- the formal transition-ratchet criterion failed;
- no tested predictor among initial E, component count, initial evenness or decline depth improved leave-one-population-out prediction of population-specific κ over an intercept-only baseline.

The search is closed.

## Section S6: MAPPPD regional support gate

Source: pinned CCheCastaldo/mapppdr commit `88c73a507e0921b2541c218c71eaf16721bc6502`.

The regional concentration extension reuses the earlier frozen Paper 2 observation cohort and calibration. Species × published APBP region is the parent monitoring network; site_id is the component.

Eligibility was determined from observation structure only:

- at least 3 retained sites;
- at least 5 seasons observed at every retained site;
- at least 10 calendar years between the first and last complete seasons.

The deterministic pruning rule removes the site with the fewest observed seasons until the first qualifying roster is reached; ties are resolved by removing the lexicographically greatest site ID. Count magnitude does not enter roster selection.

Thirteen candidate species × region groups were present; seven were eligible.

## Section S7: Complete regional panel results

**Table S4. Complete eligible MAPPPD regional network inference.**

| Species | Region | Trend | Sites | Seasons | raw κ | obs-error Δκ | p | Pass |
|---|---|---|---:|---:|---:|---:|---:|---|
| Adélie | CWAP | decline | 3 | 5 | 0.080 | +0.073 | 0.108 | no |
| Adélie | SSI | decline | 4 | 7 | 0.088 | +0.115 | 0.0148 | yes |
| Adélie | Victoria | increase | 11 | 5 | −0.358 | −0.355 | 0.766 | no |
| Chinstrap | CWAP | decline | 3 | 10 | 0.022 | +0.017 | 0.432 | no |
| Chinstrap | SSI | decline | 6 | 8 | 0.445 | +0.434 | 0.0152 | yes |
| Gentoo | CWAP | increase | 7 | 5 | −0.238 | −0.228 | 0.984 | no |
| Gentoo | SSI | increase | 5 | 7 | 0.024 | +0.020 | 0.427 | no |

CWAP = Central-west Antarctic Peninsula; SSI = South Shetland Islands. Pass = individually supported under both frozen regional nulls.

**Table S5. First and last retained endpoints for the seven eligible MAPPPD networks.**

| Species | Region | First N | Last N | First E | Last E |
|---|---|---:|---:|---:|---:|
| Adélie | CWAP | 2,279 | 559 | 1.967 | 1.733 |
| Adélie | SSI | 29,710 | 8,576 | 3.040 | 2.726 |
| Adélie | Victoria | 387,917 | 516,140 | 4.848 | 3.559 |
| Chinstrap | CWAP | 764 | 488 | 2.057 | 1.997 |
| Chinstrap | SSI | 10,539 | 3,611 | 2.469 | 1.552 |
| Gentoo | CWAP | 19,084 | 23,253 | 4.933 | 4.128 |
| Gentoo | SSI | 11,910 | 19,544 | 3.902 | 3.859 |

The four declining networks all have positive observation-error-calibrated Δκ. Two are individually supported under the panel-level support rule frozen before regional outcomes were computed. These four panel tests are not treated as a prespecified family-wise generality test, and no multiplicity-adjusted regional rejection criterion was frozen. The nominal one-sided probability of four positive signs out of four is 0.0625, but the panels are not independent geographic replicates because two species occur within each of the two declining regions. This sign probability is therefore descriptive only.

Local and regional inference also use different scale-appropriate statistics: the within-system primary tests use the temporal slope of E, whereas the regional extension uses the abundance–E elasticity κ and its panel-specific null calibration. They share the effective-component state and fixed-composition logic, but are not pooled as estimates of a common effect size or p-value.

The Central-west Antarctic Peninsula retained rosters include BISC (Biscoe Point), which is part of the broader Palmer-area APBP context but is not one of the three primary Palmer concentration populations (Cormorant, Humble and Litchfield). The MAPPPD regional analysis is therefore treated as a scale-transfer test, not as an additional independent geographic replication of Palmer. Signy supplies the independent geographic replication.

## Section S8: Increasing regional networks

All three eligible increasing networks ended with lower E than in their first retained complete season (Table S5): Adélie — Victoria Land, abundance +33.1% and E −26.6%; Gentoo — Central-west Antarctic Peninsula, abundance +21.8% and E −16.3%; and Gentoo — South Shetland Islands, abundance +64.1% and E −1.1%.

These observations are a main interpretive boundary on the regional decline-specific narrative: lower regional E is not restricted to declining abundance trajectories in the eligible panels. Their inferential status remains descriptive because no regional time-slope, decline-versus-increase asymmetry, ratchet or hysteresis endpoint was frozen before these outcomes were inspected.

## Section S9: Component-level route boundary

A post-hoc descriptive decomposition shows that the same decrease in E can arise through contrasting component histories.

At Palmer, the initially dominant colony-code unit had zero breeding pairs by the final eligible census in all three populations, and another component became dominant.

At Signy, the initially dominant unit remained dominant and increased its share:

- Adélie: 47.5% to 69.4%;
- chinstrap: 40.0% to 65.6%.

This contrast rules out a universal interpretation in which concentration necessarily means persistence of the historically largest component.

## Section S10: Claim boundary and stop rule

Supported scope:

> Replicated non-proportional concentration during decline within Palmer/Signy breeding systems, with a regional boundary showing that effective breeding-site concentration is not restricted to declining abundance trajectories.

Not supported:

- a universal Antarctic regional concentration law;
- a seabird-wide or colonial-breeder-wide rule;
- a universal κ ≈ 0.25 exponent;
- a universal large-colony refuge mechanism;
- a formal hysteresis claim;
- interpretation of APBP regions as closed demographic populations;
- causal attribution to habitat, snow, site fidelity, recruitment, movement or predation.

No further regional definitions, geographic radii, hand-built clusters, completeness thresholds, lags, nonlinear scaling families, trait screens or same-data mechanism searches are opened by this manuscript. Further generality requires an independent taxonomic data source.
