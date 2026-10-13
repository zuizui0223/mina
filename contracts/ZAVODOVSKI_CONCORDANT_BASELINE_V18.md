# V18 — Jointly corroborated C→M map-change footprint (frozen prior to computing new V18 outcome)

Date: 2026-10-13. Scope: PR196 Zavodovski exploratory maps only, after V10/V16 outcomes were already exposed, **not** confirmatory testing. The *specific* V18 endpoint and core-buffer values are fixed by this contract before opening a V18 summary. Primary Ecology PR189 is unchanged.

## Precise distinction

The currently quoted 2011→2016 67% area share is **not an observed settlement probability**. Using two historical **interpretations of the same 2011 satellite image**, we can ask whether any fraction of mapped 2011→2016 gain-loss co-location survives concordant species labeling. Independent readers ≠ independent field observations.

## Original evidence and required input protection

- BAS source DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308.
- 2011 original-image revised chinstrap and macaroni polygons, and Lynch historic same-scene CHPE/MCPE/MIXED polygons; 2016 original-image revised chinstrap and macaroni polygons.
- Cloud masks from 2011 and 2016 applied together to every layer. Absolutely exclude 2011/2016 under-cloud replacements and 2020–22 composite.
- Historical source CHPE=442, MCPE=18, MIXED=46 records. Neither mixed polygon nor a polygon with historic overlapping CHPE and MCPE may count as corroborated pure chinstrap.
- EPSG:32726, all polygon geometry valid, source SHA256s recorded. Fix identical evaluation support S as the union of all above mapped polygon footprints minus 2011 and 2016 cloud masks, as in V16. This is **not a complete surveyed island absence mask**.

## Fixed endpoint and competing state partitions

On S define `G = M2016\M2011(revised)`; `L = C2011(revised)\C2016`; `X = G∩L`. Use set operations intersected with S.

Let `H_C, H_M, H_mix` denote the historical 2011 CHPE, MCPE and MIXED polygon unions. Freeze **concordant historical pure-chinstrap footprint**:

`T = X∩H_C \ (H_M∪H_mix)`.

This requires:
(1) revised 2011 chinstrap occupancy;
(2) historical 2011 CHPE labeling of that land;
(3) no revised 2011 macaroni (already G), no historic 2011 MCPE or MIXED;
(4) 2016 macaroni occupancy (G) and no revised 2016 chinstrap (L);
(5) common direct-image 2011/2016 clouds excluded.

Report T m², T/G, T/X and T/L, all denominators explicitly. These are **intersection geometry shares**, never proportions of birds, settlements, or historical sites truly unoccupied by macaroni.

Partition all X in exclusive order:
A = X∩H_mix;
B = X∩(H_M\H_mix);
C = X∩(H_C\(H_mix∪H_M)) = T;
D = X\(H_mix∪H_M∪H_C).
A+B+C+D must equal X within numerical tolerance, with no pixel double counting. B can include rare original CHPE/MCPE overlaps: include in ambiguous historical macaroni category. D means *not depicted in historical 2011 CHPE/MCPE/MIXED polygons*, **not evidence of surveyed absence**.

Report raw m² + fraction of X in each state. Also give full G numerator and denominator of each state where meaningful. Validate reconstruction in code.

## Conservative geometric interior diagnostic (post-outcome, not inferred registration error)

For δ = 0, 1, 2, 5 m, define Tδ:
`Tδ = S ∩ shrink(C2011,δ) ∩ shrink(H_C,δ) ∩ shrink(M2016,δ) \ [ expand(C2016,δ) ∪ expand(M2011,δ) ∪ expand(H_M,δ) ∪ expand(H_mix,δ) ∪ expand(Cloud2011∪Cloud2016,δ) ]`.

For δ=0, this should match T exactly to numerical precision. Report Tδ m² and Tδ/G, **with G held at δ=0**, not changing denominators to make percentages look large. Since H_C is same image independent digitization but relative registration is not independently measured, these thresholds are **arbitrary sensitivity distances**, not empirically estimated georeferencing errors.

Even nonzero T5 cannot identify time order within five years, individual movements, competition, guano-mediated facilitation, independent habitat preference, successful breeding or causal island recolonization. Do not claim that it does.

## Success/failure interpretation

- T near zero: headline 67% co-location lacks corroborated pure-chinstrap 2011 baseline; downgrade site takeover language.
- T positive: a subset of mapped changes has concordant historical chinstrap labeling (two digitizers); **only a strengthened descriptive cartographic result**.
- Any numerical range is labeled post-outcome exploratory. Avoid post-hoc p-values.
