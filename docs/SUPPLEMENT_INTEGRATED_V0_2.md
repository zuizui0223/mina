# Supporting Information — integrated Palmer–Antarctic manuscript v0.3 / JBI v0.4

## S1. Scope and inferential role

This Supporting Information documents the analyses needed to audit the main
manuscript without changing its inferential hierarchy. The two core results are:

1. Palmer Adélie decline is accompanied by within-island concentration beyond
   proportional thinning plus prespecified count error.
2. Static breeding-island architecture does not yield a confirmed transferable
   Antarctic-wide response rule.

All secondary analyses below retain their frozen interpretation boundaries. A
Supplementary result cannot replace or rescue a non-confirmatory main-text
result.

---

## S2. Data provenance and frozen analysis frames

### S2.1 Palmer census

The Palmer discovery analysis used the Palmer LTER Adélie penguin area-wide
breeding population census (DOI
10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e). The frozen downloaded file had
SHA-256
`b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16`.
The synchronized island-total panel contained five islands over 1991–2017.
Colony-code concentration analyses were restricted to Cormorant (COR), Humble
(HUM) and Litchfield (LIT), whose reported colony-code rosters remained stable
over the synchronized interval.

### S2.2 Antarctic-wide abundance data

The broad-scale analysis used MAPPPD/APBP data pinned to commit
`88c73a507e0921b2541c218c71eaf16721bc6502`. The frozen 1980–2025 breeding
season window produced 107 temporally bridged site × species units and 2,100
nest-count records. Observation metadata comprised 1,889 direct records, 149
image-based records and 62 records with unknown vantage.

After the final species-wide V3 forcing decision and primary predictor
missingness rules, the real-outcome site × species frames contained 41 Adélie,
34 chinstrap and 29 gentoo units.

### Table S1. Frozen analysis frames

| Component | Frozen size / rule |
| --- | --- |
| Palmer synchronized panel | 5 islands × 27 years |
| Palmer concentration subset | COR, HUM, LIT |
| Antarctic Gate-0 candidates | 152 site × species units |
| Antarctic bridged cohort | 107 units |
| Antarctic nest-count records | 2,100 |
| Final Adélie V3 units | 41 |
| Final chinstrap V3 units | 34 |
| Final gentoo V3 units | 29 |
| Primary breeding-landscape radius | 2 km |
| Primary heterogeneity metric | Tier-2 Habitat Complex richness |

---

## S3. Palmer concentration analysis and count-error nulls

For each island-year, effective colony number was

\[
N_{\mathrm{eff}}=\frac{1}{\sum_j p_j^2},
\]

where \(p_j\) is the fraction of breeding pairs assigned to colony code \(j\).
The observed statistic was the OLS slope of annual
\(N_{\mathrm{eff}}\) against centered calendar year.

The fixed-composition null preserved each observed island-total trajectory while
holding latent colony composition constant. Expected colony counts were then
subjected to Poisson error or Gamma–Poisson error with frozen 10% and 20%
multiplicative CV sensitivities. Each error model used 100,000 realizations.

### Table S2. Palmer concentration results

| Island | First \(N_{\mathrm{eff}}\) | Last \(N_{\mathrm{eff}}\) | Fractional change | Observed slope yr⁻¹ | Poisson p | CV10 p | CV20 p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| COR | 3.535 | 2.859 | −0.191 | −0.03098 | 0.01215 | 0.01941 | 0.03800 |
| HUM | 4.625 | 2.285 | −0.506 | −0.08550 | 0.000010 | 0.000010 | 0.000010 |
| LIT | 5.783 | 1.000 | −0.827 | −0.36808 | 0.000010 | 0.000010 | 0.000010 |

The joint three-island plus-one probability was 0.000010 under Poisson,
Gamma–Poisson CV10 and Gamma–Poisson CV20. Therefore the concentration result
survives the full frozen independent count-error family. The CV values are
stress tests and are not estimates of actual observer error.

Independent Torgersen mapping provides phenomenon-level spatial triangulation:
23 historic active subcolonies were reduced to five active footprints by 2022.
All historic south-aspect footprints were extinct, versus a south-minus-north
extinction-fraction difference of 0.385. The historic area–extinction-year
correlation was \(R=0.75\) (reported source p = 0.0009). Because the
colony-code/polygon crosswalk is unresolved, these results validate the spatial
phenomenon rather than individual census identifiers.

---

## S4. Palmer secondary demographic diagnostics

### S4.1 Effective colony number and next-year growth

A frozen conditional analysis retained a positive standardized coefficient
between effective colony number and next-year growth
(\(\beta=0.1168\)). Structured circular-shift nulls showed that the observed
coefficient was unusual (independent-island shift p = 0.000010; exact
joint-shift p = 1/416 = 0.002404).

The held-out predictive result did **not** survive its primary year-block
permutation. The observed leave-one-year-out MSE gain was 0.001029, whereas the
one-sided permutation p-value was 0.2622. Thus the manuscript may describe a
conditional association but not a validated out-of-year predictor.

### S4.2 Hierarchical variability

On the stable-roster islands, raw multiplicative temporal beta was

- within islands: 1.0737;
- among islands: 1.0112;
- total subcolony-to-archipelago: 1.0858.

Approximately 86.4% of the log-beta reduction occurred within islands in the
raw decomposition. However, the hierarchy is measurement-error sensitive.
Under Poisson and Gamma–Poisson CV10 simulations, the raw within-versus-among
contrast was far more extreme than expected (p = 0.000010). Under the frozen
Gamma–Poisson CV20 stress test, the raw log-beta contrast was compatible with
the null (p = 0.4475). Detrended and annual-growth variants also failed to
provide a measurement-error-robust rescue.

Accordingly, hierarchical beta is descriptive context and is not a primary
buffering result.

### S4.3 Environmental diagnostics

Sea-ice and weather analyses are retained only as contextual diagnostics. They
do not identify a cause of Palmer concentration, and the latent Antarctic-wide
species forcing is not equated with any specific environmental driver.

---

## S5. Antarctic-wide observation model and pre-outcome gates

### S5.1 Observation-overlap audit

The outcome-blind metadata audit identified 1,721 site × species × season
groups, of which 273 had repeated records. There were 41 groups containing both
direct and image-based records:

- Adélie: 9;
- chinstrap: 10;
- gentoo: 22.

There were 92 known-date direct–image pairs, including 23 exact-date pairs and
53 pairs separated by no more than 14 days.

The primary observation model was frozen as:

- direct counts as the reference method;
- one shared image-based mean offset;
- accuracy class 1 versus pooled classes 2–5 for observation precision;
- unknown-vantage records retained without their own method offset;
- exclusion of unknown vantage and raw-ground-only fits as sensitivities.

### S5.2 Synthetic observation recovery

Using the real 2,100-record metadata layout and 200 synthetic replicates, the
shared image offset and two accuracy scales were recoverable. The simulated
image offset truth was log(1.15) = 0.13976 and the median recovered value was
0.13867 (bias −0.00109). The correct offset sign was recovered in 100% of
replicates.

Accuracy-scale recovery was also close to the frozen truth:

| Accuracy group | Truth log-SD | Median recovered log-SD | Relative bias |
| --- | ---: | ---: | ---: |
| 1 | 0.04879 | 0.04902 | +0.47% |
| 2–5 | 0.22314 | 0.21846 | −2.10% |

### S5.3 Predictor identifiability before outcomes

Before demographic count magnitudes were opened, the candidate A × H design
was checked for numerical and geographic support. In the regional candidate
frames, the complete-predictor sample contained 40 Adélie, 33 chinstrap and 28
gentoo units. Interaction VIF values were 2.26, 1.25 and 1.19, respectively;
condition numbers were 3.72, 4.03 and 4.32. Every species had at least four
units in each A/H sign quadrant.

These checks established estimability only; they did not imply that an
ecological effect existed.

---

## S6. Evolution of the Antarctic-wide estimator

The final estimator was selected through pre-outcome recovery, not through
fit to the real demographic effects.

### Table S3. Pre-outcome estimator/gate history

| Stage | Purpose | Frozen result | Consequence |
| --- | --- | --- | --- |
| Observation overlap | identify nuisance structure | shared image offset identifiable | direct reference + one image offset |
| Predictor audit | ensure A × H estimability | full rank; low VIF | interaction retained as testable |
| Latent schedule recovery | recover shared forcing/loadings on real seasons | regional pass for ADPE/CHPE; GEPE regional failure | GEPE initially fell back species-wide |
| Observation recovery | recover offset/accuracy on real metadata | all frozen checks passed | observation layer retained |
| Integrated V1 | combine process + observation | failed | estimator rejected; thresholds not relaxed |
| Hierarchical V2 | fit trait effects inside loading model | species-wide recovery passed all 3 species | species-wide forcing retained |
| Spatially adjusted V3 | protect traits from broad geography | all frozen recovery checks passed | final estimator |
| Cross-species V4 | validate paper-level median estimand | passed | median \(\gamma_{AH}\) retained |
| H-main V5 | validate nonzero H recovery | passed all 3 species | marginal-slope classification permitted |
| Source robustness | exclude-unknown / raw-ground recovery | paper-level robustness passed | real-outcome gate satisfied |

The important transition occurred at hierarchical V2. Regional integrated
configurations failed the unchanged recovery criteria for Adélie and chinstrap,
whereas species-wide configurations passed for all three species. This is why
the final model uses a species-wide latent annual factor. It is an
identifiability/model-resolution decision and is **not** evidence for biological
synchrony at the full species-range scale.

V3 retained geography separately as loading-adjustment strata:

- Adélie: CCAMLR blocks (25, 15 and 1 unit);
- chinstrap: APBP regions (18, 15 and 1 unit);
- gentoo: APBP regions (21, 7 and 1 unit).

In pre-outcome V3 recovery, median forcing correlations were 0.847, 0.869 and
0.893 for Adélie, chinstrap and gentoo. A common crossover truth of
\(\gamma_{AH}=-0.35\) was recovered with median estimates −0.356, −0.359 and
−0.320 and negative-sign fractions 0.92, 1.00 and 0.99.

Residual process-SD estimates frequently reached the frozen profiling floor in
recovery and real fits. Residual process variance is therefore not interpreted
ecologically anywhere in the manuscript.

---

## S7. Primary Antarctic-wide permutation inference

The real 2 km richness-model interaction estimates were:

| Species | \(\gamma_{AH}\) | Raw p | Holm p | Full point-estimate crossover |
| --- | ---: | ---: | ---: | --- |
| Adélie | −0.3036 | 0.2162 | 0.2162 | No |
| Chinstrap | −1.1844 | 0.0661 | 0.1689 | Yes |
| Gentoo | −0.3182 | 0.0563 | 0.1689 | Yes |

The paper-level statistic was the median interaction across the three species,
−0.3182. In 9,999 block-preserving permutations, 946 permuted statistics were
at least as negative, yielding a plus-one one-sided p-value of 0.0947. The
permutation distribution had median 0.0027, 5% quantile −0.4235 and 95%
quantile 0.3664.

All three point estimates are negative, but neither the paper-level test nor any
Holm-adjusted species-specific test rejects its frozen null.

---

## S8. Prespecified secondary breeding-space analysis

The A-only estimates were negative in all three species:

| Species | \(\gamma_A\) | Raw one-sided p | Holm p |
| --- | ---: | ---: | ---: |
| Adélie | −0.2804 | 0.1426 | 0.4278 |
| Chinstrap | −0.2005 | 0.4225 | 0.6134 |
| Gentoo | −0.0706 | 0.3067 | 0.6134 |

No species-specific test was supported after the frozen Holm correction.
H-only estimates were descriptive only (Adélie +0.294, chinstrap +0.518,
gentoo −0.006); no directional H-only inference was preregistered.

---

## S9. Observation-timing and source sensitivities

### S9.1 Timing-matched image offsets

The primary same-season image/direct multiplicative factor was 1.040.
Timing-matched estimates were:

| Calibration | Pairs | Image/direct factor | Cross-species median \(\gamma_{AH}\) |
| --- | ---: | ---: | ---: |
| Same season, primary | — | 1.040 | −0.318 |
| Exact date | 23 | 1.069 | −0.326 |
| Within 14 days | 53 | 1.058 | −0.323 |

All three species retained negative interaction estimates under the two
timing-matched sensitivities; chinstrap and gentoo retained the full
point-estimate crossover classification.

### S9.2 Observation-source recovery boundary

Before real outcomes were opened, the paper-level cross-species interaction
estimand remained recoverable after excluding unknown-vantage records. The
partial raw-ground-only recovery also passed for its two outcome-blind testable
species (chinstrap and gentoo). Adélie raw-ground support was coverage-limited
and was frozen as nonblocking.

The Adélie species-specific exclude-unknown sign-recovery rate did not satisfy a
stricter species-level threshold in an earlier sensitivity. That limitation is
not erased by the paper-level robustness gate and is why universal
species-specific wording is prohibited.

---

## S10. Spatial-support and heterogeneity-metric sensitivities

The primary 2 km richness analysis was not replaced by any sensitivity.

| Variant | Cross-species median \(\gamma_{AH}\) | Negative species | Full crossover species |
| --- | ---: | ---: | --- |
| 1 km richness | −0.0577 | 2/3 | Gentoo |
| 2 km richness, primary | −0.3182 | 3/3 | Chinstrap, Gentoo |
| 5 km richness | +0.1068 | 0/3 | None |
| 2 km Shannon | −0.1635 | 2/3 | Chinstrap, Gentoo |

### S10.1 Joint multi-radius null

The raw radius change was evaluated with a joint block-preserving permutation
that moved each site's complete 1/2/5 km trait tuple together. Across 9,999
permutations:

| Diagnostic | Plus-one probability |
| --- | ---: |
| 2 km negative → 5 km positive sign switch | 0.2478 |
| 5 km − 2 km contrast ≥ observed 0.425 | 0.0971 |
| Joint sign switch + observed-size contrast | **0.0810** |
| Total 1/2/5 km range ≥ observed | 0.2645 |
| Order 2 km < 1 km < 5 km plus observed-size range | 0.0765 |

The prespecified biological scale-dependence criterion required the joint
probability to be at most 0.05. It was not met. Radius variation is therefore a
robustness limitation, not an ecological scale-dependence discovery.

---

## S11. Retrospective detectable-effect analysis

The realized 5% lower tail of the primary 9,999-permutation reference was about
−0.424. The unchanged V3 model and real observation layout were then simulated
with a common three-species interaction over a frozen effect grid.

### Table S4. Detection probability for a common interaction

| True \(\gamma_{AH}\) | Detection fraction | Wilson 95% interval |
| ---: | ---: | --- |
| −0.20 | 0.000 | 0.000–0.013 |
| −0.25 | 0.0367 | 0.021–0.064 |
| −0.30 | 0.0467 | 0.028–0.077 |
| −0.35 | 0.1167 | 0.085–0.158 |
| −0.40 | 0.3800 | 0.327–0.436 |
| −0.45 | 0.5967 | 0.540–0.651 |
| −0.50 | 0.8100 | 0.762–0.850 |
| −0.55 | 0.9267 | 0.891–0.951 |
| −0.60 | 0.9667 | 0.940–0.982 |

The isotonic-interpolated retrospective thresholds were
\(|\gamma_{AH}|=0.4977\) for 80% detection and 0.5386 for 90% detection.
The observed absolute cross-species median (0.3182) is approximately 64% of
MDE80.

This is an operating characteristic, not an equivalence test or confidence
bound. Moderate common effects around the observed magnitude remain poorly
resolved, whereas a very large shared effect around 0.50–0.55 would usually
have been detected.

---

## S12. Palmer reproductive-denominator semantics audit

A post-outcome measurement-semantics audit was conducted to prevent a false
mechanistic interpretation of Palmer concentration.

The independent adult-pair and legacy chick-table pair fields matched exactly
for only 37 records (4.7%). The median absolute difference was 11 pairs and the
median difference relative to the independent adult count was 28.4%. Chicks
exceeded twice the legacy chick-table pair denominator in 21.95% of usable
rows, compared with 1.27% when the independent adult denominator was used.

On a common 95-island-season / 727-colony-row frame, a pooled positive
count-space association between colony size and chick allocation was present
with either denominator:

- independent adult denominator: \(\beta=0.0455\), multiplicative change
  1.0465 per 1 SD;
- legacy chick-table denominator: \(\beta=0.0433\), multiplicative change
  1.0442 per 1 SD.

However, island-specific effects differed in sign and the effect was not robust
to every leave-one-island-out check or to the strongest frozen unstructured
overdispersion sensitivity. A ratio regression using the legacy same-denominator
quantity was nearly null, illustrating that the ratio and count-space models
are different estimands and highly sensitive to denominator semantics.

A zero-boundary audit showed that small-first disappearance was compatible with
proportional zero-hitting rather than evidence for an Allee or predation
mechanism. Pre-extinction chick success was also non-confirmatory
(one-sided p = 0.0626; four events across three event-bearing risk sets).

Therefore the integrated manuscript does **not** claim that larger groups
universally rear more chicks per pair, that reproductive failure causes
concentration, or that an Allee mechanism has been identified.

---

## S13. Palmer performance-linked redistribution and independent Signy transfer test

This section reports the secondary dynamic-state analyses retained in manuscript
v0.3. They sharpen the information-transfer interpretation but do not replace
either core result.

### S13.1 Palmer fixed-specification lag profile

Relative colony reproductive performance was defined as chick output relative
to a size-proportional within-island expectation and standardized within
island-season. Under the repaired fixed specification, performance in season
t predicted relative colony redistribution during later intervals as follows:

| Lag | beta | one-sided permutation p | Interpretation |
| ---: | ---: | ---: | --- |
| 1 | 0.1004 | 0.000010 | descriptive; mechanically coupled to predictor-year adult census |
| 2 | **0.0409** | **0.00327** | bias-resistant primary endpoint |
| 3 | **0.0511** | **0.00136** | positive short-lag extension |
| 4 | 0.0223 | 0.121 | unsupported |
| 5 | -0.0148 | 0.770 | unsupported |

The delayed-recruitment-echo contrast comparing lags 4–5 with lags 2–3 was
negative and unsupported. The Palmer result is therefore short-lived rather
than a 4–5 year recruitment echo.

Provenance boundary: the chick-season key was repaired after Palmer lag
coefficients had already been exposed. These coefficients are fixed-specification
validation, **not** a fully preregistered confirmatory result.

### S13.2 Performance-state memory

Measured performance state had weak one- to two-year persistence:

- lag-1 rho = **0.0639**, p = **0.0258**;
- lag-2 rho = **0.0532**, p = **0.0485**;
- lag-3 rho = 0.0479, p = 0.0586.

A bridge diagnostic tested whether past performance retained information about
lag-2 redistribution after measured current performance, outcome-interval group
size and persistent colony identity were included. The past-performance
coefficient remained positive (**0.0296**, p = **0.00726**).

This pattern is consistent with layered local dynamics in which persistent
habitat/state effects coexist with short-lived demographic memory. It does not
identify causal mediation, public-information use, prospecting or individual
breeding dispersal.

### S13.3 Prospectively frozen Palmer P1–P3 mechanism follow-up

Three new endpoints were frozen before their values were computed.

**P1 — poor-performance breeder share and later island-total growth.**
The coefficient was +0.0275. The frozen meaningful-negative-effect decision was
compatible with redistribution or replacement rather than a biologically
meaningful island-total loss. However, direct poor-loss/good-gain accounting did
not show simple one-for-one compensation; the median compensation ratio was 0.

**P2 — island-level reproductive performance and later island-total growth.**
The coefficient was +0.0578, but the frozen meaningful-effect decision was
inconclusive. The analysis therefore does not establish islands as closed
redistribution units.

**P3 — lose-switch asymmetry.**
The primary hinge contrast was
\(\Delta=\beta_{loss}-\beta_{win}=-0.0126\), with one-sided
p = **0.579**. Leave-one-island-out and alternate-metric sensitivities did not
support the prespecified positive asymmetry.

The specific win-stay/lose-switch mechanism is therefore unsupported.

### S13.4 Independent frozen Signy replication

The independent transfer test used the BAS/NERC dataset
“Population size and breeding success of Adelie penguins on Signy Island from
1978 to 2020” (Dunn et al. 2021; DOI
`10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d`).

The primary window was frozen to the CCAMLR-standard 1996/97–2019/20 period.
Before any Signy effect was computed, the support gate confirmed 22 predictor
seasons, nine literal colony labels and 153 candidate lag-2 rows. The final
primary model retained 118 complete lag-2 rows across 17 predictor seasons.

| Signy analysis | beta / delta | one-sided p | Frozen decision |
| --- | ---: | ---: | --- |
| Primary lag-2 | **beta = 0.0213** | **0.279** | not replicated |
| Atomic-label-only lag-2 | beta = 0.0634 | 0.0603 | unsupported sensitivity |
| Comment-flag-exclusion lag-2 | beta = 0.0727 | 0.0207 | supported sensitivity only |
| Primary lose-switch hinge | delta = 0.0678 | 0.301 | unsupported |

The positive comment-filter sensitivity cannot replace the null frozen primary
replication. The Palmer lag-2 signal is therefore not established as a
transferable Antarctic mechanism.

### S13.5 Dynamic-transfer claim boundary

The combined Palmer–Signy evidence permits only the following statement:

> relative reproductive state can carry short-lived local information about
> redistribution at Palmer, but the corresponding frozen primary association
> did not independently replicate at Signy.

Do not claim:

- a general win-stay/lose-switch mechanism;
- observed movement of individual adults among colonies;
- island-scale demographic closure;
- public-information use or prospecting;
- a positive independent replication at Signy — **do not call Signy a positive independent replication**;
- that the Signy comment-filter sensitivity rescues the null primary test — it **cannot replace the null frozen Signy primary result**.

---

## S14. Reproducibility and analyses intentionally excluded from the manuscript

Every primary or secondary numerical claim above maps to a committed JSON
receipt and frozen code path in the `mina` repository. Failed candidate
estimators are retained in the development history rather than being silently
discarded.

One later Palmer analysis remains outside this Supplement version:

1. post-outcome size-ordered colony-code extinction hazard (PR #102).

The fixed-specification performance-linked lag analysis, memory audit,
prospectively frozen P1–P3 mechanism follow-up and independent Signy replication
are retained in S13 with their provenance and null-result boundaries explicit.
They sharpen the transferability interpretation but do not alter the integrated
manuscript's core inference.

---

## Additional reproducibility material

No additional Supplementary figure is required for the scientific claims in
this version. The complete diagnostic outputs underlying the summarized
secondary analyses are preserved as committed JSON receipts and reproducible
workflow artifacts in the archived analysis repository. In particular, the
repository retains:

- full Palmer count-error null distributions;
- N_eff association and permutation diagnostics;
- hierarchical beta/count-error outputs;
- the complete Paper 2 gate pass/fail history;
- observation-overlap and timing-calibration outputs;
- species-specific marginal-slope fits;
- the complete 9,999-permutation radius-null distribution; and
- the full retrospective detectable-effect grid;
- Palmer lag-profile, performance-memory and P1–P3 mechanism receipts; and
- the complete Signy support and replication receipts.

This choice keeps the submitted Supporting Information focused on methods,
numerical audit tables and inferential boundaries rather than duplicating
development diagnostics already available in machine-readable form.

### Supplement terminal rule

This Supplement exists to make the inferential history auditable. No
Supplementary analysis changes the main manuscript's frozen conclusions:
Palmer concentration is strongly supported; the Antarctic-wide A × H rule is
non-confirmatory; simple A-only buffering is unsupported; moderate common
interactions remain unresolved; and the apparent cross-radius sign reversal is
not treated as biological scale dependence.
