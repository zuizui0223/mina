# Evidence ledger v1 — 66 result receipts on main

**Frozen source:** `main` at `7764523c5f1e536b86084de8583cdd6262ee8fa7`  
**Inventory rule:** every JSON file under `results/` at that commit, exactly **66 receipts**.  
**Machine-readable ledger:** `docs/ENDPOINT_EVIDENCE_LEDGER_V1.csv`

## Why this ledger exists

The repository records a branching research program, not 66 independent tests of one favored claim. Treating every receipt as an equal “endpoint” would double-count follow-up diagnostics, synthetic recovery gates, sensitivity checks, and superseded analyses. This ledger therefore separates **ecological evidence** from **design/quality infrastructure**, and assigns inferential weight from provenance rather than p-value magnitude.

The central question inherited from ODSP is:

> **At which hierarchical level does information about population fate actually reside?**

The ledger supports a coherent elimination story, but only if the evidence hierarchy remains visible.

## Evidence tiers

| Tier | Meaning | May originate a manuscript claim? |
|---|---|---|
| **C1 — confirmatory / independent replication** | Effect was frozen before outcome inspection in an external system or species and passed its decision rule. | **Yes.** This is the strongest positive evidence. |
| **C2 — robust but exploratory** | Discovery result, bounded post-hoc analysis, structured-null robustness, or independent triangulation. | Supports interpretation; **does not by itself establish generality**. |
| **C3 — scope-limiting negative** | A frozen or bounded prediction failed, or a robustness analysis limits the range of defensible effects. | **Yes, negatively:** it defines what the data do not support. |
| **C4 — data/gate stop** | The biological question could not be executed because the required data bridge or support was absent. | No effect claim; establishes an information boundary. |
| **D0 — design / quality audit** | Outcome-blind inventory, schema audit, synthetic recovery, identifiability check, or packaging result. | **No.** Never count these as ecological votes. |

### Counts

- **C1:** 2
- **C2:** 20
- **C3:** 14
- **C4:** 1
- **D0:** 29
- **Total:** 66

Thus, only **37/66 receipts contain direct ecological evidence or a biological evidence boundary**; 29/66 exist to make those inferences auditable.

## The hierarchy story after deduplication

### 1. Regional level — direction is shared, simple annual mechanisms are not

**Strong context:** `PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1` shows that the five Palmer Adélie island trajectories share an exceptionally strong long-term component (**PC1 = 96.4%**) while annual growth synchrony is only moderate.

**Scope-limiting negatives:** frozen annual sea-ice duration, low-frequency 3/5/7-year sea-ice duration, and October snowfall × habitat formulations all fail their decision rules.

**Defensible statement:** regional forcing plausibly sets the long-term direction, but the tested simple annual or smoothed environmental formulations do not identify that forcing.

### 2. Static place level — no transferable Antarctic-wide rule is confirmed

The Antarctic breeding-option / terrain atlases and their many recovery gates are **D0**, not positive ecological evidence.

The real-data Paper 2 interaction is negative in all three species at the point-estimate level, but the prespecified cross-species permutation test is **non-confirmatory** (`p = 0.0947`), no species survives Holm correction, and the 1–5 km sensitivity is scale-dependent. The radius sign reversal itself is null-compatible.

The detectable-effect analysis adds a useful bound: the design would usually detect a common interaction around (|\gamma_{AH}| \approx 0.50–0.55), but it is weak for effects around 0.30.

**Defensible statement:** there is no confirmed common static island-architecture rule of the tested magnitude and form; very large common effects are constrained, while moderate effects remain unresolved.

### 3. Species / phenotype level — apparent island phenotype is mostly borrowed from species composition

The exploratory Palmer phenotype analyses show that assemblage-level island differentiation is largely species sorting. Within Adélie, fixed island morphology effects are weak, pairwise contrasts reverse across years, and island identity transfers poorly across years.

These are **C2 exploratory**, not causal evidence for plasticity or adaptation.

**Defensible statement:** a single-season island phenotype should not be treated as a persistent within-species island property.

### 4. Within-population spatial configuration — the only positive signal with prospective external replication

**Discovery (C2):** Palmer Cormorant, Humble, and Litchfield show declines in effective breeding-component number of approximately **19%, 51%, and 83%**, more extreme than fixed-composition proportional-thinning nulls under Poisson, CV10%, and CV20% count-error sensitivities.

**Independent geographic replication (C1):** Signy Adélie prospectively replicates concentration beyond the same logic.

**Cross-species replication (C1):** Signy chinstrap prospectively replicates it again.

The component-level route is not universal: Palmer loses its initially dominant unit, whereas Signy retains and strengthens the initial core. Bounded post-hoc scaling finds positive (kappa) in all five local trajectories, but no universal threshold and no successful ratchet rule.

**Defensible statement:** declining *Pygoscelis* populations can reorganize toward fewer effective breeding components beyond proportional thinning. The replicated quantity is the **direction of spatial reorganization**, not a universal exponent or refuge mechanism.

### 5. Mechanism level — several traces survive, none identifies the individual process

The N_eff → next-year growth family must be read as one chain, not six positive endpoints:

1. initial held-out gain was small;
2. synchronized year-block permutation showed that predictive gain is null-compatible (`p = 0.262`);
3. the positive conditional coefficient survives circular-shift, mechanical-coupling, count-error, and demographic-momentum diagnostics.

**Final state:** a weak but robust **conditional association**, not a validated predictive mechanism.

Performance-linked redistribution is also bounded:

- Palmer lag-2/3 redistribution is supported in a provenance-repaired exploratory lane;
- the delayed 4–5 year recruitment echo is rejected;
- the specific win-stay/lose-switch asymmetry is rejected;
- the frozen Signy primary lag-2 replication fails (`p = 0.279`).

Reproductive evidence is similarly bounded: no Palmer-wide Allee-like reproductive law and no supported pre-extinction reproductive collapse.

**Defensible statement:** the aggregate data are compatible with short-lived local reallocation and persistent local state, but do not identify movement, retention, recruitment, mortality, or cue use as the mechanism.

### 6. Individual-process level — the public-data bridge is absent

The Palmer mark–resight audit is **C4**: banding and standardized resighting are documented, but no public table links individual ID to later breeding-season colony/subcolony and breeding status.

That means the key individual-level discrimination cannot be executed reproducibly from the public data located in the audit.

## Do not double-count these families

| Evidence family | Receipts that belong together | Final interpretation |
|---|---|---|
| **N_eff conditional association** | colony erosion; year-block permutation; circular shift; mechanical coupling; circular coupling; demographic momentum | Conditional coefficient robust; held-out predictive gain **not** supported. |
| **Hierarchical variability / beta** | raw hierarchy; component-count audit; count-error null | Observed sub-island separation exists, but robustness fails under the inherited uncalibrated CV20 scenario. |
| **Palmer concentration** | Palmer concentration + Torgersen spatial triangulation | Palmer is the **discovery**, not an independent replication. |
| **Signy Adélie concentration** | strict-epoch V2 + later canonical Signy concentration + quality audit | One external Adélie replication, not multiple independent replicates. |
| **Contraction scaling** | scaling-rules summary + scaling-law synthesis | One bounded post-hoc search; (kappa \approx 0.25) is descriptive, not a law. |
| **Phenotype reassembly** | exploratory result + final phenotype result | One exploratory phenotype family, not two independent demonstrations. |
| **Paper 2 static-place hypothesis** | many D0 recovery/audit receipts + first real fit + permutation + scale/radius sensitivities | One ecological primary result: **non-confirmatory** common interaction; design gates are not votes. |
| **Performance redistribution** | Palmer lag profile / memory / win-stay diagnostics + Signy replication | Locally plausible Palmer process; **no independent Signy replication**. |

## Main-paper evidence ledger

A readable manuscript table should not contain 66 rows. The 66-row CSV belongs in Supporting Information / repository provenance. The main paper can use the following compressed ledger.

| Hierarchy | Strongest positive evidence | Strongest limiting evidence | Final status |
|---|---|---|---|
| **Regional direction** | Five Palmer islands: PC1 96.4% | annual and 3/5/7-year sea-ice duration; snowfall × habitat fail | **Context established; mechanism unresolved** |
| **Static place / island architecture** | negative interaction point estimates are directionally concordant | primary cross-species permutation p=0.0947; scale reversal null-compatible; MDE80 ≈0.50 | **No confirmed transferable static rule** |
| **Species / phenotype** | species composition explains assemblage differentiation | within-Adélie island identity weak/non-transferable | **Exploratory reassembly, not fixed ecotype** |
| **Within-population configuration** | Palmer discovery + Signy Adélie C1 + Signy chinstrap C1 | route and (kappa) magnitude are heterogeneous | **Only replicated positive ecological signal** |
| **Mechanistic trace** | robust conditional N_eff coefficient; Palmer short-lag redistribution | predictive gain p=0.262; Signy lag-2 replication p=0.279; win-stay/lose-switch fails | **Suggestive, not identified** |
| **Individual process** | — | public mark–resight bridge absent | **Data-limited** |

## What can anchor claims

### Claim A — can be stated positively

> Declining Adélie and chinstrap penguin populations repeatedly become concentrated into fewer effective monitored breeding components beyond proportional thinning.

Why: Palmer is a strong discovery, and the same endpoint was prospectively frozen and supported in an independent Signy Adélie system and then in Signy chinstrap.

### Claim B — can be stated as hierarchy/context

> Long-term regional direction is much more coherent than annual local dynamics, while tested static place descriptors and simple environmental responses do not yield a confirmed transferable rule.

Why: the regional pattern is strong, and the negative mechanism/static-place tests are bounded and explicit.

### Claim C — must remain qualified

> Breeding configuration contains information associated with near-term demography.

Required qualifier: this is a conditional association, not a robust held-out predictor or identified causal mechanism.

### Claim D — cannot be made

Do not claim a universal (kappa), a common collapse threshold, a universal large-colony refuge, win-stay/lose-switch, a Palmer-wide Allee mechanism, a common static island-architecture law, or an identified individual movement process.

## Program-level stopped routes outside the 66-result ledger

The 66-row inventory is defined strictly as `results/*.json` on main. Some routes can stop before a final result receipt exists and therefore must **not** be silently added to the 66 count. Examples discussed in the program history include additional population/region routes such as HUMPOP and Ross Sea extensions. These belong in a separate “not executed / no final result receipt” appendix if documented from their frozen contracts or branch provenance.

The one stopped route already represented among the 66 receipts is the Palmer individual mark–resight bridge.

## Bottom line

The evidence ledger sharpens the story rather than inflating it:

> **Direction is visible at the regional level, but the most transferable positive ecological information is in changing breeder configuration within populations. Static island traits and simple environmental formulas do not provide a confirmed common rule; configuration contraction does, through independent geographic and cross-species replication. The individual process producing that contraction remains below the resolution of the available public data.**

That is a stronger claim than “one positive result among 66 tests,” because it explicitly shows which of the 66 were outcome-blind design gates, which were later diagnostics of the same endpoint, which were negative tests that narrow the claim, and which two receipts provide the actual prospective replication.
