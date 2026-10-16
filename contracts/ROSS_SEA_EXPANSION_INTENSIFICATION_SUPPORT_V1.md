# Ross Sea Adélie expansion–intensification support audit v1

**Status:** pre-effect support audit. No breeding-pair outcome is summarized or modeled.

## Candidate data

Manaaki Whenua / Antarctica New Zealand Ross Sea Adélie penguin aerial census:
- DOI: 10.7931/kf06-x745
- coverage: 1981–2024
- published description: breeding-pair aerial census across 39 colonies between 158°E and 175°E; repeated regional reconnaissance also discovered previously unreported colonies.
- license on the current DataStore record: CC BY-NC 4.0.

## Biological question generated before opening counts

During numerical recovery of an Adélie metapopulation, is growth first absorbed by already occupied colonies (intensification), or expressed as spatial expansion to additional breeding colonies?

This is an independent test of the generated **attrition–intensification asymmetry**:
- decline in Palmer/Signy is dominated by unequal local losses;
- recovery is predicted to be expressed first as gains within surviving occupied colonies, with expansion a separate transition.

## Outcome-blind support audit

The audit may inspect:
- workbook and sheet names;
- column names;
- row counts;
- unique colony identifiers/names;
- year/date fields and distinct years;
- coordinates/region fields;
- survey-method, survey-status, missingness or quality fields;
- whether a breeding-pair/count field is populated, but not its numerical values.

It must not summarize:
- breeding-pair magnitudes;
- trends;
- first-to-last changes;
- colony shares;
- population growth;
- occupancy transitions inferred from count values.

## Support gate

A future count analysis is eligible only if the data contain:

1. a stable colony identifier or name;
2. survey year/season;
3. breeding-pair count field;
4. at least 3 colonies with repeated counts in a common regional grouping;
5. at least 10 distinct survey years for one such grouping;
6. a documented representation of non-survey/missing counts distinct from true zero, or sufficient metadata to avoid treating missing surveys as absence.

For a formal **colonisation/expansion** endpoint, an additional gate is required:
7. search effort or explicit historical absence must distinguish a newly occupied site from a merely newly discovered/first-surveyed colony.

If gate 7 fails, the dataset may test intensification among established colonies but **must not** test colonisation.

## If support passes

Before opening breeding-pair magnitudes, freeze:

### Primary independent test — established-colony intensification

Within one objectively defined regional metapopulation with >=3 repeatedly censused colonies:
- define a growth interval using metadata or an external published period, not the unseen count outcomes;
- fix the colony roster to colonies known/monitored at interval start;
- calculate total N and effective colony number E across the fixed roster;
- decompose total growth into site-level absolute gains/losses;
- quantify what fraction of gross positive gains is absorbed by colonies already large at baseline.

The key hypothesis is not a universal rich-get-richer rule. It is:

> numerical recovery can occur largely within the established colony network without requiring spatial expansion.

### Secondary expansion endpoint

Only if gate 7 passes, quantify breeder gains attributable to genuinely new/reoccupied colonies versus persistent occupied colonies.

## Boundaries

- First observation is not colonisation unless prior adequate search establishes absence.
- Newly discovered colonies are not automatically newly founded colonies.
- Aerial census colony units are physical breeding colonies, not directly equivalent to Palmer LTER colony_code units.
- The support audit cannot alter Paper 1.
