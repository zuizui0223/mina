# Evidence hierarchy synthesis from the 66-result ledger — v1

**Source:** `contracts/EVIDENCE_LEDGER_66_V1.json` and `data/EVIDENCE_LEDGER_66_V1.csv`.

## One-sentence scientific story

> Penguin decline has a regional direction but a local spatial form: static place traits and apparent island phenotypes do not yield a transferable rule, whereas the redistribution of breeders among breeding components is the only ecological signal in the 66-record program that reaches prospectively frozen independent replication.

This sentence is deliberately narrower than a causal mechanism claim. The ledger establishes where reproducible information appears; it does not establish which individual process creates that information.

## What the 66 records actually are

The repository contains 66 result JSONs on main, but they are not 66 equivalent hypothesis tests.

- **3 A-tier records**: prospectively frozen replication records. All are breeding-space concentration; two Signy Adélie records share one independence group, so these represent **2 independent replication families**.
- **18 B-tier records**: robust exploratory, fixed-specification, or triangulating ecological evidence.
- **15 C-tier records**: informative negatives, failed replications, directional reversals, sensitivity failures, or quantitative scope limits.
- **4 D-tier records**: analyses stopped before ecological inference because a data/recovery gate failed.
- **26 N records**: audits, predictor construction, synthetic recovery, intermediate non-inferential fits, and reproducibility checks. They govern what was allowed to be tested but do not count as ecological evidence.

Thus only 40/66 records are ecological evidence records (A–D), and fewer still are statistically independent evidence families.

## Main-text evidence table

| Information level | Question | Strongest records | Evidence class | Result | Allowed manuscript claim |
|---|---|---|---|---|---|
| **Regional direction** | Do nearby islands move together, and can a simple regional forcing explain the annual response? | Palmer synchrony (#19); sea-ice/habitat (#32); low-frequency sea ice (#33); snowfall×habitat (#34) | B + C | Five islands share a dominant long-term decline (PC1 96.4%), but the frozen annual and low-frequency sea-ice-duration models and snowfall×habitat model fail their directional tests. | Regional conditions plausibly set the long-run direction, but the tested simple annual/low-frequency proxies do not identify the driver. |
| **Static place** | Do fixed breeding-site traits yield a transferable Antarctic resilience rule? | Paper2 primary permutation (#58); A-only buffering (#36); detectable-effect bound (#39); radius null (#52); scale/trait sensitivity (#53) | C | The primary cross-species A×H permutation is non-confirmatory (p=0.0947); simple A is unsupported; large common effects are bounded; radius/metric sensitivity prevents a general static-architecture law. | Static site architecture did not produce a confirmed transferable rule; very large common effects are unlikely, but moderate effects remain unresolved. |
| **Species/composition** | Is apparent island individuality a persistent within-species phenotype? | Palmer phenotype exploratory result (#8); phenotype reassembly (#30) | B | Much apparent site differentiation is species composition; within Adélie, fixed island morphology is weak and cross-year island identity is poorly transferable. | Apparent island phenotype is substantially borrowed from species composition and temporal reassembly; persistent island ecotypes are not established. |
| **Within-island configuration** | Does decline reorganize how breeders are distributed among breeding components beyond proportional thinning? | Palmer concentration discovery (#12); Signy Adélie (#61/#64); Signy chinstrap (#62) | **B → A** | Palmer discovered robust concentration under frozen error sensitivities; prospectively frozen Signy tests replicate it independently in Adélie and across species in chinstrap. | **This is the only positive ecological endpoint family that reaches A-tier replication.** Decline can concentrate reproduction into fewer effective monitored breeding components beyond proportional thinning. |
| **Configuration route / scaling** | Is the same local mechanism or universal scaling constant responsible? | Dominance routes (#5); scaling (#6–7); Torgersen triangulation (#14) | B | Palmer turns over its initially dominant component, Signy retains its core; local κ values are positive but heterogeneous; fixed collapse thresholds are unsupported. | The replicated endpoint is more general than its route or rate. Do not claim a universal refuge, threshold, or quarter-power constant. |
| **Mechanism trace** | Does configuration predict demography or respond to reproductive performance? | N_eff association family (#13, #22–25); year-block null (#26); performance memory/lags (#28–29); Signy redistribution replication (#65) | B + C | N_eff has a small structured-null-robust conditional association but not a robust predictive gain. Palmer performance→redistribution is fixed-specification suggestive, but its frozen Signy primary replication fails. | Configuration behaves like an ecological state signal; a transferable causal mechanism is not established. |
| **Specific mechanisms** | Are large groups, Allee-like reproduction, or win-stay/lose-switch the mechanism? | >50-pair threshold (#18); reproductive denominator audit (#31); win-stay/lose-switch (#35) | C | Protective large-group prediction reverses; Palmer-wide reproductive law and pre-extinction reproductive collapse are unsupported; specific lose-switch asymmetry fails. | These simple mechanistic stories are ruled out or substantially narrowed. |
| **Individual process** | Can the aggregate signal be resolved into retention/dispersal/prospecting? | Palmer mark-resight audit (#21) | D | Public data located in the audit lack the band-to-later-breeding-site bridge needed for direct movement inference. | Individual retention, breeding dispersal, prospecting, immigration, mortality, and nonbreeding remain unresolved by the available data. |

## The logical backbone

The evidence program can be read as a sequence of increasingly local questions.

**1. Region supplies direction, not a simple annual mechanism.**  
The five Palmer islands share a very strong long-term direction, yet the tested sea-ice duration and snowfall formulations do not explain annual or prespecified low-frequency response. The correct role of the synchrony result is context, not a causal climate identification.

**2. Static place does not supply a confirmed transferable rule.**  
Paper2 is especially useful because its negative result is not an uninformative “p>0.05.” Synthetic recovery, observation-model audits, source sensitivities, permutation inference, detectable-effect simulations and radius sensitivities establish what the design could and could not say. The result excludes a large, stable, common static architecture effect more strongly than it excludes moderate or taxon-specific effects.

**3. Species composition explains much apparent site individuality.**  
The phenotype lane weakens the idea that each island carries a persistent, transferable functional phenotype. Assemblage-scale differences are strongly compositional, and within-Adélie island identity is temporally unstable.

**4. Relative breeder configuration is where reproducible ecological information survives.**  
Palmer is discovery-only, but the same abundance-conditioned concentration endpoint is prospectively frozen and replicated at Signy, first geographically within Adélie and then across species in chinstrap. No other positive ecological family in the 66-record ledger reaches this A tier.

**5. The endpoint is reproducible; the mechanism is not.**  
Different dominance routes lead to the same concentration endpoint. N_eff is a weak conditional state association rather than a validated predictor. Performance-linked redistribution remains locally plausible at Palmer but fails its frozen Signy primary replication. Large-group protection, a general Allee-like reproductive mechanism and specific win-stay/lose-switch are not supported.

**6. The next missing level is the individual.**  
Aggregate counts cannot distinguish retention, movement, prospecting, temporary nonbreeding or mortality. The mark-resight audit reaches a genuine data gate rather than a negative biological result.

## Why the negative records belong in the story

The C-tier results are not failed side projects to hide. They progressively remove stronger stories:

- #32–34 remove simple tested regional climate/weather formulations;
- #17 prevents upgrading the variability hierarchy to count-error-robust biological buffering;
- #26 removes the predictive interpretation of N_eff while preserving a weaker conditional association;
- #18, #31 and #35 remove simple large-group, reproductive-collapse and win-stay/lose-switch mechanisms;
- #36, #39, #52, #53 and #58 prevent the static Antarctic architecture analysis from becoming a universal macroecological rule;
- #65 prevents the Palmer performance-redistribution association from being described as a transferable Antarctic mechanism.

This is why a hierarchy-of-information narrative is stronger than a collection of positive results: each negative closes an alternative level or mechanism.

## Evidence-weighting rule for the manuscript

The central biological claim must be stated from the **A-tier independence groups**, not from the number of result files. Palmer concentration (#12) is the discovery that generated the hypothesis. Signy Adélie (#61/#64, one independence group) and Signy chinstrap (#62) are the confirmatory replications.

B-tier evidence can explain robustness, ecological interpretation and boundary conditions, but must not be used to turn a non-confirmatory result into a confirmed claim. C-tier evidence should be reported wherever it closes an attractive alternative. D-tier records document unanswered questions rather than biological absence. N records belong in Methods, provenance, or the full ledger, not in a vote count.

## Important scope note: the ledger is exactly the 66 main result files

Some gate histories discussed elsewhere in the project (for example HUMPOP or later SMP planning) are not represented by one of these 66 main-branch result JSONs. They should not be silently inserted into a “66 endpoint” count. If they are needed in the final narrative, create a separate **unreceipted/external gate appendix** with explicit provenance.

## Natural next question

Once the endpoint family is defined this way, the next independent test is straightforward:

> Does abundance-conditioned breeding-space concentration recur outside *Pygoscelis* in other colonial breeders?

That is a new-data generality test. It is not something the present 66-record ledger can answer by further re-analysis.
