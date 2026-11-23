# Ross Island matched-breeding-abundance branch audit v1

**Status:** post-result exploratory branch comparison. This analysis was generated after the frozen Ross V2 result and is not confirmatory. It asks whether decline and recovery revisit the same spatial state at similar total breeding abundance.

## Hysteresis-style question

If spatial recovery simply retraced spatial collapse, then years with similar total breeding-pair abundance should have similar colony composition and effective colony number, regardless of whether the system is on the decline or recovery branch.

The Ross record contains a narrow range where decline and recovery breeding abundances overlap closely enough for direct comparison.

## Closest near-equal-N pairs

### Pair A

Decline branch, 1997:

    breeding-pair N = 204,837
    E3 = 1.6261
    E6 = 2.1706
    shares:
      Royds  = 1.92%
      Bird   = 23.19%
      Crozier= 74.89%

Recovery branch, 2002:

    breeding-pair N = 203,996
    E3 = 1.5074
    E6 = 1.8190
    shares:
      Royds  = 1.10%
      Bird   = 19.94%
      Crozier= 78.96%

Relative difference in N:

    -0.41%

Recovery-versus-decline redundancy:

    E3: -7.30%
    E6: -16.20%.

Thus almost identical total breeding abundance occupies a more concentrated spatial configuration on the recovery branch.

### Pair B

Decline branch, 1985:

    breeding-pair N = 224,414
    E3 = 1.6252
    E6 = 2.2902
    shares:
      Royds  = 1.43%
      Bird   = 23.86%
      Crozier= 74.71%

Recovery branch, 2004:

    breeding-pair N = 221,301
    E3 = 1.4130
    E6 = 1.8652
    shares:
      Royds  = 0.92%
      Bird   = 16.62%
      Crozier= 82.46%

Relative difference in N:

    -1.39%

Recovery-versus-decline redundancy:

    E3: -13.06%
    E6: -18.56%.

Again, nearly the same total breeding abundance is associated with a substantially more concentrated composition on the recovery branch.

## Additional near matches

Using a descriptive nearest-decline-year comparison with a <=5% relative N difference also yields:

- recovery 2005 (254,617) vs decline 1987 (242,644):
  - N difference +4.93%
  - E3 difference -3.69%
  - E6 difference -15.82%

- recovery 2007 (251,239) vs decline 1987 (242,644):
  - N difference +3.54%
  - E3 difference -7.62%
  - E6 difference -21.93%.

These reuse the same decline year and are not independent replicates. They are reported only as descriptive consistency.

## Interpretation

The Ross breeding distribution is not a single-valued function of total breeding-pair abundance.

At similar N, the recovery branch is more Crozier-dominated and has lower effective breeding-unit number than the decline branch.

This is a **branch-dependence / hysteresis signature**:

    same approximate N
    + different history
    -> different spatial composition.

## Why this is not proof of endogenous hysteresis

The decline and recovery years differ in more than historical state.

Potential explanations include:

- different sea-ice and ocean-access conditions;
- different food-web state;
- B15A/C16 iceberg effects;
- colony-specific breeding propensity;
- survival and recruitment differences;
- movement;
- configuration-mediated edge predation / nest-site fidelity;
- dynamic breeding capacity.

Therefore this comparison cannot distinguish:

    endogenous spatial hysteresis

from:

    exogenous environmental state dependence

or a mixture of both.

## Relation to existing Adélie theory

McDowall & Lynch (2019) already demonstrated a mechanistic hysteretic response of within-colony spatial configuration in Adélie penguins: declines can fragment nesting aggregations, while nest-site fidelity and slow rearrangement leave colonies in suboptimal configurations as abundance changes.

The present analysis does not rediscover that mechanism.

It shows that a **branch-dependent spatial state is visible one level higher, among major Ross Island breeding colonies/components**, in the breeding-pair census.

That cross-scale connection is hypothesis-generating.

## Claim boundary

Safe:

> At comparable total breeding-pair abundance, Ross Island was more spatially concentrated on the recovery branch than on the decline branch.

Safe:

> This is consistent with spatial hysteresis but does not establish its endogenous cause.

Too strong:

- the matched pairs prove an Allee threshold;
- the same individuals failed to return to former colonies;
- colony configuration alone caused the branch difference;
- the phase coefficient is causal.
