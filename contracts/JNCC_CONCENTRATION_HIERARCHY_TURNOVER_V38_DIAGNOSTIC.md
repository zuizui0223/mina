# V38 — Post-V37 diagnostic: excess concentration with reversal of initial size hierarchy

**Prepared 2026-10-27, after observing the negative V37 size-retention score (17 taxa, 16 negative). This is openly post-result exploratory decomposition, NOT another confirmatory hypothesis test and NOT an ecological mechanism claim.**

## Single descriptive problem
V30 previously reported 959 JNCC two-census parent networks with falling matched-site totals and >finite-count excess concentration in 62.25% of them. Frozen H1a V37 subsequently found negative average signed size-to-share score in 16/17 taxa. These endpoints are not mathematically identical. Find out whether they coexist **within the same original parent panels**, and if so whether the lead monitored site changes, while excluding false interpretations due to source method or regression to mean.

## Source and fixed cohort
- Same original JNCC publisher XLSX SHA256 \`9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4\`; reapply exact V29/V30 source unit/ID/master aggregate safeguards before reading counts. Exactly 1,483 structural panels, 1,321 numeric eligible, 959 declining total count, 17 species. Any mismatch -> STOP.
- Primary panel unit species × original Country × Master-site × count unit with ≥3 same original child Site.ID records, exact integer adjusted counts and N0,N1≥2. Include ALL declining source panels, regardless of concentration or winner position; no cherry-picked E subset.
- No original raw child census cells, site names, coordinates, year-specific site counts, or movement trajectories committed.

## Fixed descriptive metrics
For each total-declining original panel, with p0_i=n0_i/N0 and p1_i=n1_i/N1:

1. **E** exactly reproduces frozen V30 finite-count-adjusted concentration: \`E=C1-[C0+(1-C0)/N1]\`, \`C=Σp_i²\`; concentration excess means E>0.
2. **S** exactly repeats frozen V37 \`(n0+0.5)/(N0+0.5k)\` size-score with \`x_i=log1p(n0_i)\` and p*-weighted standardization; **S<0** is initial size hierarchy losing relative shares. If all old child counts equal, S is not identified, and the joint E/S rate denominator excludes that panel without assigning zero.
3. **Dominant-child switching** only if the maximum count is UNIQUE in both epochs. A unique early leader and a unique different late leader is a switch; unresolved early/late ties are logged and not recoded as switches. On original source IDs only; a site code does not prove a fixed physical nesting polygon.
4. **Joint event A:** E>0 **and** S<0, denominator all decreasing panels with informative S; report raw count, raw panel fraction, species-equal mean of within-species fractions (eligible species ≥3 panels). This is the primary *descriptive* target, not a p-value for a newly post-registered ecological hypothesis.
5. **Joint event B:** E>0 **and** two-period dominant-child switch among panels with unique leaders both periods; report denominator, fraction, species-equal mean, and initial leader share change. Independently report all-decay panel switch fraction and E-positive fraction to avoid misrepresenting conditional denominator.
6. **No inferential relabeling:** observed changes of site share, a low TV, or a lead-site change are not verified colonization, local extirpation, recruitment, dispersal, predator refuge or social Allee effect.

## Fixed conditional idealized-count diagnostic
- Exactly 1,999 within-panel multinomial simulations with later total N1 fixed, prior shares p*_i=(n0_i+0.5)/(N0+0.5k), PCG64 seed 20261028. This is the identical *allocation family* as V37 but a new openly post-result exploratory statistic, not pre-registered confirmation.
- For every null draw, apply exactly E, S, unique leader switching and both joint events, all raw-panel and species-equal summaries; calculate null expectation and 5–95th envelopes where defined. Don't choose a different α, period, count restriction, simulator, species list or events to obtain a stronger result.
- Report a **synthetic regression-to-mean counterexample** constructed on invented fixed true site shares with *independent measurement noise in both census snapshots*. Under no biological site-size advantage, using noisy measured n0 as BOTH baseline predictor and null allocation reference may produce a negative average S. This is a risk demonstration only, not a fitted uncertainty model or null replacement for the original observational data.
- Never compare S and E statistically as independent evidence; both share same matched child census counts, and raw count measurement error is unidentified.

## Decision
Report the V38 decomposition whether it shows many concentration/reversal examples or few. Interpret at most an original source-level **compositional replacement/leadership switching phenomenon** (two periods), not an actual social game or island effect. Any question about causal social attraction, historical species movement or within-island structure requires independent repeat census/effort and fixed physical breeding-component geometry. The V36 predator-island ecological H2 result remains a **source gate STOP** and is not reopened or blended into these V38 results.
