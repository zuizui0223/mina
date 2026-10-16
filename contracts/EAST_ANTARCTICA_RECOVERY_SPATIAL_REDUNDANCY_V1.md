# East Antarctic recovery spatial-redundancy test v1

**Status:** pre-effect contract. Frozen after reading only publication-level design and aggregate summaries from Southwell et al. (2015), and before extracting the 99 site-level historical/recent population values from Supporting Information.

## Independent system

Southwell et al. (2015), *Spatially Extensive Standardized Surveys Reveal Widespread, Multi-Decadal Increase in East Antarctic Adélie Penguin Populations*, PLOS ONE, DOI `10.1371/journal.pone.0139877`.

The published design contains 99 repeat-survey breeding sites distributed among five spatially distinct East Antarctic regional populations:

- Syowa
- Mawson
- Davis
- Casey
- Dumont d'Urville

The paper reports, at aggregate level and therefore known before this contract:

- the same 99 sites increased from approximately 520,050 to 878,308 breeding pairs;
- all five regional populations increased;
- 84/99 local populations increased and 15 decreased;
- local annual growth rates ranged from -5.8% to +11.4%.

No site-level historical or recent abundance values are to be inspected until this contract is committed.

## Biological question

When an Adélie regional population recovers numerically, does spatial redundancy recover with it?

Ross Island generated the unexpected pattern:

    total abundance strongly up
    all fixed colonies up
    effective colony number down

The East Antarctic system tests whether recovery concentration by **differential amplification** recurs outside the Ross Sea.

## Fixed units

Primary units are the 99 publication-defined breeding sites.

Primary grouping is the five publication-defined regional populations.

A breeding site is treated exactly as defined by Southwell et al.: a distinct geographic feature such as an island or continental-rock outcrop where Adélie penguins breed.

No post-effect regrouping, island merging, or splitting is allowed.

## Fixed endpoints

For site i in region r, use the publication's standardized historical and recent point estimates:

    n_i0 = historical standardized breeding-pair estimate
    n_i1 = recent standardized breeding-pair estimate

For each region r:

    N_r0 = sum_i n_i0
    N_r1 = sum_i n_i1

    p_ir0 = n_i0 / N_r0
    p_ir1 = n_i1 / N_r1

    E_r0 = 1 / sum_i p_ir0^2
    E_r1 = 1 / sum_i p_ir1^2

Primary effect:

    delta_logE_r = log(E_r1 / E_r0)

Also calculate an all-99-site descriptive E using the same formula.

## Proportional-growth reference

For each region, hold historical composition fixed and scale it to the recent regional total:

    expected_i1 = N_r1 * p_ir0

    residual_i = n_i1 - expected_i1

A site with residual > 0 gained more breeders than expected under exactly proportional regional recovery.

This is deterministic and carries no Monte Carlo p-value.

## Mass-balance decomposition

For every region report:

    gross_gain = sum max(n_i1 - n_i0, 0)
    gross_loss = sum max(n_i0 - n_i1, 0)

and:

    gain_loss_ratio = gross_gain / gross_loss

with infinity reported when gross_loss = 0.

Also report:

- fraction of sites increasing;
- fraction decreasing;
- share of gross gain occurring in the historically largest quartile of sites;
- the same share expected under proportional growth.

The quartile comparison is descriptive and secondary.

## Frozen predictions

### H1 — numerical recovery does not guarantee spatial recovery

Eligibility is already satisfied at publication level because all five regional totals increased.

The primary directional prediction generated from Ross is:

    median_r(delta_logE_r) < 0

That is, across the five independent regional populations, the typical recovery should show reduced effective site number.

This is a deliberately risky prediction. A positive or zero median falsifies the Ross-style generalization.

### H2 — concentration, where present, is amplification-dominated

For any region with delta_logE_r < 0 and N_r1 > N_r0:

- gross gains should exceed gross losses;
- concentration should therefore be attributable primarily to unequal positive growth rather than net site attrition.

Because the publication already states that 15/99 sites declined, this hypothesis does **not** require every site to increase.

### H3 — recovery mode can vary among regions

Report all five regional signs even if H1 succeeds.

- delta_logE < 0: differential amplification / concentration candidate;
- delta_logE approximately 0: proportional spatial recovery;
- delta_logE > 0: deconcentrating recovery candidate.

No region may be dropped because it conflicts with the generated Ross pattern.

## No baseline-size regression as a primary test

Do not use growth ratio `n_i1/n_i0` regressed on `n_i0` as a primary mechanism test because the baseline occurs on both sides and can induce regression-to-the-mean artifacts.

Likewise, do not infer density dependence from a simple baseline-size versus growth correlation.

## Decision hierarchy

Strong external support for a general recovery-concentration tendency requires:

1. all five published regional totals are represented using their fixed site rosters;
2. the median regional delta_logE is < 0;
3. at least three of five regional delta_logE values are < 0;
4. regions with E decline are gain-dominated rather than merely reflecting widespread site disappearance.

If conditions 2-3 fail, Ross recovery concentration is treated as a local or conditional pattern rather than a general recovery rule.

## Relation to the mechanism hypothesis

This test addresses **generality of the spatial outcome**, not its mechanism.

If recovery concentration generalizes, subsequent work may ask whether colony/site demographic quality predicts the proportional residuals.

If it does not generalize, that strengthens the two-mode hypothesis in which local quality and dynamic capacity determine whether recovery concentrates or spreads.

## Boundaries

- Historical and recent estimates come from heterogeneous field methods that Southwell et al. standardized; this analysis inherits their uncertainty and standardization assumptions.
- The primary analysis uses published point estimates. Publication-reported uncertainty may be propagated only in a separately labeled sensitivity analysis.
- First/last comparison does not identify individual dispersal.
- Site persistence or disappearance is not interpreted as colonisation/extinction without search-history evidence.
- This contract is independent of Paper 1 and does not retroactively alter Ross V2 decisions.
