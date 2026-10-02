# Palmer colony-code continuity audit v1

## Question

Do Palmer LTER `colony_code` values represent stable physical breeding colonies through time strongly enough to interpret post-hoc dominant-unit turnover biologically?

## Public evidence supporting continuity

1. **Official variable semantics.** The Palmer ERDDAP metadata defines `colony_code` as a code identifying an ecosystem colony, with the colony number referring to a colony on a specific island. This supports interpreting codes as named colony units rather than arbitrary row identifiers.
2. **Standardized colony-level monitoring.** Palmer seabird work follows CEMP standard methods, and historical Palmer sampling schedules specify breeding-population censuses once per colony across Humble, Torgersen, Litchfield, Christine and Cormorant.
3. **Historical mapping.** The 1989–90 AMLR program reported that maps of 39 colonies in the five Adélie rookeries near Palmer Station were developed from aerial photographs and charts, followed by ground-truthing after the breeding season.
4. **Independent narrative continuity at Litchfield.** Field accounts from 2005–06 explicitly identify the final Litchfield redoubt as Colony 8, consistent with the census code that remains at the end of the LTER series rather than suggesting a newly assigned label.
5. **Biological use of colony-size classes.** Palmer investigators have previously treated breeding groups/colonies as persistent biological units when discussing the proportions of birds in large and small breeding groups and island-specific decline.

## What the public record does NOT establish

- No public, versioned geometry or colony-boundary crosswalk was found that demonstrates that every Palmer code retained exactly the same spatial polygon from 1991–2017.
- An unchanged set of code labels therefore rules out roster turnover but does not by itself rule out undocumented boundary adjustment, splitting/merging under a retained label, or other field-operational changes.
- The strongest vulnerability is the post-hoc statement that the identity of the dominant physical breeding group changed. This depends on longitudinal identity semantics more strongly than the island-total decline.
- The primary N_eff analysis is also based on nominal colony units and therefore must be described as concentration among monitored census colonies/components, not direct contraction of mapped physical area.

## Consequence for manuscript interpretation

1. Keep Palmer as the **discovery system**.
2. Keep the primary Palmer concentration result because official metadata, standardized colony-level methods and historical mapping support the ecological meaning of the units, while clearly naming them **monitored census colonies/components**.
3. Put the confirmatory weight on the prospectively frozen Signy Adélie and chinstrap replications.
4. Remove Palmer-versus-Signy dominant-unit route contrast from the Abstract and central claim.
5. Relegate the Palmer/Signy dominant-unit comparison to Supplementary material as **post-hoc nominal census-unit trajectories**.
6. Do not claim that Palmer dominance turnover reflects movement among fixed physical polygons unless the data providers confirm boundary/code continuity.

## Contact rationale

The Palmer metadata explicitly encourages users to contact the data authors when questions about methodology or interpretation arise. A short data-semantics inquiry should therefore be sent before or during submission, without delaying the frozen Signy-based confirmatory claim.

## Public sources checked

- Palmer ERDDAP metadata for `AdeliePenguinCensus`, including variable definitions, CEMP methods, contributor contact and data-use notes.
- Palmer LTER 1996–97 standard sampling schedule describing once-per-colony breeding-population censuses.
- AMLR 1989–90 report describing mapping of 39 colonies across five Adélie rookeries.
- Published/narrative record identifying the terminal Litchfield breeding group as Colony 8.
- Palmer LTER material discussing large versus small breeding groups as biologically meaningful units.
