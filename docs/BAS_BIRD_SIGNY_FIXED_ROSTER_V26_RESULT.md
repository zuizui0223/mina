# V26 — Baseline-anchored Bird colony roster preserves the observed Bird–Signy period contrast

**Date 2026-10-21.** On original publisher-SHA-verified BAS Gentoo nest/pair census data, a post-V25 diagnostic of V25's historical correlation change was completed and tested by [GitHub Actions #39453485125](https://github.com/zuizui0223/mina/actions/runs/39453485125). The initial V26 CI failed a synthetic test due to the wrong test output-key name; only that unit test was changed and the subsequent source-based workflow succeeded.

## Why this check matters

V25's Bird Island–Signy annual nest/pair growth correlations were +0.547 before 1997 and −0.144 at/after 1997. However V25 permitted **5–7** Bird Island colonies, requiring only the same colonies within individual consecutive-year changes. This makes the island-mean changing monitoring roster a plausible explanation of apparent nonstationarity. V26 fixes all Bird observations to the **five named colonies recorded jointly in 1982/83**, selected from original structural metadata rather than measured abundance or correlations:

**Johnson; Lower Mountain Cwm; Square Pond; Upper Mountain Cwm; Upper Natural Arch.**

These five are held identical in EVERY analyzed annual growth window. The original V25 full-history r=+0.165616495725728 and original short V23 r=−0.33420933224382615 were reproduced exactly before computing new V26 sensitivity correlations. Original Bird Island historical v1 SHA256 b1abc3c3adacee3f277d481217aabe4206c7b592a81f1f0eb1a0ec20a64450d3 and Signy original CSV SHA256 53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b were both verified.

## Observed result

| Matched original annual start-year windows | V25 variable 5–7 Bird components | V26 *same five* Bird components | V26 leave-one-window-out r |
|---|---:|---:|---|
| Full original source history, 33 windows | +0.1656165 | **+0.1908476** | −0.0220 to +0.2680 |
| Before start 1997, 14 windows | +0.5466331 | **+0.5764783** | +0.1045 to +0.6969 |
| At/after start 1997, 19 windows | −0.1440887 | **−0.1414460** | −0.2056 to −0.0471 |

The pre-minus-post **difference between descriptive correlation coefficients is +0.7179243** in the fixed five-colony analysis (not a causal effect, and not a p-value). Signs agree in 8/14 early and 9/19 late comparisons. All 33 numeric source intervals survive with the same five Bird component identities; two of 35 originally eligible metadata windows were excluded for missing/unparseable Signy pair count as in V25. No source absence becomes biological zero.

**Primary interpretation:** changing the number or identity of monitored Bird Island colony components in the V25 year-specific mean **cannot alone explain the observed early positive versus later slightly negative correlation**. This is a meaningful source-bias sensitivity and strengthens the narrower descriptive statement that the historical observed synchrony is period-dependent.

## A different and important confound was measured directly

The publisher's original source count-date fields are available for all **35 structurally eligible** annual start-year windows, including 14 earlier and 21 modern metadata records. The **absolute seasonal gap between median Bird Island nest-count dates and Signy pair-count dates** differs:

| Original source period | Parseable Bird + Signy source count dates | Median absolute date-phase gap | Years with gap ≥30 days |
|---|---:|---:|---:|
| Before 1997 | 14 | **12.5 days** | 1 |
| At/after 1997 | 21 | **29.0 days** | 9 |

These 21 modern count-date observations include the two windows excluded later for unknown Signy abundance; thus this metadata comparison and the 19 numeric correlation windows have slightly different denominators. No calendar date criterion was used to remove year-outcomes, and no seasonal threshold was tuned. The observational-stage gap is conspicuously larger in the later programme: variation in true phenology, measurement definitions, and field effort may change the meaning of yearly pair-versus-nest tallies. This remains a potentially important rival to an ecological shift. The data do **not** establish a statistically inferred change point nor a climate-driven regime transition.

## Decision and current research state

**EXPLORATORY_FIXED_ROSTER_PERIOD_ASSOCIATION_CAUSAL_HOLD.** The narrow V25 observed period difference survives the strongest basic source-roster identity correction, but the CEMP/monitoring-stage transition and seasonal field-date difference remain confounded with true biological annual variability. There are **two physical islands**, not 33 independent island replications or a continent-scale law. Within-site log1p counts compare different original nest/pair indicators, which remain vulnerable to time-varying method effects. Do not interpret positive early and negative late r as observed environmental regime shifts, climate causes, inter-island dispersal, metapopulation colonization, predator–prey effects, or an island boundary mechanism.

Next independent information gain is a **multi-island panel with common count stage, contemporaneously measured year-varying environment, known observation effort and independently repeated geographic contrasts**. Continuing a narrow V25 two-island regression with more post-outcome year choices is not a publishable Antarctic macroecology test. The *Ecology* Paper1 PR189 remains scientifically frozen and was not changed.

- [Frozen post-result V26 diagnostic specification](../contracts/BAS_BIRD_SIGNY_FIXED_ROSTER_V26.md)
- [Source-verified result JSON](../results/BAS_BIRD_SIGNY_FIXED_ROSTER_V26.json)
- [Original-data CI](https://github.com/zuizui0223/mina/actions/runs/39453485125)
