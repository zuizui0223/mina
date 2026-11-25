# V6 — Partial identification under cloud-year imputation (2026-10-13)

A descriptive overlap ratio alone is not a valid ecological effect. If the valid same-year support cannot be fully recovered, a conservative **partial-identification** approach can report uncertainty without assuming imputed areas are observed.

For a frozen transition interval, let G be the total measured macaroni gain area in an audited common frame, and let X be the measured overlap with lost chinstrap space. Let U_G be the *upper bound* on gain area potentially affected by date substitutions or other unverified provenance, and U_X be the upper bound on overlap area potentially affected by those same uncertainties. If **G>0** and valid observed support and area denominators are separately justified, a conservative interval for the genuine-overlap share under contamination is

lower = max(0, X - U_X) / G
upper = min(G, X + U_G) / G.

This interval is intentionally broad and assumes fixed G; if even G is partly unverified, a separate denominator interval [G_min,G_max] is required, yielding the more conservative lower = max(0,X-U_X)/G_max and upper = min(1,(X+U_G)/G_min), **only when G_min>0**. If G_min=0, the ratio is not identified; never report a finite bound as if denominator positivity were established.

**Critical:** U_G and U_X are not guessed from a general >90% survey coverage claim. They require documented spatial provenance or a rigorous maximum affected-area estimate. Without such a bound, set the identification region to [0,1] or undefined and STOP the ecological inference. Even tight overlap bounds would not identify site legacy, competition, or causality.

No BAS shapefile or biological polygon has been accessed; this is an algebraic protocol note only. The source remains DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308. Ecology PR189 unchanged.
