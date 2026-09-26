# Stage 4: weather × island habitat mechanism

This stage follows the frozen 1991–2017 five-island synchrony result.

The empirical pattern to explain is deliberately narrow:

- the five islands share an almost common long-term decline (PC1 = 96.4%);
- annual growth is only moderately synchronous;
- Litchfield reaches local extinction while neighboring islands persist.

The primary test is **not** another cross-sectional correlation between habitat
quality and long-term decline. Instead it asks whether the *same regional
weather year* produces different demographic deviations depending on island
snow-retention habitat.

For census interval ending in year `t`:

1. calculate each island annual log growth;
2. remove zero→zero intervals after local extinction;
3. subtract the mean growth of the other eligible islands in the same year;
4. count Palmer Station October days with precipitation > 0 before that census;
5. test whether
   `local_deviation ~ island + z(suboptimal_habitat) * z(october_precip_days)`.

A negative interaction is the predeclared prediction: wet/snowy pre-breeding
conditions should disproportionately depress populations on snow-prone islands.

The static habitat percentages are from Fraser et al. (2013) and were already
related to long-term population change in that publication. Therefore this is a
**cross-scale follow-up interaction test**, not a claim of independently
discovering the habitat effect.

Regional sea ice is intentionally deferred to a separate frozen lane because
its ice-year timing relative to the November census needs an explicit temporal
alignment rule.
