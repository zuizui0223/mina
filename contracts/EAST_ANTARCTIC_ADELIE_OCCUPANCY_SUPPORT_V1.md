# East Antarctic Adélie occupancy support audit v1

**Status:** pre-effect support audit. No occupancy transition effect is computed.

## Candidate data

Southwell et al. (2016), *Site occupancy by breeding Adélie penguins in East Antarctica*,
Australian Antarctic Data Centre, DOI **10.4225/15/57590498D301C**.

The published metadata describes direct presence/absence observations at breeding sites
from the 1950s to 2012, with site coordinates and repeated breeding-season observations.

The associated 2017 paper warns that apparent colonization/extinction events inferred
from incomplete historical/satellite records can be false. Therefore no transition
event is defined until direct-observation support is audited.

## Biological question generated from the Palmer/Signy result

Does local breeding-site loss increase functional isolation and thereby constrain later
spatial recovery of Adélie penguins?

The eventual causal sequence of interest is:

population decline
→ local breeding-site loss
→ loss of occupied neighbours / social connectivity
→ reduced recolonization
→ recovery concentrated in already occupied sites.

## Audit-only fields

The audit may inspect only:
- file/table names and schemas;
- row counts;
- site identifiers;
- breeding-season identifiers;
- coordinates;
- observation-method/source fields;
- whether an occupancy field is populated.

It may calculate support quantities such as:
- number of unique sites and seasons;
- number of sites observed in ≥2, ≥3 and ≥5 seasons;
- duplicate site-season records;
- availability of latitude/longitude;
- number of rows with a nonmissing occupancy field.

It must **not** summarize, compare, model, or plot presence/absence values.

## Support gate

A future transition analysis is structurally eligible only if the direct-observation
table contains:
1. a stable site identifier;
2. a breeding-season/time field;
3. an occupancy field;
4. latitude and longitude or a joinable site table with coordinates;
5. at least 20 sites with observations in at least two distinct seasons;
6. at least 5 distinct breeding seasons represented.

If the gate fails, stop. No alternate data source is substituted on this route.

## Data-use boundary

The AADC metadata lists the data as public under CC BY 4.0, while its citation page
states that contacting the data originator before applying the data is an expected
research norm. This audit may establish support from the public package, but a
confirmatory biological effect analysis should not be opened until that provenance
and contact requirement has been handled explicitly.

## If support passes

Freeze, before opening occupancy outcomes:
- the exact transition definition;
- handling of irregular survey intervals;
- detection/observation-quality exclusions;
- geographic connectivity kernel or distance bins;
- the distinction between persistence, extinction, recolonization, and first colonization;
- the primary test of whether recolonization depends on occupied-neighbour connectivity;
- a history term testing whether previously occupied-but-lost sites behave differently
  from otherwise suitable unoccupied sites.

No outcome-driven threshold search is allowed.
