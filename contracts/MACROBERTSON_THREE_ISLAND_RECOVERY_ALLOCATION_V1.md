# Mac.Robertson Land three-island breeding-recovery allocation test v1

**Status:** pre-effect contract. Frozen before opening breeding-pair count magnitudes in the AADC Bechervaise/Verner/Petersen count workbook.

## Independent system

Australian Antarctic Division dataset:

**Adélie penguin population counts for Bechervaise, Verner and Petersen Islands, Mawson**

DOI: `10.26179/5c9bf6704cf70`.

The source metadata states that the workbook contains intermittent population counts for three distinct islands:

1. Bechervaise Island
2. Verner Island
3. Petersen Island

Post-1990/91 values are occupied-nest counts taken on or about 2 December during incubation.

This is geographically independent of Ross Island and Palmer/Signy.

## External phase definition

Clarke et al. (2003) independently analysed Bechervaise Island from 1990/91 through 2001/02 and reported a positive trend in mid-incubation nest counts over those 12 seasons.

Freeze the candidate regional-recovery window to:

    1990/91 through 2001/02

before opening the three-island count magnitudes.

The Bechervaise published trend is used only to define the external window; it does not guarantee that the combined three-island network increased.

## Outcome-blind support audit

Before reading any count magnitude, inspect only:

- workbook/sheet names;
- column names;
- season/year labels;
- which of Bechervaise, Verner and Petersen are represented;
- missing versus populated count cells;
- date/method/quality fields.

Do not summarize count magnitudes during support audit.

## Fixed endpoint rule

If all three islands have populated occupied-nest values in both 1990/91 and 2001/02, use those exact endpoints.

If either endpoint is structurally incomplete, use:

- the earliest season within 1990/91–2001/02 with populated counts for all three islands; and
- the latest season within the same window with populated counts for all three islands.

This rule is based only on missingness.

If fewer than two all-three-island seasons exist, stop with SUPPORT FAIL.

No season may be changed after magnitudes are opened.

## Eligibility gate

Let the fixed three-island endpoint totals be N0 and N1.

The recovery-allocation test is eligible only if:

    N1 > N0.

If N1 <= N0:

- record the recovery gate as FAIL;
- do not relabel a subinterval as recovery;
- do not search for a more favorable period.

## Primary endpoint

For each fixed endpoint:

    N = sum_i n_i
    p_i = n_i / N
    E = 1 / sum_i p_i^2.

Primary effect:

    delta_logE = log(E1 / E0).

Interpret direction only:

- delta_logE < 0: concentrating breeding recovery;
- delta_logE = 0: exactly proportional composition;
- delta_logE > 0: spreading/equalizing breeding recovery.

Report the continuous value; do not create a post-hoc threshold for a meaningful change.

## Exact proportional-growth decomposition

For each island:

    G_i = n_i1 / n_i0
    G_bar = N1 / N0.

With starting shares p_i0 and H0 = sum p_i0^2:

    w_i0 = p_i0^2 / H0
    G_D = sqrt(sum_i w_i0 G_i^2).

Verify exactly:

    E1/E0 = (G_bar/G_D)^2.

Also report endpoint proportional residuals:

    expected_i1 = N1 * p_i0
    residual_i = n_i1 - expected_i1.

## Compositional turnover

Report:

    TV = 0.5 * sum_i |p_i1 - p_i0|.

Report dominant island identity at both endpoints.

This distinguishes:

- retained-dominance concentration;
- dominance reversal;
- weak composition change.

## Local-count arithmetic

Report for each island:

- absolute change;
- multiplication factor;
- whether endpoint count rose or fell.

Classify the network descriptively:

### Universal-positive recovery

    all 3 island counts increase.

If E falls simultaneously, this is a prospective external example of concentration without endpoint local decline.

### Mixed recovery

    regional N increases but at least one island count declines.

If E falls, concentration cannot be described as pure differential amplification.

## Decision logic

This route does **not** assume that recovery must concentrate.

After the frozen eligibility gate:

### Outcome A — N up, E down

External support for the general empirical proposition:

> recovery of breeding abundance can concentrate across distinct island nodes.

If all three island counts also rise, it additionally supports:

> concentration does not require endpoint local decline.

### Outcome B — N up, E up

External counterexample to a universal recovery-concentration rule.

This strengthens a conditional/path-dependent model of recovery allocation.

### Outcome C — N up, E unchanged

Recovery is approximately proportional in composition at the endpoint.

### Outcome D — N not up

Recovery gate fails. No recovery-allocation conclusion.

No outcome is allowed to trigger new endpoint selection.

## Relation to configuration-mediated hysteresis

This count-only test does not test the generated hysteresis mechanism.

It tests only whether the abundance-allocation phenomenon transfers to a three-island breeding network.

Mechanism would require independent information on:

- breeding configuration;
- usable capacity;
- survival/recruitment;
- movement/immigration;
- environmental state.

## Boundaries

- Counts are breeding/occupied-nest abundance, not total adult population size.
- Pre-1990 counts may require timing corrections; the primary window intentionally starts at 1990/91.
- The same three island identities are fixed throughout.
- No first observation is interpreted as colonisation.
- This route is prospective with respect to the three-island E endpoint, but the Bechervaise-only positive trend is already known from published literature and is explicitly part of the design.
