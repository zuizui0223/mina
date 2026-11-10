# Frozen Ross observation-stage chronology, 2026-11-09

**Design status:** Post-result analytical audit, not independent preregistration. Originally verified Ross USAP-DC data: 601443 band inventory and 601444 resights, publisher MD5 aaaa... (full below). Previous baseline 193638 source events, 94678 valid events, 15157 strict nest events, 7132 age≥2 chick-band resighted individuals, 506 off-natal resighted, 64 documented off-natal strict nest, 3 two-colony strict breeding-site switches. Prior 2026 Dugger et al. Frontiers DOI 10.3389/fevo.2026.1868960 already studies prospecting and recruitment, so this is source coverage diagnosis rather than novel migration-rate discovery.

## Question

Among the **64** chick-banded birds with original strict active nests at a non-natal colony, was a **same-foreign-colony visit documented in a strictly earlier breeding year**? Or did the first directly observed foreign-colony record already include nest activity? Distinguish actual prior-year observation from a hypothetical prior visit, which cannot be ruled out by undetected years.

## Frozen original-data gates

- Publisher uncompressed CSV MD5: band inventory (601443) **3da33defa4decc82b6e317c7fa9f9044**; resights (601444) **aaae6ddad6d12081b5a68466794438a2**, 229 inventory ranges, 193638 raw resighting events, 14 malformed free-text notes rows repaired only in RAM, four overlapping inventory band labels excluded.
- Original unique ID in inventory range, original home colony matches resight orig_col, proofed=1 and bandseen=Y, recorded date and season consistent, colonies BEAU/BIRD/CROZ/ROYD. CHIC from source inventory and resight season age≥2. Do not change the six source route results or subset years after opening outcome.
- Strict nesting if (status INC and 1–2 source eggs) or (status BR and 1–2 source chicks). This operational interpretation is aligned to the published study's description but does not replace a primary-source status codebook.
- Collapse each individual × site × season to **observed** and **strict nesting** states. A site-year with nesting cannot be treated as a pure visitor even if earlier/later records show no nest. Multiple colony observations same season are not evidence for annual breeding-site change.

## Frozen calculations

1. For each of the 64, define first foreign colony of a directly documented strict nest, first strict nest season at it, earliest documented visit season to that same colony. Categorize strictly earlier-year visit; same first observed season already nesting; or competing/tied first-nest sites. Record gap (years) and original banding age at documented nest. No individual identity, exact track or raw notes published.
2. Count prior same-season **earlier-calendar-date nonnesting event** at the destination separately; it is not an independently identified prebreeder state.
3. Count any strict active nesting observed at natal colony before, same season, or after first foreign nest. Unknown years stay unknown, not nonbreeding years.
4. Across 506 off-natal seen birds, count strict nesting anywhere and at foreign colony; do not divide 64/506 to estimate immigration/settlement probability.
5. Original colony × season record coverage and observation effort bias reported separately. No p-values, resistance fitting or post hoc geographic subset selection.
6. Reconcile previously validated 193638/94678/15157/7132/506/64/3. If mismatch, halt rather than alter filters.

## Biological boundary

Observed foreign visit preceding observed foreign nest is a **sequence of detections**, not the true first prospecting date or actual settlement latency. False absences are plausible, especially because Cape Bird regular resighting effort ended in 2013 and observation effort differed drastically by colony and season. 2026 multistate work already estimates these state transitions; no first-discovery claim.

Keep Ross stage analysis on Draft PR #212; do not merge as a causal model of colony relocation, summer Chinstrap GPS accessibility or future Antarctic warming breeding change into PR #206. Source ZIPs and per-bird identities remain outside Git.
