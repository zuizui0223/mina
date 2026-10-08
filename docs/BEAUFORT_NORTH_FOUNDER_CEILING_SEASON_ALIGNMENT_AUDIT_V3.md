# Beaufort north-shore expansion — corrected season-aligned founder bound (v3)

**2026-10-08 | Exploratory structural falsification, previously published observations only.**
**Not a mark–resight analysis, not a new immigrant-source measurement, not confirmation of PR #192 source-capacity/rescue hypothesis.**
This audit corrects the founder-time anchoring in the earlier founder ceiling script. It does NOT reopen or change PR #189's frozen Ecology manuscript or PR #142's resighting-data lock.

## 1. Archival facts, with correct clock and locality

**Official Antarctic Specially Protected Area 105 management plan, Measure 5 (2015), p. 4** reports:
- January **1995**: **2 breeding pairs**, **3 chicks**, and approximately **10–15 nonbreeding penguins** at the *west end of the northern beach* (76°55'S 166°52'E).
- **2005/06**: **525 breeding pairs** at the northern subcolony.
- **2008/09**: **677 breeding pairs**.
- **2013/14**: **989 breeding pairs**.
- Its introduction explicitly says the subcolony was established in 1995, and describes Ross-banded birds seen especially on the northern beach.

The 1995 January record is part of the **1994/95 breeding season (start-year 1994)**, not the 1995/96 reproductive cohort. The observation of 525 pairs belongs to **2005/06 (start-year 2005)**. Numeric models using integer year labels but not aligned reproductive cycles can be off by an entire reproductive generation.

LaRue et al. (2013) report **460 pairs in 2004** and **957 in 2010** at a *northeast* Beaufort subcolony. The official plan describes the *northwest/west end of north beach* site. Site identity is plausible but **not established by a georeferenced spatial crosswalk**; the primary bound therefore uses ONLY the official northern site 1994/95 → 2005/06. LaRue 2004 is a separate conditional sensitivity.

Independent age constraint: Kappes et al. (2021) explicitly found **no breeders younger than age 3** in the known-age Ross sample (youngest breeding cohort 3 years). Age-2 breeding is tested only as a deliberate *outside-the-observed-age-range* relaxation.

Sources:
- Official ASPA105 (2015) management plan: https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/Measure5_ASPA105.pdf
- LaRue et al. 2013: https://doi.org/10.1371/journal.pone.0060568
- Kappes et al. 2021: https://doi.org/10.1111/1365-2656.13422

## 2. Strongest possible closed-population counterfactual

Let `P_y` denote potential breeding-pair equivalents in a breeding season starting in year y and `C_y` the chicks fledged from that season. For a strict, *hypothetically completely enumerated* northern subcolony in 1994/95:

`P_1994 = 2; C_1994 = 3`.

As an extreme advantage to the closure hypothesis, already in season 1995/96 **all 15 observed nonbreeders** are permitted to become `15/2 = 7.5` immediately reproductive pair equivalents. Thus `P_1995 = 9.5`, without mortality of the original breeders. Each pair then produces **two surviving chicks every year**; all parents and offspring survive indefinitely; all chicks can first reproduce with a partner at exactly age 3, with no limitations of food, space, mates, or sex ratio. The 1994/95 observed three chicks are assumed fully fledged even though that was not actually measured.

For later y, the recursively accumulated optimistic potential obeys

`P_y = P_(y-1) + C_(y-3)/2`, and `C_y = 2 P_y`.

Pair *equivalents* can be fractional; they are not observed fractional pairs. With a finite, completely enumerated founding population and no further immigrating or initially unobserved prebreeding cohorts, every additional 3-year-old contributor must originate from a previously counted local chick.

**Correct, season-aligned output:**

| Start year | Optimistic closed `P_y` | Published north-shore observation |
|---|---:|---:|
| 1994 | 2 | 2 pairs / 3 chicks |
| 1995 | 9.5 | NA |
| 1997 | 11 | NA |
| 2004 | **194** | 460 pairs in LaRue 2013, *site crosswalk unresolved* |
| 2005 | **285.5** | **525 pairs**, official 2005/06 |
| 2006 | **418** | no same-season paired count in this comparison |
| 2008 | **897.5** | 677 pairs, official 2008/09 |
| 2013 | **6068** | 989 pairs, official 2013/14 |

**Conditional falsification:** 525 observed pairs in 2005/06 exceeds the **285.5** maximal closed-founder capacity by **239.5 pair equivalents**, even allowing biologically impossible perfect vital rates. The one-extra-season sensitivity (418 pairs in 2006/07) still does not reach 525.

But **this is not a minimum number of immigration pairs**: early additional founders can produce descendants that contribute to late counts. Not all real individuals are captured by the 1995 beach visit; the 3 chicks do not certify all local births or previously born offshore cohorts.

## 3. The indispensable sensitivity: unobserved 1995 founders

Permit **x additional potential breeding-pair equivalents**, not recorded at the north beach but ready to reproduce in 1995/96, under the same impossible perfect-demography assumptions. This is not asserting immigrants: such birds might already be local, have visited from the much larger Beaufort main colony, or have immigrated from Ross.

The exact deterministic sensitivity at the 2005/06 endpoint is

`P_2005(x) = 285.5 + 28 x`.

Solving `P_2005(x) >= 525` gives `x >= 8.553571...` early pairs, or **18 unobserved adults when conservatively rounded up to complete individuals and perfectly paired**. This small difference in founding knowledge **removes the unconditional proof that net immigration occurred after the first visit**.

The 2004/05 extrapolation (194 + 19 x >= 460) requires `x>=14`, i.e. 28 additional adults, but only **if** LaRue's northeast colony is geospatially the *same* site as the official northwest/northern colony. Do not mix source polygons without verification.

Other deliberately extreme sensitivities:
- Count **4** 1994/95 fledglings rather than 3: `P_2005=292` (still below 525).
- Delay every young bird's first breeding to age **4**: `P_2005=140.5`.
- Allow a fraction `q` of every chick cohort to first breed at **age 2** instead of age 3, all else perfect: minimum `q≈0.5248` to reach 525 in start-year 2005. This contradicts the *observed Ross study age range* and is an explicitly non-empirical stress test, not proof that age-2 reproduction is physiologically impossible everywhere.

A realistic mortality/fledging model would reduce the closed growth potential; nevertheless, **unmeasured founding cohorts remain a fundamental identifiability issue regardless of realism**.

## 4. What this DOES and DOES NOT add to island biogeography

**Supported conditional conclusion:** if the 1994/95 census completely recorded the northern site and its pre-existing potentially reproductive cohorts, and earliest first breeding is age 3, then known founders cannot account for the 2005/06 expansion. Additional previously unobserved or newly arrived individuals would be needed to explain the count.

**Not supported:** a demonstrated flux of Ross→Beaufort **breeding settlers**, a reversal of source/sink roles, a net absolute export decline from Beaufort, an immigration rescue of Ross, or causality from glacier-retreat-induced nesting capacity.

The official ASPA105 plan reports birds *banded at Royds, Bird, Crozier* **sighted** at Beaufort north beach. That supports two-way encounter *possibility*, not a measured reverse immigrant breeder rate or natal-origin assignment to the new subcolony. Visits are not successful breeding placements.

**Prior-art veto:** Herman & Lynch (2022, DOI 10.1093/ornithapp/duac014) already used age-structured models and approximate Bayesian computation to infer sustained immigration during colonization of four gentoo colonies from counts. A demographic growth bound or generic claim "new colonies need immigration" is **not** a new ecological mechanism.

The potentially original island-scale proposition remains sharper and still untested:

> **When a change in breeding options causes founder recruitment inside one island, does it redirect future first-breeding settlement away from geographically neighbouring islands, changing the *direction and absolute flux* of the island network?**

This requires source-origin tags, first confirmed breeding location and timing, observation effort, stable within-Beaufort north/main boundaries, independently reconstructed pre-outcome ice-free nesting options, and an independent receiver panel capable of measuring true reoccupation/rescue.

## 5. Stop rules

- **DO NOT** interpret the 239.5 pair-equivalent difference as an integer count of immigrating breeding pairs.
- **DO NOT** claim Beaufort north was founded in 2004 (official 1995 records exist).
- **DO NOT** equate LaRue north-east and official northwest colonies before a footprint/census identity check.
- **DO NOT** assume the 1995 adult/nonbreeder tally exhausts all viable prebreeder cohorts: it was a site visit, not a complete island-wide age-resolved census.
- **DO NOT** infer that banded Ross birds *bred* on Beaufort from sighting alone.
- **DO NOT** update or unfreeze PR #189, or bypass PR #142's API-key and pre-outcome gate.
- If access to individual origin/settlement data is not obtained, retain this as a **conditional falsification and identifiability demonstration** only.

## Reproduction

`python scripts/audit_beaufort_founder_ceiling.py`

Focused tests:
`python -m pytest -q tests/test_beaufort_founder_ceiling.py tests/test_source_rescue_structural_support.py`.

Result outputs are deterministic and based only on published numbers and explicitly labelled assumptions.

## 6. **Exposure-site mismatch:** measured south-colony area cannot substitute for the north founding-site option

LaRue et al. (2013) explicitly specify their habitat-cover analysis on the **main southwestern colony** (Cadwalader Beach). The 1958, 1983, 1993, 2005 and 2010 mapped usable-area series is current-year **main-colony guano envelope minus snow/ice cover**. It is not an independently dated series of new habitat on the Beaufort **northern beach**. The 2015 ASPA105 plan explicitly describes the 1995 north-shore settlement at an already *ice-free* portion of the northern beach.

The measured southern mean nesting density **increased** over 2005→2010, even though the published Beaufort-to-Ross *marked visitor rate* declined. That cochange makes **contemporaneous release of average crowding at the established main colony** a poor stand-alone explanation. It does not exclude local new breeding options: simultaneously increasing main-colony density and subcolony growth are compatible if previously available north-beach nest sites attract recruits independently of mean core density.

A discriminating future study must treat:
- `K_main_south(t)`: outcome-independent bare/suitable nesting substrate on the southern main-colony geomorphic footprint;
- `K_north(t)`: independent northern beach newly usable/available nest options and verified occupancy history;
- `N_main(t)`: main-colony breeder number;
- `p_main_to_north(t)`, `p_main_to_Ross(t)`, `p_Ross_to_north(t)`: **confirmed first-breeding transitions**, not visit counts.

**Specific falsifiable opportunity-substitution claim:** increase in independently measured `K_north` changes within-island versus across-island **first-breeding settlement probabilities** even when `K_main_south`, source cohort size, access and marine forcing are held fixed. An effect of `K_main_south` alone, without independently measured north-site suitability, cannot establish this claim.

**Status:** no longitudinal independent `K_north(t)` or individual origin-specific first-breeding destinations have yet passed the frozen data structure gate. The simultaneous crowding/within-island expansion facts are published observations, not a fitted proof of opportunity substitution.

