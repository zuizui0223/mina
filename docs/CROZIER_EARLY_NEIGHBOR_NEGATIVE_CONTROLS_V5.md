# V5 — Cape Crozier social assembly: site, effort and chick detection controls

**2026-10-08. Exploratory after outcome exposure.** A separate source-based negative-control audit of the exact Cox et al. 2024 2021 original Cape Crozier solitary nests (source release: pointblue/solo_nests at 04517cedac18950408abd4d0b510f4aae3447f05). It does NOT estimate a new causal mechanism and does not change frozen Ecology PR189.

## Main source fact and hard chronology correction

The earlier neighbor cutoff source audit reproduces direct crèche *confirmation* of **5/9** solitary breeder nest sites with a positive neighbor count by 2021-12-01, versus **6/27** without. No predation event or full chick-fate census is available. The time-order original source receipt was corrected and subsequently passed [Actions #37791663174](https://github.com/zuizui0223/mina/actions/runs/37791663174): of the nine early-neighbor sites, first egg was observed **before** first neighbor in five; **same-day** in two; **after** first neighbor but before December 1 in one; and **not by December 1** in one. Seven had an incubation-type observation on or before the first neighbor-positive check. Previous 5/2/2 reporting had inadvertently used a post-cutoff egg observation and has been withdrawn.

First positive neighbor observation is interval-censored, not independently observed immigration or arrival. First egg detection is not laying date.

## Detailed negative-control source checks (post-exposure descriptive)

| Original nest subset | Neighbor detected: crèche confirmed / nests | No detected neighbor: crèche confirmed / nests |
|---|---:|---:|
| All original 36 breeders (solo27 excluded) | **5/9** | **6/27** |
| Source shelter rock >=15 cm | **3/7** | **5/19** |
| Source shelter rock under 15 cm | **2/2** | **1/8** |
| Source area-code strata represented in BOTH neighbor states (M/C/L/B/QR) | **4/7** | **5/22** |
| Excluding source nest records explicitly marked GONE on/before Dec 1 | **5/9** | **6/26** |

These are source calculations on the *same exposed nests*, not independent replication or an analysis adjusted for measured/unmeasured confounders. Original area codes and coarse rock thresholds are not controlled experimental treatments. The two rock strata are tiny (especially 2/2). Some sites were checked repeatedly. The source recorded mean number of distinct check days by December 1 as **3.00** for 9 early-neighbor sites versus **2.63** for 27 no-neighbor sites, a detection-effort imbalance. The Cox paper describes ~4 to ~7-day nest rechecks with cadence varying by initial nesting stage.

A simple **logical ascertainment tipping bound**: to close the crude 5/9 versus 6/27 fraction gap (holding the 36 sites, observed positive confirmations, and neighbor categories fixed), at least **nine** of the **21** no-neighbor sites without a direct crèche confirmation would need unobserved successful crèche entry. This is NOT a statistical estimate of missed crèche events. The source's no-confirmation code cannot be treated as a certain dead chick.

The sole original source site explicitly marked GONE before Dec 1 among included breeders occurred in the no-neighbor group (solo15). Excluding it removes only one denominator from that group. But conditioning on later survival or observation can itself introduce selection bias; this sensitivity does not correct confounding.

## Biological interpretation

**Temporal settlement initiation:** Observed early neighbors are NOT generally temporally prior to the focal egg initiation; the evidence **does not identify** early social attraction as a reason for pioneer breeding.

**Social buffering after laying:** A difference in crèche confirmations remains compatible with predator dilution / local vigilance or neighboring nest refuge, but is also compatible with a good nest attracting conspecifics and better detection of its chicks. This mechanism is NOT identified. Skua attacks, nest-specific threats, parent experience and long-term tagged adult origins were not independently measured at the requisite grain.

The simplest ecological claim (group breeding reduces predation and supports chick survival) was already prior art, including the original Cox 2024 study's six-fold brood-to-crèche mortality contrast. The only unproven future mechanism deserving an independent controlled design is **whether the arrival of neighbors AFTER an isolated nest has already started breeding changes its true brood-to-crèche survival** (rather than retrospectively selecting nests destined to survive). This cannot be evaluated as causal from the present 36 original breeder sites.

Source: https://doi.org/10.1007/s00300-024-03246-9
Source-locked negative-control workflow: .github/workflows/crozier-neighbor-habitat-negative-controls-v1.yml
Contract: contracts/CROZIER_EARLY_NEIGHBOR_DETECTION_HABITAT_NEGCTRL_V1.json

**Status:** POST-OUTCOME DESCRIPTIVE ONLY. Do not claim an ecology mechanism or a novel general island-biogeographic law without independent controls. Frozen Ecology PR189 untouched.
