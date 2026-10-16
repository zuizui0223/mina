# Path-versus-state recovery manuscript — reviewer stress test v2

**Date:** 2026-10-07  
**Canonical manuscript:** \`docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_5.md\`

## Overall assessment

The v0.5 framing is stronger and more defensible than the superseded spatial-memory framing.

The focal empirical result is:

> **Ross recovered where it had declined, but not in the same proportions.**

This statement is directly supported by the counts and does not require inference about latent individual states.

## Major attack 1: “Path versus state is already known from resilience and hysteresis theory.”

**Correct. Severity: high for novelty language, low for the empirical result.**

Lamothe et al. (2019) explicitly distinguish return along the historical path from recovery via a different path/hysteresis. Community and metapopulation studies also distinguish aggregate recovery from compositional or patch recovery.

**Required response:** never claim a new theoretical distinction.

The contribution is the quantified field-natural-experiment contradiction:
- amount recovery 96.97%;
- inverse-path fidelity 90.59%;
- state restoration 2.4%.

## Major attack 2: “TV state restoration was chosen after seeing the inverse-path result.”

**Correct. Severity: high for confirmatory claims.**

The TV audit is explicitly post-result.

**Defense:** do not attach confirmatory p-values to the focal path/state contrast.

The interpretation does not depend on TV alone:
- E3 crosses from 1.609 → 1.729 → 1.507;
- E6 crosses from 2.056 → 2.292 → 1.819;
- E6 is farther from baseline after rebound than at the trough;
- the observed endpoint is far from the exact-inverse endpoint in both composition and E.

Thus TV and effective-number summaries agree that the old spatial state was not restored.

## Major attack 3: “The 2.4% state-restoration score has a small denominator.”

**Partly correct.**

The baseline→trough TV distance is 5.09%, so the ratio-based restoration score is sensitive to that denominator.

**Defense:** always report the absolute distances alongside the ratio:
- baseline→trough TV = 5.09%;
- baseline→rebound TV = 4.97%;
- trough→rebound TV = 9.75%.

The core conclusion does not require interpreting 2.4% as a precise universal recovery metric. It is enough that the endpoint is essentially no closer to baseline than the trough despite 96.97% aggregate recovery.

## Major attack 4: “High cosine is just Cape Crozier West dominating both vectors.”

**Severity: high.**

Cape Crozier West is large and contributes strongly to both loss and rebound.

**Existing defense:** a prior dominance audit removed Cape Crozier West and still found 83.2% normalized loss/rebound overlap among the remaining five components.

**Required language:** high path fidelity is partly scale-weighted and must not be presented as six equally informative nodes.

The manuscript should emphasize the counterfactual consequence rather than cosine alone:
- exact inverse allocation at the observed aggregate rebound would nearly restore baseline composition;
- the observed structured residual reweighted the endpoint.

## Major attack 5: “The 9.41% mismatch was previously called ordinary. How can it now be important?”

There is no contradiction if effect size and state consequence are separated.

The mismatch fraction is ordinary relative to other Ross down→up episodes (9.12%, 9.41%, 10.63%).

Its **state consequence** is nevertheless large because the residual is structured:
- Crozier West is +10,270.6 pairs relative to exact inverse allocation;
- the other five components are below expectation.

The manuscript must say:

> the mismatch is not exceptional in magnitude, but it is state-consequential.

Not:

> the mismatch is unusually large.

## Major attack 6: “Expected near-baseline state under exact inverse reversal is mathematically automatic.”

**Correct.**

Because aggregate restoration is 96.97%, exact proportional reversal necessarily ends close to baseline.

That is the point of the counterfactual, not a discovery.

The empirical result is that the observed endpoint did **not** follow that near-restoring counterfactual despite high path fidelity.

## Major attack 7: “The other two Ross episodes are pseudoreplication.”

**Correct.**

They are not independent replicates and cannot establish generality.

Use only as within-series calibration showing that path fidelity around 90% does not automatically track state restoration.

## Major attack 8: “Palmer/Signy/Beaufort are a different question.”

They are not replications of the Ross path/state natural experiment.

Their role is process interpretation:
- unequal local losses can reweight state during decline;
- unequal local gains can reweight state during capacity release.

Keep them secondary and do not pool them with Ross.

## Major attack 9: “Why is this ecology rather than a metric paper?”

The manuscript must keep the biological statement ahead of the metrics.

Preferred:

> **the same breeding places can regain abundance at different rates, so geographic reversal of loss can still alter dominance and spatial redundancy.**

Avoid leading with:
- a new recovery index;
- a three-axis framework;
- a novel decomposition.

Amount/path/state are organizational language for an ecological natural experiment, not the product.

## Major attack 10: “Is the focal result biologically important if baseline→rebound TV is only 4.97%?”

Importance comes from context, not the raw TV alone.

- exact inverse recovery predicts only 0.0717% TV from baseline;
- observed distance is ~69× larger;
- E6 shifts from 2.056 baseline to 1.819;
- Crozier West share rises from 67.2% to 72.2%;
- the rebound transition is the largest compositional shift in the 25-transition series.

Do not imply a universal threshold for meaningful TV.

## Publication ceiling

**Ecology Article remains plausible.**

The paper is not Nature/NEE-level as a general law because:
- path/state analysis is post-result;
- only one externally documented shock is focal;
- the other Ross episodes are not independent;
- process contrasts use heterogeneous designs.

The strongest route upward would be a prospective independent baseline–shock–rebound system with predeclared path and state metrics.

## Decision

Continue v0.5.

Do not return to spatial-memory restoration.

Do not search for a favorable alternative metric.

Proceed to submission packaging after final figure QA and copyedit.


## Major attack 11: “Near-complete aggregate recovery is just dominated by the largest colony.”

**Substantially correct and biologically informative.**

Aggregate restoration is exactly the loss-weighted mean local restoration ratio.

For the focal episode:
- Crozier West supplied 71.2% of loss and 80.6% of rebound;
- Crozier West local restoration = 109.8%;
- median local restoration across six components = 51.8%;
- unweighted mean = 58.0%;
- excluding Crozier West, the other five components restored 65.3% of combined loss.

Therefore the manuscript should not imply network-wide near-complete local recovery.

The stronger interpretation is:

> **near-complete aggregate recovery was produced by differential local recovery weighted toward the dominant component.**

This turns the dominance objection into part of the biological result rather than a nuisance to be hidden.

## Major attack 12: “Differential local recovery is obvious and already predicted by metapopulation theory.”

**Correct.**

Uneven local disturbance, variable local demography, and source-patch context are established determinants of metapopulation recovery (e.g. Wilson et al. 2023; Mutz et al. 2017).

Do not claim differential recovery as a new mechanism.

The empirical contribution is the conjunction:
1. severe documented disturbance;
2. 96.97% aggregate rebound;
3. local restoration only 10.8–109.8%;
4. 90.59% inverse-path fidelity;
5. essentially no restoration of baseline composition.

The paper shows how an expected process—heterogeneous local recovery—can make aggregate and path recovery give a misleading impression of state restoration in a real monitored population.
