# Climate–penguin checkpoint: geographic support and inference reproducibility (2026-10-29)

**Scope:** Additional read-only audit of draft PR #206 on its committed data. This is **post-exploration source-support QA**, not a registered biological hypothesis test. Frozen penguin Ecology Paper 1 (PR #189), Antarctic island-mechanism Paper 2 (PR #199) and JNCC (PR #201) are untouched.

## 1. Historical Adélie census timing changes the geographic estimand

Input: `outputs/climate_penguin/historical_count_interval_timing.csv`, original `MAPPPD` site/season count joins already qualified for positive adjacent years and unchanged known counting method. These are **site–year intervals**, not independent islands, and the six named regions are geographic labels, not independent time-series replicates.

| Timing cohort | Eligible intervals | Distinct sites | Regions represented | Victoria Land intervals | Victoria share | Inverse-Simpson regions (interval-weighted, descriptive only) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All valid adjacent intervals | 301 | 33 | 6 | 189 | 62.79% | 2.2943 |
| Both counts confirmed after September | 203 | 26 | 3 | 187 | 92.12% | 1.1741 |
| Both counts confirmed after November | 191 | 23 | 3 | 187 | 97.91% | 1.0429 |

Full after-September region composition: Victoria Land 187; Central-west Antarctic Peninsula 9; South Shetland Islands 7. The other three source regions have zero **qualifying timing-confirmed comparisons**, not zero nesting activity or zero field surveys. After-November composition: Victoria 187, Peninsula 3, Shetlands 1.

**Critical qualification:** The post-September confirmation rate is 187/189 for Victoria Land and only 16/112 outside Victoria Land. This pronounced imbalance means an environment-before-census analysis restricted to timing-verified intervals will mostly estimate **Victoria Land**, not an Antarctic-wide response. A weighted average of the 203 intervals is not a six-region macroecological estimate. The inverse-Simpson number is a descriptive share-concentration diagnostic, **not** a formal effective number of independent regions or valid inference degrees of freedom. Repeated years/sites make any interval-level independence assumption invalid.

For September-only sea-ice hypotheses, use the strict after-September flag; for the full August–November ice window, use after-November. Preserve the full 301 as a separately labeled descriptive cohort; do not imply that unconfirmed survey dates come after environmental exposure. The 191 strict cases have only **four** intervals outside Victoria Land. Regional standardization, a new p-value or a causal Antarctic-wide mechanism would be unsupported by those four cases.

## 2. Wild-cluster inference must not be promoted from exploratory screening

The previously frozen sensitivity contains 216 planned *post-exploration* combinations: 214 estimable and two insufficient. For site / year / conservative maximum one-way wild-cluster p-values:

| Multiplicity summary | Site | Year | Maximum |
| --- | ---: | ---: | ---: |
| Unadjusted p < 0.05 | 32 | 30 | 9 |
| BH q < 0.05, full 216-family | 0 | 0 | 0 |
| BY q < 0.05, full 216-family | 0 | 0 | 0 |

The independent cross-check implements BH/BY without the original statsmodels correction call, retains the unestimable entries as p=1 **in the correction family**, and checks the 214 displayed adjusted values and the bootstrap enumeration sizes from the recorded source CSV. This checks reproducibility of the **reported outputs**, not wild-bootstrap assumptions, source calendar reconciliation, or the scientific absence of an effect. No additional source-level independent test is claimed.

## 3. Executable, non-destructive review guard

`tests/test_climate_penguin_checkpoint_guard.py` checks:

1. SHA256 and byte sizes against the committed 283-entry `SNAPSHOT_MANIFEST.json` for the original timing, summary and bootstrap files;
2. no duplicated adjacent interval IDs, known-method/positive-count eligibility, nested before/after-November timing conditions, and regional support totals against the original summary;
3. the 216-candidate full inference family, 214/2 completion status, enumerated vs Monte Carlo draw sizes, max-p aggregation, and **independently reconstructed** BH/BY q-values.

This is a review test, not a replacement for the source acquisition and numerical inferential bootstrap scripts. Run from repository root: `pytest -q tests/test_climate_penguin_checkpoint_guard.py`. In CI it is also included in ordinary `pytest`.

## 4. Unfinished empirical dependencies (do not erase by respecifying the same outcome)

- The separately stored **1991–2010 daily SIC extension (2,440 August–November dates)** has not been verified complete and is not part of this source snapshot. Do not use its incomplete manifest as if it were an observed 1991–2020 environmental panel.
- Environmental association with historical counts requires an actually complete date/coordinate/grid match, month-specific chronological exposure, quality flags, sensitivity to region/time/method and later independent confirmation. Missing dates remain missing; late-month exposures must not be treated as pre-census.
- Camera-specific season/year and settlement-day origin remain unreconciled. Directional sea-ice drift is not independent bird movement measurement; two-date matched NDVI is not vegetation change or warming attribution.
- The island predator × flightless breeder access interaction is a separate **HOLD** in PR #199 until directly observed exposure, independently surveyed predator absence and suitable flying/flightless breeding comparisons exist.

**Decision:** preserve exploratory signals and the independent negative multiplicity audit, identify the **Victoria-dominated empirical support** explicitly, continue original-source acquisition rather than tune the 216 already-exposed tests or relax existing Paper 2 cell/land gates.
