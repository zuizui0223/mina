# Supporting Information — cross-scale breeding-space concentration v0.1

This supplement accompanies `docs/MANUSCRIPT_CROSS_SCALE_CONCENTRATION_V0_1.md` and records the inferential provenance and complete bounded result tables used in the manuscript. It introduces no new ecological endpoint.

## S1. Evidence provenance

The manuscript combines analyses with different inferential status.

| Evidence layer | Status | Role in manuscript |
|---|---|---|
| Palmer Adélie concentration | discovery / post-hoc ecological extension with frozen count-error family | establishes the phenomenon within one monitoring system |
| Signy Adélie concentration | prospectively frozen after Palmer discovery | independent geographic replication |
| Signy chinstrap concentration | separately prospectively frozen | cross-species replication |
| Five-trajectory abundance–E scaling | bounded post-hoc exploration, now closed | describes timescale and candidate scaling only |
| MAPPPD regional concentration | bounded existing-data extension; regional contract frozen before regional concentration outcomes | tests whether the direction transfers one spatial level upward |
| Dominance-route decomposition | post-hoc descriptive | constrains mechanism; no p-values |
| Increasing MAPPPD networks | descriptive context | evaluates qualitative consistency with a slow-state interpretation; not a hysteresis test |

No p-values are pooled across these evidence layers.

## S2. Effective breeding-component number

For every panel,

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

## S3. Palmer fixed-composition inference

The primary Palmer analysis is restricted to Cormorant, Humble and Litchfield, the three synchronized Adélie island populations with unchanged reported colony-code rosters.

Observed first-to-last change in E:

| Population | First E | Last E | Change | Slope / year | CV20 p |
|---|---:|---:|---:|---:|---:|
| Cormorant | 3.535 | 2.859 | −19.1% | −0.03098 | 0.0380 |
| Humble | 4.625 | 2.285 | −50.6% | −0.08550 | 0.000010 |
| Litchfield | 5.783 | 1.000 | −82.7% | −0.36808 | 0.000010 |

The null fixes one time-invariant cumulative component-share vector within each island, imposes each empirical island-total abundance trajectory, and adds Poisson or Gamma–Poisson count error. The severe 20%-CV sensitivity is deliberately stylized and is not an empirical estimate of observer error.

No simulated replicate among 100,000 was simultaneously as negative as all three observed slopes under CV20 (plus-one joint p = 0.000010).

## S4. Prospectively frozen Signy replications

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

## S5. Closed five-trajectory scaling exploration

The five local population trajectories gave annual log–log abundance–E elasticities:

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

## S6. MAPPPD regional support gate

Source: pinned CCheCastaldo/mapppdr commit `88c73a507e0921b2541c218c71eaf16721bc6502`.

The regional concentration extension reuses the earlier frozen Paper 2 observation cohort and calibration. Species × published APBP region is the parent monitoring network; site_id is the component.

Eligibility was determined from observation structure only:

- at least 3 retained sites;
- at least 5 seasons observed at every retained site;
- at least 10 calendar years between the first and last complete seasons.

The deterministic pruning rule removes the site with the fewest observed seasons until the first qualifying roster is reached; ties are resolved by removing the lexicographically greatest site ID. Count magnitude does not enter roster selection.

Thirteen candidate species × region groups were present; seven were eligible.

## S7. Complete regional panel results

| Species | Region | Direction | Sites | Seasons | First N | Last N | First E | Last E | raw κ | obs-error Δκ | p | Supported |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Adélie | Central-west Antarctic Peninsula | decline | 3 | 5 | 2,279 | 559 | 1.967 | 1.733 | 0.080 | +0.073 | 0.108 | no |
| Adélie | South Shetland Islands | decline | 4 | 7 | 29,710 | 8,576 | 3.040 | 2.726 | 0.088 | +0.115 | 0.0148 | yes |
| Adélie | Victoria Land | increase | 11 | 5 | 387,917 | 516,140 | 4.848 | 3.559 | −0.358 | −0.355 | 0.766 | no |
| Chinstrap | Central-west Antarctic Peninsula | decline | 3 | 10 | 764 | 488 | 2.057 | 1.997 | 0.022 | +0.017 | 0.432 | no |
| Chinstrap | South Shetland Islands | decline | 6 | 8 | 10,539 | 3,611 | 2.469 | 1.552 | 0.445 | +0.434 | 0.0152 | yes |
| Gentoo | Central-west Antarctic Peninsula | increase | 7 | 5 | 19,084 | 23,253 | 4.933 | 4.128 | −0.238 | −0.228 | 0.984 | no |
| Gentoo | South Shetland Islands | increase | 5 | 7 | 11,910 | 19,544 | 3.902 | 3.859 | 0.024 | +0.020 | 0.427 | no |

The four declining networks all have positive observation-error-calibrated Δκ. Two are individually supported under the panel-level support rule frozen before regional outcomes were computed. These four panel tests are not treated as a prespecified family-wise generality test, and no multiplicity-adjusted regional rejection criterion was frozen. The nominal one-sided probability of four positive signs out of four is 0.0625, but the panels are not independent geographic replicates because two species occur within each of the two declining regions. This sign probability is therefore descriptive only.

Local and regional inference also use different scale-appropriate statistics: the within-system primary tests use the temporal slope of E, whereas the regional extension uses the abundance–E elasticity κ and its panel-specific null calibration. They share the effective-component state and fixed-composition logic, but are not pooled as estimates of a common effect size or p-value.

## S8. Increasing regional networks

All three eligible increasing networks ended with lower E than in their first retained complete season:

| Network | Abundance change | E change |
|---|---:|---:|
| Adélie — Victoria Land | +33.1% | −26.6% |
| Gentoo — Central-west Antarctic Peninsula | +21.8% | −16.3% |
| Gentoo — South Shetland Islands | +64.1% | −1.1% |

These observations are qualitatively compatible with spatial structure changing more slowly than abundance, but no regional ratchet or hysteresis endpoint was frozen before these outcomes were inspected. They therefore remain descriptive.

## S9. Component-level route boundary

A post-hoc descriptive decomposition shows that the same decrease in E can arise through contrasting component histories.

At Palmer, the initially dominant colony-code unit had zero breeding pairs by the final eligible census in all three populations, and another component became dominant.

At Signy, the initially dominant unit remained dominant and increased its share:

- Adélie: 47.5% to 69.4%;
- chinstrap: 40.0% to 65.6%.

This contrast rules out a universal interpretation in which concentration necessarily means persistence of the historically largest component.

## S10. Claim boundary and stop rule

Supported scope:

> Cross-scale directional recurrence of abundance-conditioned breeding-space concentration within Antarctic Pygoscelis.

Not supported:

- a universal Antarctic regional concentration law;
- a seabird-wide or colonial-breeder-wide rule;
- a universal κ ≈ 0.25 exponent;
- a universal large-colony refuge mechanism;
- a formal hysteresis claim;
- interpretation of APBP regions as closed demographic populations;
- causal attribution to habitat, snow, site fidelity, recruitment, movement or predation.

No further regional definitions, geographic radii, hand-built clusters, completeness thresholds, lags, nonlinear scaling families, trait screens or same-data mechanism searches are opened by this manuscript. Further generality requires an independent taxonomic data source.
