# Global emperor penguin decline spatial-redundancy test v1

**Status:** pre-effect contract. Frozen before opening colony-level posterior abundance-index magnitudes in the public LaRue et al. global emperor penguin model output.

## Independent system

LaRue et al. global emperor penguin (*Aptenodytes forsteri*) population analysis.

Open repository:

    davidiles/EMPE_Global

Open Dryad DOI:

    10.5061/dryad.m63xsj48v

The associated publication estimates annual colony-level abundance indices across the global emperor penguin breeding distribution and independently reports an overall decline between 2009 and 2018.

Publication-level known result before this contract:

    global posterior median change ≈ -9.6% from 2009 to 2018
    uncertainty includes zero.

The colony-level spatial distribution of that change is not inspected before this contract.

## Biological question

During a global decline in a colonial penguin, does abundance-weighted spatial redundancy decrease, increase, or remain approximately stable?

This is an external test of whether decline-associated concentration is general beyond the Palmer/Signy Adélie systems.

## Frozen endpoints

    2009
    2018.

No alternative year may replace either endpoint after colony values are opened.

## Fixed data source

Primary source:

    analysis/output/model_results/3_Colony_Level/colony_summary.csv

Use the source's posterior **median colony-level seasonal abundance index** at each frozen endpoint.

Do not mix raw aerial counts, satellite-area observations or another posterior summary into the primary endpoint.

If no identifiable posterior median colony-year abundance index exists in this file, record SUPPORT FAIL.

## Outcome-blind support audit

Before summarizing any abundance magnitude, inspect only:

- column names;
- site/colony identifiers;
- year coverage;
- number of colony series;
- missingness at 2009 and 2018;
- which column is explicitly the posterior median abundance index;
- region labels, if present.

Do not calculate totals, E, shares, colony changes or dominant identity during the support audit.

## Fixed roster

Primary roster:

    every colony with a posterior median abundance index at both 2009 and 2018.

Roster selection is based only on paired structural support.

No colony may be excluded after magnitudes are opened because it is small, unstable, temporarily absent or changes direction.

Require at least 10 paired colonies. Otherwise SUPPORT FAIL.

## Decline eligibility gate

For the mechanically fixed paired roster:

    N2018 < N2009

must hold.

If not:

- record the roster-specific decline gate as FAIL;
- do not use the publication-level global decline to override it;
- do not change years or roster.

## Primary spatial endpoint

For each frozen endpoint:

    N_t = sum_i n_it
    p_it = n_it/N_t
    E_t = 1/sum_i p_it^2.

Primary effect:

    delta_logE = log(E2018/E2009).

Interpret continuously:

- delta_logE < 0: concentration;
- delta_logE > 0: equalization/spreading.

No post-hoc effect-size threshold is introduced.

## Exact decomposition

For each colony:

    G_i = n_i2018/n_i2009
    G_bar = N2018/N2009.

With:

    H0 = sum_i p_i0^2
    w_i0 = p_i0^2/H0
    G_D = sqrt(sum_i w_i0 G_i^2)

verify:

    E2018/E2009 = (G_bar/G_D)^2.

Report proportional endpoint residuals:

    expected_i2018 = N2018*p_i2009
    residual_i = n_i2018 - expected_i2018.

## Local arithmetic

Report:

- number/fraction of colonies decreasing;
- number/fraction increasing;
- gross negative change;
- gross positive change;
- largest positive/negative proportional residuals.

Because these are posterior medians of an abundance index, local signs are descriptive point-estimate signs, not posterior probabilities unless uncertainty is separately propagated.

## Composition and dominance

Report:

    TV = 0.5*sum_i |p_i2018-p_i2009|

and dominant-colony identity at both endpoints.

This identifies whether concentration/equalization accompanies dominance retention or turnover.

## Regional sensitivity

If a fixed region variable is present in the public model output or colony-attribute file, repeat the same endpoint decomposition for each region with >=3 paired colonies.

This is secondary and must report all eligible regions.

No region is selected based on direction.

## Uncertainty boundary

Primary spatial decomposition uses posterior medians because the public colony summary is the frozen source.

Do not manufacture cross-colony posterior covariance from marginal credible intervals.

If the repository contains jointly indexed posterior draws of colony-year abundance, a separately specified sensitivity may propagate E across joint draws.

The point-estimate result does not become a posterior probability without that joint structure.

## Decision logic

### Decline gate passes, E down
External support that decline can concentrate breeding abundance.

### Decline gate passes, E up
External counterexample to a universal decline-concentration rule.

### Decline gate passes, E near flat
Spatial composition changes little despite numerical decline; report continuously.

### Decline gate fails
No decline-allocation interpretation.

## Relation to Palmer/Signy

Palmer/Signy show loss-driven concentration at much finer within-island breeding-unit scale.

The emperor route operates at a global colony-network scale and a different species.

Agreement would suggest scale/species transfer of the concentration arithmetic.

Disagreement would demonstrate scale- or system-dependence.

Either outcome is informative.

## Boundaries

- Response is a model-estimated emperor-penguin abundance index, not directly comparable in units to occupied nests.
- Individual colonies can appear/disappear observationally with fast-ice conditions; no single low value is called extinction.
- No causal sea-ice interpretation is inferred from E.
- The global decline itself is prior publication knowledge; only the spatial-allocation endpoint is new to this route.
