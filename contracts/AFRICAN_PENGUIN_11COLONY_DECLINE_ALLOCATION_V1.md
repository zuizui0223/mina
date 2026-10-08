# African penguin 11-major-colony decline allocation test v1

**Status:** pre-effect contract. Frozen before opening the JARA packaged African-penguin colony magnitudes or model trajectories.

## Independent public source

Henning-Winker/JARA public repository, African-penguin example used with the Sherley et al. African penguin assessment.

The public repository description states that the example contains:

    breeding-pair counts from 11 major colonies in South Africa and Namibia

and fits colony-specific time series whose posteriors are summed to obtain the species-level trajectory.

This is a separate analysis frame from the 22-colony Dryad raw-count contract. It is not a substitute inside that contract.

## Frozen comparison

Use:

    1989
    2019

because the associated publication independently identifies 1989 as the broad population peak and 2019 as the terminal historical low.

No alternative endpoint is allowed after magnitudes are opened.

## Fixed roster

Primary roster:

    the 11 major African penguin colony series packaged in the JARA example.

No colony is selected or dropped based on trend direction.

## Source hierarchy

Preferred primary endpoint values:

1. actual packaged observed breeding-pair counts if the JARA example exposes them at both 1989 and 2019;
2. otherwise, the JARA colony-specific fitted median abundance at the two frozen years, if all 11 colonies have fitted values at both endpoints.

The source type must be fixed during a **support-only audit before magnitudes are summarized**.

Do not mix raw and fitted values among colonies.

If neither source gives a common 11-colony endpoint, record SUPPORT FAIL rather than changing years.

## Support-only audit

Before summarizing magnitudes, inspect only:

- object/file names;
- field names;
- colony-series names;
- year coverage;
- missingness at 1989 and 2019;
- whether endpoint values are raw observations or fitted medians;
- whether all 11 series share the same source type.

Do not calculate totals, E, shares or colony trends during support audit.

## Decline gate

For the fixed 11-colony frame:

    N2019 < N1989

must hold to interpret the result as a decline-allocation test.

If not, record gate FAIL. Do not change the roster or interval.

## Primary endpoint

For t in {1989,2019}:

    N_t = sum_i n_it
    p_it = n_it/N_t
    E_t = 1/sum_i p_it^2.

Primary effect:

    delta_logE = log(E2019/E1989).

## Exact decomposition

For each colony:

    G_i = n_i2019/n_i1989.

Report:

- absolute change;
- multiplication factor;
- sign of change;
- proportional endpoint residual.

Compute:

    G_bar = N2019/N1989
    w_i0 = p_i0^2 / sum_j p_j0^2
    G_D = sqrt(sum_i w_i0 G_i^2)

and verify:

    E2019/E1989 = (G_bar/G_D)^2.

## Local attrition

Report:

    n_colonies_down
    n_colonies_up
    gross_loss
    gross_gain
    gross_gain/gross_loss.

If E decreases, distinguish:

- universal attrition: 11/11 decline;
- predominant attrition: losses dominate but >=1 colony increases.

## Composition history

Report:

    TV = 0.5*sum_i |p_i2019-p_i1989|

and dominant colony identity at both endpoints.

## Decision logic

### N down, E down
External support for decline-associated spatial concentration.

### N down, E up
External counterexample showing a declining colonial population can become more even.

### N not down
Decline gate fails for this fixed 11-colony frame.

## Relation to the Antarctic results

This prospective route tests only the decline-side spatial arithmetic in a phylogenetically and environmentally distinct penguin.

It does not test:
- Ross shock/rebound asymmetry;
- configuration-mediated hysteresis;
- island capacity;
- movement.

## Boundaries

- If fitted medians are required, the result is explicitly a model-estimated spatial composition rather than raw-count composition.
- Do not present fitted posterior medians as exact observations.
- No alternative JARA model version is selected after seeing the result.
- This contract remains separate from the 22-colony Dryad raw-count contract.
