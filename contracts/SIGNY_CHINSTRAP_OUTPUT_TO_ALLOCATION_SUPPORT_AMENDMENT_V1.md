# Signy Chinstrap output-to-allocation support amendment v1

**Status:** pre-effect support-only amendment. Frozen before any late-fledgling magnitudes are summarized into the mechanism predictor or any beta/correlation is computed.

## Why an amendment is needed

The original contract required a fixed provider-defined colony roster but intentionally deferred the exact labels to an outcome-blind structural audit.

The public provider table reveals several **schema/semantic** complications that must be resolved before effect opening:

- C16 and C17 have seasons in which the provider reports a combined late-fledgling total rather than colony-specific late output;
- C18a and Outer Island do not form a continuous standardized-period colony-specific late-output series;
- C26, C66 and C69 enter the monitored roster later in the standardized period and therefore cannot define a common long-run core from 1996/97 onward;
- 1997/98 lacks pair counts because sea ice delayed base opening;
- 2010/11 lacks the required nest counts;
- 2020/21 lacks late fledgling counts because the base closed early.

These are structural/provider-semantic facts, not effect magnitudes.

## Frozen core roster

Primary mechanism roster:

1. C15
2. C18
3. C46
4. C47
5. C79
6. C80
7. C81

This roster is fixed before predictor/effect calculation.

## Explicit exclusions

### C16 and C17

Excluded because provider comments explicitly pool late fledgling output across the two colonies in some standardized-period seasons.

No attempt is made to split a pooled fledgling total.

### C18a and Outer Island

Excluded because they do not provide a sufficiently continuous colony-specific standardized-period support path for the fixed-roster one-year mechanism design.

### C26, C66, C69

Excluded because they enter the monitoring table after the 1996/97 standardized-period baseline and therefore do not belong to the common long-run core.

These exclusions are based only on structural support and output semantics.

## Frozen breeding abundance field

Use provider:

    Total number of pairs

when structurally present and >0.

Do not reconstruct a different total from other fields after effect opening.

## Frozen late-output field

Use provider:

    Total number of fledglings

only when a colony-specific late fledgling date/count is structurally recorded for that fixed colony-season.

A numeric zero is accepted as biological output only when the late count itself is structurally present.

Rows with no late count date / provider-declared no fledgling data are missing, not zero.

## Transition eligibility

For each start season t, all seven fixed colonies must have:

- B_it structurally observed and >0;
- colony-specific C_it structurally observed;
- B_i,t+1 structurally observed and >0;
- immediately consecutive t+1 season.

Any season with pooled late output, missing pair count, no late count, or zero breeding abundance in any fixed colony is ineligible.

No partial-colony panel is allowed.

## Support threshold

Require:

    >= 12 eligible start seasons

and:

    7 fixed colonies x eligible years

as a complete rectangular mechanism panel.

Otherwise:

    SUPPORT FAIL.

## Effect boundary

Until the support receipt is committed, do not compute:

- size-adjusted late output Q_it;
- local share changes;
- beta;
- correlations;
- permutation statistics.

If support passes, execute the original contract unchanged on this fixed 7-colony roster.
