# Bird Island gentoo six-unit breeding-allocation test v1

**Status:** pre-effect contract. Frozen before opening any incubating-nest count magnitude from the BAS 1981–2025 Bird Island dataset.

## Independent system

British Antarctic Survey / NERC Polar Data Centre:

**Breeding success of Gentoo penguins at Bird Island, South Georgia, from 1981 to 2025 - VERSION 2.0**

DOI: `10.5285/8fedb5a0-b98c-4457-9d86-aae9c6d3ed8e`.

This system is independent of:
- Ross Island;
- Beaufort Island;
- Palmer Archipelago;
- Signy Island;
- Heard Island.

It is also a different focal species from the Ross/Beaufort Adélie analysis.

## Measurement match

The dataset records incubating/occupied nests.

Breeding counts are made 7 days after 75% of marked nests at the timing colonies have laid at least one egg. Counts at Natural Arch and Mountain Cwm are made within one day of the Johnson counts. Counts are repeated until similar (about 5%) when needed.

This is a breeding-abundance endpoint, not total adult population size.

## Fixed six breeding units

Use only the six units explicitly defined by the BAS breeding-count methodology:

1. Johnson Beach
2. Square Pond
3. Upper Natural Arch
4. Lower Natural Arch
5. Upper Mountain Cwm
6. Lower Mountain Cwm

Do not add:
- Landing Beach;
- a generic unsplit Mountain Cwm record;
- any later/auxiliary location,

even if present in the CSV.

Do not merge Upper/Lower pairs after counts are opened.

## Outcome-blind support audit

After this contract is committed, inspect only:

- CSV column names;
- season/date fields;
- breeding-unit identifiers;
- which seasons have a populated incubating-nest field for each fixed unit;
- explicit missing-value representation;
- whether repeated same-unit/same-season rows exist.

Do not summarize or inspect numerical nest magnitudes during the support audit.

## Fixed endpoint rule

Let a **complete season** be a season in which all six fixed breeding units have exactly one usable incubating-nest count after applying only provider-defined row/field semantics.

Freeze:

- start = earliest complete season in the dataset;
- end = latest complete season in the dataset.

If fewer than two complete seasons exist, stop with SUPPORT FAIL.

No endpoint may be moved after count magnitudes are opened.

## Recovery eligibility gate

After endpoints are frozen by missingness only, open the twelve endpoint values once.

Let:

    N0 = sum_i n_i0
    N1 = sum_i n_i1.

Interpret the interval as a **breeding-recovery allocation** test only if:

    N1 > N0.

If N1 <= N0:

- record recovery gate FAIL;
- do not search for a positive subinterval;
- retain the result only as a long-interval spatial-allocation comparison.

## Primary spatial endpoint

For each endpoint:

    p_i = n_i / N
    E = 1 / sum_i p_i^2.

Primary effect:

    delta_logE = log(E1/E0).

Classification:

- delta_logE < 0: endpoint concentration;
- delta_logE = 0: proportional composition;
- delta_logE > 0: endpoint spreading/equalization.

Report continuous values; no post-hoc meaningful-change threshold.

## Exact allocation decomposition

For each unit:

    G_i = n_i1 / n_i0
    G_bar = N1 / N0.

With H0=sum p_i0^2 and w_i0=p_i0^2/H0:

    G_D = sqrt(sum_i w_i0 G_i^2).

Verify exactly:

    E1/E0 = (G_bar/G_D)^2.

Also report:

    expected_i1 = N1 * p_i0
    residual_i = n_i1 - expected_i1.

## Local endpoint arithmetic

For each of the six units report:

- absolute endpoint change;
- multiplication factor;
- sign of change.

Classify:

### Universal-positive recovery

    N1 > N0
    and all six local endpoint counts rise.

If E also falls, this is a prospective external example of breeding recovery concentration without endpoint local decline.

### Mixed recovery

    N1 > N0
    but at least one local endpoint count falls.

If E falls, do not label the pattern pure differential amplification.

## Composition history

Report:

    TV = 0.5 * sum_i |p_i1 - p_i0|.

Report dominant unit identity at both endpoints.

If the dominant identity changes, classify as endpoint dominance turnover.

Do not infer the within-interval path from endpoints alone.

## Decision logic

This route does **not** predict that recovery must concentrate.

### Outcome A — recovery gate passes, E down

Supports:

> breeding recovery can end in a more concentrated distribution across fixed breeding units.

If all six endpoint counts rise, additionally supports:

> endpoint concentration does not require endpoint local decline.

### Outcome B — recovery gate passes, E up

External counterexample to any universal recovery-concentration rule.

Supports path-dependent/conditional recovery allocation.

### Outcome C — recovery gate passes, E approximately unchanged

Long-interval recovery is approximately composition-preserving.

### Outcome D — recovery gate fails

No recovery conclusion. Do not search another interval.

## Secondary temporal audit — frozen before counts

Only after the endpoint result is recorded, use all complete seasons to describe the trajectory of:

- N_t;
- E_t;
- dominant-unit identity.

No significance test or temporal breakpoint is primary.

This secondary audit asks whether endpoint change is:
- monotonic;
- pulse-like;
- non-monotonic;
- associated with dominance turnover.

No breakpoint may be selected to improve the primary result.

## Relation to Ross

Ross generated a shock/rebound pattern in occupied breeding territories:

    shared shock -> temporary equalization
    immediate rebound -> reconcentration.

Bird Island is an external prospective allocation test. It is not required to reproduce the Ross shock sequence.

The transferable question is narrower:

> can breeding-abundance increase across a fixed colonial network be spatially redistributed rather than simply restoring or preserving the earlier composition?

## Boundaries

- Incubating nests are breeding abundance, not total adults.
- The test is about spatial allocation among monitored breeding units, not island-wide Gentoo abundance.
- The fixed six units come from provider methodology, not outcome inspection.
- No colonisation/extinction claim is made from missing rows.
- No environmental or Allee mechanism is inferred from this count-only endpoint.
- The recovery gate and endpoint rule are terminal; no favorable subinterval search is allowed.
