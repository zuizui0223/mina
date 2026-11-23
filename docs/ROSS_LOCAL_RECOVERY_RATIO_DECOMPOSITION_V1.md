# Ross local recovery-ratio decomposition v1

**Date:** 2026-10-07  
**Status:** exact algebraic interpretation of already-opened focal counts; not a new ecological endpoint.

## Definitions

For a baseline–trough–rebound episode, define local loss and rebound

\[
L_i=n_{i,0}-n_{i,1},
\qquad
R_i=n_{i,2}-n_{i,1},
\]

and the local restoration ratio

\[
q_i=\frac{R_i}{L_i}.
\]

For the focal Ross episode, all six \(L_i>0\) and \(R_i>0\), so all \(q_i\) are defined.

Aggregate restoration is

\[
A=\frac{\sum_iR_i}{\sum_iL_i}
=\frac{\sum_iL_iq_i}{\sum_iL_i}.
\]

Thus **aggregate restoration is exactly the loss-weighted mean local restoration ratio**.

Exact proportional inverse recovery requires

\[
q_i=A
\]

for every breeding component.

## Focal local restoration ratios

| Component | Loss | Rebound | \(q_i=R_i/L_i\) |
|---|---:|---:|---:|
| Cape Royds | 2,253 | 872 | 0.387 |
| Cape Bird South | 4,515 | 487 | 0.108 |
| Cape Bird Middle | 1,499 | 523 | 0.349 |
| Cape Bird North | 15,019 | 13,351 | 0.889 |
| Cape Crozier West | 80,216 | 88,054 | 1.098 |
| Cape Crozier East | 9,111 | 5,911 | 0.649 |

Aggregate restoration:

\[
A=0.9697.
\]

But the six local restoration ratios range from **0.108 to 1.098**.

The unweighted mean is only 0.580 because several small breeding components recovered weakly. The aggregate value is much larger because Cape Crozier West contributed 71.2% of the shock loss and 80.6% of the rebound.

Removing Cape Crozier West, aggregate restoration across the remaining five components is only **65.3%**.

Thus the headline 96.97% aggregate recovery is not evidence that all breeding components nearly recovered.

## Exact link to inverse-path mismatch

The exact inverse-path residual in counts is

\[
\delta_i=R_i-A L_i=L_i(q_i-A).
\]

The half-\(L_1\) mismatch is

\[
M
=
\frac{1}{2}\sum_i|\delta_i|
=
\frac{1}{2}\sum_iL_i|q_i-A|.
\]

Therefore the mismatch fraction of total rebound is

\[
\frac{M}{\sum_iR_i}
=
\frac{1}{2A}
\frac{\sum_iL_i|q_i-A|}{\sum_iL_i}.
\]

So the published 9.41% mismatch is exactly the **loss-weighted mean absolute deviation of local restoration ratios, scaled by \(2A\)**.

For the focal episode:

- loss-weighted mean absolute deviation of \(q_i\): **0.1824**;
- aggregate restoration \(A\): **0.9697**;
- \(0.1824/(2A)=0.09405\).

## Exact link to endpoint composition

The exact inverse endpoint is

\[
n_{i,2}^{*}=n_{i,1}+A L_i.
\]

Because observed and expected endpoints have the same total abundance,

\[
p_{i,2}-p_{i,2}^{*}
=
\frac{\delta_i}{N_2}.
\]

Therefore

\[
D_{\mathrm{TV}}(p_2,p_2^{*})
=
\frac{M}{N_2}.
\]

For Ross:

- \(M=10,270.6\) pairs;
- \(N_2=203,996\);
- observed-versus-exact-inverse endpoint TV = **5.035%**.

Thus the same structured local-recovery heterogeneity that creates the 9.41% rebound mismatch directly creates a 5.03% compositional displacement from the exact inverse endpoint.

## Biological interpretation

The central biological quantity is not cosine similarity.

It is the heterogeneity of local restoration ratios.

Cape Crozier West:
- accounted for 71.2% of total loss;
- accounted for 80.6% of total rebound;
- restored 109.8% of its prior loss.

Cape Bird South:
- restored only 10.8% of its prior loss.

Near-complete aggregate recovery therefore emerged from **differential recovery weighted toward the dominant component**, not uniform restoration of the breeding network.

## Claim boundary

This decomposition is exact bookkeeping and is not claimed as new mathematics.

Its purpose is to show that the path-versus-state result is not an artifact of cosine similarity or an arbitrary concentration metric.

The ecological statement is:

> **unequal local recovery rates can generate near-complete aggregate recovery while reweighting spatial population structure.**
