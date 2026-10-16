# Ross inverse-path bounded-count sensitivity v1

**Status:** post-result deterministic sensitivity analysis. This is not a sampling-error model and does not replace the count-uncertainty audit.

## Question

The observed six-component rebound differs from exact inverse-path restoration by 9.41% of rebound abundance.

Because the historical Ross aerial series does not provide component-specific count standard errors, no confidence interval can be attached to that mismatch.

A narrower question is still answerable:

> how large would bounded multiplicative perturbations of the reported 1999, 2001 and 2002 component counts have to be before an exact inverse path becomes algebraically possible?

## Setup

For component i let the reported counts be:

    A_i = 1999 pre-shock
    B_i = 2001 trough
    C_i = 2002 rebound.

Allow unknown latent counts:

    A_i*
    B_i*
    C_i*

to lie independently within:

    observed * (1 +/- delta).

Exact inverse-path rebound with common scaling k requires:

    C_i* - B_i*
      = k (A_i* - B_i*)

for every one of the six components.

Equivalently:

    C_i*
      = k A_i* + (1-k) B_i*.

This is only a bounded-perturbation feasibility calculation.

It does **not** assume the actual count error is independent, symmetric, multiplicative, or bounded this way.

## Sensitivity A — keep the observed aggregate rebound scaling

The observed aggregate loss and rebound imply:

    k_obs
      = 109,198 / 112,613
      = 0.969675.

With k fixed at this observed aggregate value, the smallest common symmetric relative tolerance that permits an exact inverse path is:

    delta_min = 0.22669
              = 22.67%.

The binding component is Cape Royds.

Component-specific minimum tolerances under the same fixed k are approximately:

- Royds: 22.67%
- Bird South: 20.31%
- Bird Middle: 16.49%
- Bird North: 1.94%
- Crozier West: 3.61%
- Crozier East: 9.54%.

Thus exact proportional reversal at the **observed aggregate rebound fraction** cannot be produced by moving every reported anchor count by less than 22.7% under this deliberately simple error envelope.

## Sensitivity B — also allow the inverse-path scaling to float

A more permissive analysis allows k itself to vary.

Choose k to minimize the largest relative tolerance required across the six components.

The optimum is:

    k = 0.65135

with:

    delta_min = 0.13843
              = 13.84%.

At that optimum the binding components are approximately:

- Bird South: 13.84%
- Crozier West: 13.84%.

Thus even when the common inverse-path rebound scale is allowed to change substantially, exact reversal is infeasible unless at least ~13.8% symmetric relative perturbation is allowed.

## Interpretation

These values are **robustness thresholds**, not estimates of measurement precision.

Safe statement:

> Under a simple symmetric bounded-error sensitivity, exact inverse-path restoration is not algebraically recoverable from the reported counts with perturbations smaller than 22.7% when the observed aggregate rebound fraction is retained; allowing the common rebound scale to float lowers the threshold to 13.8%.

Do **not** write:

- historical count error was <13.8%;
- the Ross mismatch is statistically significant;
- the counts are accurate to 10%;
- the sensitivity proves biological reallocation.

## Relation to the 9.41% mismatch

The network-level half-L1 mismatch is:

    9.41% of rebound.

That does not mean 9.41% per-cell count error would erase the result.

The inverse-path constraint links all three time points and all six components with one common k.

As a result, the bounded perturbation required to make the entire trajectory exactly reversible is larger than the half-L1 allocation mismatch.

## Manuscript role

This is supplementary robustness only.

The main text should retain:

- 96.97% aggregate restoration;
- 9.41% inverse-path allocation mismatch;
- no formal CI because source-specific count error is unavailable.

If a reviewer asks whether a modest count perturbation could produce exact reversal, this sensitivity provides a transparent answer without inventing a probability model.
