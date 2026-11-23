# Proportional spatial counterfactuals v1

**Date:** 2026-10-07  
**Status:** synthesis note; no new endpoint or statistical test.

## Common biological null

The integrated manuscript's process-specific analyses are unified by one question:

> **What would the spatial pattern look like if the observed aggregate change occurred without additional spatial reallocation?**

### Monotonic change

For starting local counts \(\mathbf n_0\) and endpoint total ratio

\[
G=N_1/N_0,
\]

the fixed-composition counterfactual is

\[
\mathbf n_1^{*}=G\mathbf n_0.
\]

This preserves local shares exactly.

Uses:
- Palmer / Signy decline: proportional thinning;
- Beaufort growth: proportional expansion.

### Recovery after an identified shock

For baseline \(\mathbf n_0\), trough \(\mathbf n_1\), loss vector

\[
\mathbf L=\mathbf n_0-\mathbf n_1,
\]

and observed aggregate rebound \(R\), the exact proportional inverse path is

\[
\mathbf R^{*}=R\frac{\mathbf L}{\sum_i L_i}.
\]

The implied recovery state is

\[
\mathbf n_2^{*}
=
\mathbf n_1
+
r(\mathbf n_0-\mathbf n_1),
\qquad
r=R/\sum_iL_i.
\]

Thus the counterfactual lies on the straight path from trough toward baseline. If \(r=1\), it returns exactly to baseline.

Use:
- Ross 1999→2001→2002.

## Why this matters

The systems do not need a pooled common effect size to form one manuscript.

Their common structure is the counterfactual:

    aggregate change alone
        vs
    aggregate change + spatial reallocation.

The observed spatial departure is measured in a system-appropriate way:

- Palmer / Signy: effective-unit trajectory versus fixed-composition simulations;
- Beaufort: proportional residual of the small/new unit and change in effective unit number;
- Ross: cosine alignment and half-L1 distance from the inverse path.

## Boundary

This proportional framework is bookkeeping, not new mathematics.

Do not claim a new decomposition theorem or a universal scalar measure.

Its value is conceptual and inferential: it makes the null of "no spatial reorganization beyond aggregate change" explicit across otherwise heterogeneous natural experiments.
