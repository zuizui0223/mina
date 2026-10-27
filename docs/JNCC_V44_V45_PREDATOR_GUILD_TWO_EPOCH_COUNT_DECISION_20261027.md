# V45 decision — the V44 reverse guild contrast is not two-epoch sampling robust

Date 2026-10-27. Scope: **same original 11 Scottish JNCC Country×Master networks, 17 same-unit, within-year/within-5-km gull-vs-kittiwake paired links from V44**. No taxa, site, dates, contrasts or source-count thresholds were reselected. Already-observed V44 direction remains NOT SUPPORTED; this is an explicitly **post-result** diagnostic, not a new confirmatory predation test.

## What was corrected

V44 E=C1-[C0+(1-C0)/N1] subtracts the second-epoch finite-N concentration expectation conditional on first-epoch observed shares as though p0 were true. If **both** epochs independently multinomial-sample the same latent p, E[E]=-(1-Q)(1-1/N1)/N0. This negative bias increases at small early N0 even if the true distribution never changes. V45 uses the unbiased within-that-model Simpson concentration U_t=sum_i n_ti(n_ti-1)/(N_t(N_t-1)), then delta U1-U0. An independent two-epoch pooled-share multinomial null draws both original N0 and later N1 3,999 times without changing original site component identities.

This is a **hypothetical measurement model**, not documented observation error in JNCC's adjusted two-census near-complete surveys. Source site maps, visit effort, counts' actual detection probability and survey-method changes were not recovered.

## Authentic source-level evidence (V45 GitHub Actions)

| Indicator | Original V44 | Two-epoch diagnostic V45 |
| --- | ---: | ---: |
| Master network count / pair links | 11 / 17 | **11 / 17 unchanged** |
| Equal-Master ground gull minus cliff kittiwake concentration | **−0.100017** | **−0.035747** |
| Two-epoch pooled multinomial null 5th–95th percentile | −0.084057 to +0.045417 (legacy metric) | **−0.096579 to +0.112811** |
| Observed difference's lower-tail percentile in its two-epoch parametric null | 0.01825 | **0.30075** |
| Signed D positive in Masters | 4/11 previously | **5/11** |
| Source count-support eligibility with N0,N1>=20 for both guilds | not primary | **1 Master only** |
| Counts N1/k >=3 for all eligible panels of both guilds | not primary | **2 Masters only** |
| Counts N1/k >=10 for all eligible panels of both guilds | not primary | **0 Masters** |

Original accessible (three gulls) panels n=17: median initial N0=35, later N1=8, source child components k=6, later N1/k median **2.14**; N1<10 occurs 9/17, N1/k<3 occurs 10/17. Original cliff kittiwake panels n=11: median N0=1392, N1=436, components k=5, later N1/k median **87.2**. An analytical negative expected legacy-D from the two-epoch pooled model is **−0.02362**; simulated mean **−0.02292**. This bias alone does NOT quantitatively explain the whole original −0.100 difference and may overestimate real census noise. The new estimator changes its scale, variability, and finite-sample properties.

Additional robustness: under the corrected delta-U, leave-one-Master-out mean range **−0.08049 to +0.03194**, with 9/11 omissions retaining negative sign; hence the negative direction also depends on which Master is included.

## Biological interpretation

**Original user-selected H2 prediction** that more mammal-accessible nesting guilds become more concentrated in declining shared Master-site networks was negative in observed V44 and remains **UNSUPPORTED**; this new correction must not be interpreted as supporting H2. The originally surprising negative gull-minus-kittiwake contrast was **not stable to two-epoch count treatment**. Claiming a biological cliff-vs-ground compensatory reorganization or a mammalian refuge effect is not supported.

Still separate and unresolved:
- no mammalian occurrence/nonoccurrence measured at the source breeding component's island, date or nest microhabitat;
- all 11 matched Masters Scottish; cliff guild is Black-legged Kittiwake only;
- source JNCC Site.ID polygons and survey effort / complete nest coverage not demonstrated;
- baseline size score and leader-change in full 959 declining panels not yet audited using a two-epoch null; V45 examines only V44 fixed guild contrast.
- Antarctic penguin systems have avian predators and distinct substrate, cannot be treated as predator-free controls.

## Reproducibility

- Frozen V44 source strata: `contracts/JNCC_WITHIN_MASTER_NEST_ACCESS_GUILD_V44_FROZEN.md`
- Post-result V45 design: `contracts/JNCC_V45_TWO_EPOCH_COUNT_DIAGNOSTIC_POSTRESULT.md`
- Executed exact original-source source script: `scripts/diagnose_jncc_v44_two_epoch_sampling_v45.py`
- Synthetic tests: `tests/test_jncc_v45_two_epoch_sampling_diagnostic.py`
- Compact verifiable numbers: `results/JNCC_V45_TWO_EPOCH_COUNT_DIAGNOSTIC_SOURCE_RESULT.json`
- [Original successful GitHub Actions](https://github.com/zuizui0223/mina/actions/runs/40487811125) and [full JSON artifact](https://github.com/zuizui0223/mina/actions/runs/40487811125/artifacts/12725608288).

**No substantive new ecological mechanism was supported by this exercise.** The valuable result is a hard bound on what source-level paired turnover/contrast may be claimed without calibrated observation processes.
