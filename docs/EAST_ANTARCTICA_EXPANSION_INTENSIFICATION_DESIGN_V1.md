# East Antarctica penguin expansion–intensification route v1

**Status:** pre-data source/identifiability route. Independent follow-up only. It must not delay, reframe, or rescue the Ecology submission paper.

## Biological question

When an Adélie penguin population grows, **where do the additional breeders go?**

Do growing populations rebuild/expand their breeding-site network by colonizing suitable empty sites, or do they primarily intensify already occupied colonies? And does the answer depend on island isolation and the spatial fragmentation of breeding habitat?

The subject is the penguin population. Island structure is the environmental constraint on its redistribution.

## Classical baseline and generated alternative

### H_classic — spatial expansion

Under a colonization–extinction / incidence-function view, a suitable empty breeding site should become easier to colonize when:
- source populations are larger or growing;
- the site is less isolated from occupied breeding sites;
- more occupied breeding sites occur nearby.

Population growth should therefore create at least some **occupancy expansion** where suitable empty sites are available.

### H_colonial — intensification / settlement feedback

If settlement is strongly conditioned by conspecific presence, site fidelity, or switching costs, additional breeders can preferentially enter already occupied colonies. Empty but physically suitable sites can remain empty even while nearby populations grow.

This predicts a divergence between:
- **numerical recovery/growth**, and
- **spatial recovery/expansion**.

### Interaction prediction

The strongest generated prediction is not that all growing penguin populations fail to expand.

It is:

> **The conversion of population growth into spatial expansion should decline as functional isolation increases.**

Thus the ecological endpoint is **expansion versus intensification**, conditional on the island/breeding-site network.

## Why East Antarctica

This route uses three independent source families:

1. **Direct breeding-site occupancy**
   - Southwell et al. 2016, *Site occupancy by breeding Adélie penguins in East Antarctica*
   - DOI: 10.4225/15/57590498D301C
   - presence/absence observations by geographic breeding site and split-year breeding season, approximately 1950s–2012.

2. **Potential breeding habitat / spatial reference**
   - Southwell et al. 2016, *Sites of potential habitat for breeding Adélie penguins in East Antarctica*
   - DOI: 10.4225/15/5758F4EC91665
   - geographic sites of ice-free coastal land, including islands and continental outcrops, with stable spatial identifiers.

3. **Population abundance**
   - Southwell et al. 2015, PLOS ONE 10:e0139877
   - DOI: 10.1371/journal.pone.0139877
   - standardized long-term abundance comparisons at 99 breeding sites; relevant population data are in the paper/S1 file.

Published work already establishes that East Antarctic Adélie abundance increased broadly and that true occupancy events are rare and easy to misclassify. This route therefore **does not claim a blind discovery of colonization or expansion**. Its purpose is to test the spatial conditions under which growth is expressed as expansion versus intensification.

## Stage A — source and identifiability gate only

Stage A may inspect:
- metadata HTML;
- direct-download URLs;
- archive/file names;
- file hashes;
- table names;
- column headers;
- row counts;
- identifier formats;
- temporal and spatial coverage metadata.

Stage A must **not**:
- count occupied versus empty records;
- count colonization/extinction events;
- calculate distances for outcome-bearing transitions;
- fit any ecological model;
- search thresholds or redefine site identities.

Required source support:
1. occupancy data have a stable breeding-site identifier, season/year, and explicit occupancy state;
2. potential-habitat data have a stable site identifier and coordinates;
3. the occupancy identifier can be linked exactly to the spatial reference or by an outcome-blind mapping supplied by the source;
4. abundance data contain site or regional identities plus at least two comparable abundance estimates;
5. there is a pre-outcome way to map abundance units to occupancy spatial groups/regions.

If any bridge is unavailable, the route stops or is reformulated **before** occupancy outcomes are summarized.

## Detection-error rule

Direct field occupancy observations are primary.

Satellite-only apparent absence/presence must not be treated as equivalent to direct occupancy because prior work shows that small colonies can be omitted and false colonization/extinction events can result.

No “not reported = absent” coding is allowed.

## Stage B — estimand freeze after Stage A, before event counting

If Stage A passes, Stage B must freeze all of the following before counting colonizations:

### Unit
Potential breeding site × breeding season (or the coarsest temporal interval justified by the source).

### Availability
A site enters the risk set only if it is a recognized potential breeding-habitat site and has an explicit survey/observation in the relevant interval.

### Colonization
Explicit absence at a directly observed survey followed by explicit presence at a later directly observed survey, with no inference through an unobserved interval unless the interval-censoring rule is frozen first.

### Extinction
Analogous explicit presence → explicit absence transition; secondary to the expansion question.

### Isolation
Primary: great-circle distance to the nearest occupied breeding site at the previous observed state.

Secondary, only if support permits:
- number of occupied sites within a single frozen radius;
- distance-weighted occupied-site connectivity.

No radius search after outcomes.

### Source pressure
Primary abundance-pressure variable must be chosen from the abundance-source support structure before occupancy transitions are counted. If only regional abundance is bridgeable, use regional abundance/growth and do not invent site-level source abundance.

## Primary future comparison

The primary future endpoint will contrast colonization hazard among suitable empty sites as a function of:

1. physical isolation;
2. source/regional population pressure;
3. their interaction.

The generated prediction is:

> **population growth should translate into colonization primarily where isolation is low; high isolation should channel growth toward intensification of already occupied breeding sites instead.**

A social-attraction interpretation is **not identified** by this model alone. It would require independent settlement/movement evidence or a stronger contrast between physically suitable empty sites with and without nearby conspecific cues.

## Expansion–intensification accounting

If abundance and occupancy can be aligned over the same intervals, report separately:

- change in total abundance;
- number/rate of newly occupied or reoccupied suitable sites;
- change in abundance at sites occupied at interval start.

Do not collapse these into one arbitrary index unless a dimensionally interpretable index is frozen before outcomes.

## Stop rules

Stop rather than rescue if:
- occupancy absences are not explicit;
- site IDs cannot be bridged to spatial coordinates without outcome-informed fuzzy matching;
- fewer than 10 directly observed colonization events are available for the planned model;
- abundance/occupancy intervals cannot be aligned at a defensible regional scale;
- detection method confounds colonization status in a way that cannot be frozen independently of outcomes.

No low-count pseudo-absence threshold, post-outcome distance radius, alternate geography, or selective period may rescue a failed gate.

## Relation to current evidence

This route is generated by, but inferentially independent of:
- replicated breeding-space concentration during Palmer/Signy decline;
- descriptive weak spatial recovery during abundance rebounds;
- MAPPPD increasing networks in which abundance rose while effective breeding-site number did not increase.

Those results motivate the question; they do not count as evidence for this future East Antarctic test.
