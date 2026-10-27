# V37 — Source-frozen size-dependent breeding-site share retention (H1a)

**Prepared 2026-10-27. Freeze BEFORE inspecting the new V37 site-size-versus-share-change statistic.**
**Existing known information**: JNCC V30 discovered 1,321 source-comparable panels / 17 seabird species, including 959 with lower later total and cross-taxon excess Simpson concentration. Those outcomes are already known; V37 is explicitly a **post-discovery, new-outcome exploratory test**, not an independent prospective ecological confirmation. It must NOT be mixed into frozen Penguin Ecology PR #189, UK seabird V30, Antarctic PR #197/#199 or the closed V36 physical-island/predator refuge lane.

## Single primary biological hypothesis

H1a: **Within a monitored species × Country × Master-site × original-count-unit panel whose total decreases, larger earlier-counted child Site.ID units gain or retain a larger share in the second census than conditional proportional allocation predicts.**

This is a **relative share-retention** prediction, not a prediction of site extinction, site movement, social Allee dynamics or actual nest quality. Results could be driven by habitat quality, survey method, baseline count measurement error, site-boundary changes or observational selection. The cross-species H1b density/coloniality interaction and H3 habitat quality require new independent source-verified traits/habitat and are **not fitted in V37**. Predator H2 remains STOP per frozen V36 original geography sample (three fully verified mixed-landmass parents, 0 with mink source-status variation, versus ≥20 parent/5 species requirement).

## Original frozen data gate and role of V30

- Authentic JNCC 2024-07-08 revised Seabirds Count compared with Seabird 2000 original XLSX SHA256 \`9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4\`.
- Reuse V29 unique matched child Site.ID, 5 count-unit classes (AON/AOS/AOT/AOB/IND), correct Puffin comparable sheet, V30 outcome-blind parent-name aggregate guard; keep *all source structural panels* before reading biological count magnitudes.
- V29/V30 expected structural count: 14,112 unique site×species source rows, 1,485 parent candidates, and 1,483 source parent panels after possible master-as-child duplicate exclusion. If any changes, stop.
- On source-open, counts must be nonnegative **exact integers** (no imputation or rounding); both panel totals \`N0>=2, N1>=2\`. Expected source-compatible panels **1,321**, with previously known declines **959**, 17 taxa, at least 100 eligible panels across 8 taxa / 30 Country×Master networks / 3 source biological units. Validate these before the new effect statistic.
- Use every decline panel (\`N1<N0\`) with **variation in original child count sizes**, defined by population-variance of \`log1p(n_i0)\` under original smoothed baseline allocation >0. Panels with all earlier child counts equal are mechanically uninformative for the size slope; count and report, never drop based on later shares. Minimum 100 information-bearing declining panels, ≥8 species, ≥30 Country×Master, ≥3 units. Each focal species requires at least three information-bearing decline panels for the equal-species primary statistic; report exclusions.

## Primary within-parent size score (one pre-fixed scale)

For each eligible panel g containing k≥3 identical matched Site.ID children:

- Baseline allocation \`p*_i=(n0_i+0.5)/(N0+0.5*k)\`. Exactly α=0.5 as in V32; all count-unit types remain separate. This pseudocount is **not a claim that a previously zero-count source site had half a real nest**.
- Earlier size feature \`x_i=log(1+n0_i)\`; baseline-p*-weighted mean \`μ=Σp*_i x_i\` and standard deviation \`σ=sqrt(Σp*_i (x_i−μ)^2)\`. If \`σ=0\`, mark size-uninformative; no zero substitution.
- Observed later child share \`p1_i=n1_i/N1\`. **Score**
  
  \`S_g = Σ_i (p1_i−p*_i) (x_i−μ)/σ\`.
  
  The expectation of S_g is **exactly zero** conditional on original observed n0 and later total N1 under \`n1 ~ Multinomial(N1,p*)\` (not a full ecological observation-error null). A larger child retaining disproportionately more than original baseline earns positive S. Identical earlier child size is necessarily unidentifiable.
- S is the **standardized score at β=0** for the conditional compositional offset model \`q_i(β) ∝ p*_i exp[β(x_i−μ)/σ]\`. We use the same score under every simulated null draw, which is a standard conditional score test and does **not** require refitting the nonlinear β for each simulation. **Do not reinterpret this score as a fitted causal β**.
- Equal-parent averaging **within each species**, then **equal species weighting** over species with ≥3 size-informative declines, yielding T_obs. The primary sign check is T_obs>0 and positive within-species mean scores in ≥ceil(2/3 eligible species); report country imbalance separately. Do not calculate a favorable subgroup-only primary endpoint after reading effects.
- Predeclared descriptive sensitivities: (a) apply same score to **all 1,321 eligible panels** irrespective of decline, with ≥3 per species; (b) leave-one-source-Country-out species-equal mean T, including omission of Scotland; (c) leave-one-species-out equal-species mean T. Report negative results unchanged.
- A source panel is **one compositional observation**, not k independent demographic transitions. Repeated networks across taxa share original observation context, and the 17 species are at most 17 taxonomic replication units.

## Exact null protocol and uncertainty ceilings

- Generate **1,999** fixed-seed \`numpy.random.default_rng(20261027)\` independent within-parent multinomial replicates with exactly its observed later total N1 and original \`p*\`. Calculate the **same S_g** in every replicate, then the same equal-parent/equal-species aggregate. No retuning threshold, ROI, count unit, α, taxa subset, or simulation count after seeing outcomes.
- Report T_obs, mean/5–95th quantiles of T_null, conditional Monte Carlo upper-tail fraction \`(1+#{T_null≥T_obs})/(2000)\`. **This tail is conditional on an idealized fixed-allocation experiment, not a biological p-value accounting for census effort, site-boundary histories, overdispersed counts, baseline N0 uncertainty or arbitrary ecological recruitment.**
- Report species means and raw underlying n for each species, but NOT original child-site count records, site locations or inferred movement. Include all species with insufficient panels as unsupported, not zeros.
- A sufficiently large positive score supports **size-dependent source site-share retention above a transparent arithmetic baseline**, not social aggregation unless independent site-quality, survey-method and demographic mechanisms exclude alternatives.
- If primary T≤0 or positivity/independence gates fail, declare that H1a size-advantage is not supported in this new source cohort. Do not retune score, zero smoothing, census intervals, simulation model, network/site definitions, or species clustering to rescue.

## Execution & immutability

The new V37 source/read-only script and tests must be committed alongside this frozen contract **before** the authentic JNCC V37 effect job is first executed. Synthetic tests examine q normalization, zero-baseline smoothing, sign on invented panels, finite-count null expectation and informative-panel filters without seeing actual source outcomes. Persist a compact reproducible JSON with original SHA, source gate counts, observed T, species table, conditional null bounds, all prespecified sensitivities and limitations. Keep V30, V36 and the Ecology manuscript untouched.
