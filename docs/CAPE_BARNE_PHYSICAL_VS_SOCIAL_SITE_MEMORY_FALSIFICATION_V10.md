# V10 — an Antarctic counterexample to sufficiency of persistent nest-site memory

Date: 2026-10-10. Secondary published evidence audit in mina PR #193, independent of the 2021 Cox source cohort. No new field observations or causal effect fit. Canonical source: Emslie, Steven D., *Antarctic Science*, published online 17 July 2026, [doi:10.1017/S0954102026100807](https://doi.org/10.1017/S0954102026100807).

## A crucial negative example for the physical-legacy-only explanation

**Cape Barne, south of Cape Royds on Ross Island, remained unoccupied as a sustained Adélie breeding colony despite extant physical traces of historical nests.** The Emslie 2026 research independently reports:

| Field or historical evidence | Legitimate observational claim | Unlicensed extrapolation |
|---|---|---|
| 1912 mapped 'old penguin rookery' | Old nesting substrate recognised during Terra Nova | A full 1912 active-pair census |
| Visits across 1963–1966 | Sporadic attempted nesting/new nests or adult pairs at Cape Barne | First arrival times, exact annual pair counts, fledging success |
| **1988/89** field record | **Five nests with breeding adults** as Royds reached ~4,200 pairs at a modern peak | Five successful fledged chick cohorts, established emigrant origin |
| Late 1990s | Abandoned again; around the same time Royds breeding colony halved; very small sporadic nesting also mentioned | Causal 'low emigrant supply caused abandonment' inferred from synchronous pattern |
| January **2001** visit | No nesting pairs observed during source author's visit | Every breeding season from 2001 onward had full zero-census |
| December **2024** visit | Intact pebble nest constructions and guano stains still visible, and the area reported abandoned | Precisely dated identity of each stone nest, annual 2024 quantified pair census, proof seabird arrival never possible |

The time between 1988 and 2024 is 36 calendar years, **not 36 continuous documented zero-count years**. The source notes no 21st-century reports of Cape Barne breeding (including a 2001 negative visit), but sporadic visits cannot justify unmonitored year zero imputations. Remnant substrate may be older than the 1980s nests. Earlier abandoned nests have radiocarbon ages spanning multiple millennia, and the paper explicitly reports 49 radiocarbon measurements. Do not assume all physically persistent mounds were created by failed 1980s nesters.

This is an empirical **counterexample to the strong necessary-and-sufficient claim that physical guano/pebble nest legacies automatically guarantee future site reuse**. It is NOT proof that old physical nest cues have zero effect on the probability of future settlement; sea access, food availability, adults able to prospect, breeding-season snow, predator exposure and available nearby habitat remain uncontrolled.

## New high-information causal contrast worth seeking data for

**Different persistence timescales of physical and social site memory.** Pebble nest/ornithogenic structures can remain for decades or centuries while their particular breeding groups and immediate social informational cues vanish. Reuse might require both *favourable functional sea-to-colony accessibility* and *enough prospective breeders arriving*, with physical legacy modifying preferences **conditional on** those opportunities. None of these components is identified from the historical narrative.

Define prior physical patch mark as `M` (old pebble structure vs genuinely surveyed never-used and matched rock), pre-season access `A` (season/stage-specific open-water pathway), and colonist supply `S` (independent marked first breeders or linked source-colony trajectories).

- **Legacy-only sufficiency (strong version):** `M=1` alone predicts continued high reuse even if `A` or `S` deteriorate. Cape Barne is inconsistent with this version in its ecological context, but still cannot establish individual effect magnitude.
- **Conditional ecological memory:** `M` influences settlement in seasons where `A` and `S` permit movement into the risk set, but may leave long periods with visible `M` and zero colony recovery. Predict positive `M x A` or `M x S` interactions under independently measured denominators; avoid logistic p-values until source support.
- **Public-information success cue:** recent successful chicks and active social aggregations predict pioneer settlement; decades-old nests without live groups may have little attractiveness.
- **Static site sorting:** rocks, slope, snow, water access and geography explain all apparent site memory once potential-patch baselines are matched.

For a genuinely new island-biogeographic law, pre-register at least two independent source-colony–recipient-patch systems, map all empty but suitable receiving patches **before** new arrivals, include successfully used, genuinely failed, never-used and old abandoned substrate patches, and independently track actual marked new breeders and chick fates. Distinguish Ross Island *subsites* from true inter-island dispersal.

**Do not multiply environmental effects to force significance.** If both years with/without nesting and relevant supply/access are not independently covered with comparable detection, this contrast is structurally unidentified. A full model should not be fit.

## What was actually implemented

- `contracts/CAPE_BARNE_PERSISTENT_NEST_LEGACY_RECOLONIZATION_V10.json`: six independently source-dated narrative event classes with unmeasured states declared unknown, no unsurveyed zeros.
- `scripts/audit_cape_barne_legacy_vs_reoccupation_v10.py`: checks exact source event counts, the five 1988/89 occupied nests, physical legacy in 2024, and rejects manufactured census or chick-success claims; calculates calendar elapsed time but not absence duration.
- `tests/test_cape_barne_legacy_vs_reoccupation_v10.py`: synthetic changes to 2024 pair count, nest fledging and legacy sufficiency must fail.
- `.github/workflows/cape-barne-persistent-nest-legacy-v10.yml`: source-backed data contract without reading new original biological outcomes. A passing CI validates chronology semantics, **not a new biological effect**.

**Scientific verdict:** A persistent nesting-site 'memory' can coexist with present colony abandonment. This is an especially useful falsifier of **unconditional** microhabitat engineering claims, but the explanation of conditional recovery remains unknown. Do not present the earlier Cox failed-pioneer hypothesis as discovered. The old physical structures at Cape Barne were used by past breeding populations; this is not a verified example of a failed individual pioneer. The newest Southwell island-scale potential-habitat survey is also a different spatial grain and cannot repair Cox's absent fine-scale counterfactual.

Ecology PR #189 frozen, PR #142 USAP source authentication gate untouched, and emperor PR #195 unmodified.
