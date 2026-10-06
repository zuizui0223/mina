# East Antarctica Adélie expansion/recolonization support gate v1

**Status:** frozen after outcome-blind schema audit and before event counting.

## Unit

Primary spatial unit: `geog_site_id`, the published geographic-site unit (a discrete ice-free island or continental rock outcrop).

Primary time unit: split-year breeding season.

Only `occupancy_penguin.xlsx / 2_search events` is used for occupancy outcomes. `geog_sites_all.xlsx / 2_geog_sites_all` supplies site feature, area and centroid coordinates.

## State construction

Use `occurrence` only:
- P = explicit present
- A = explicit absent
- NR = unknown and excluded from state transitions

For multiple records within a geographic site × season:
- any P => site state P;
- otherwise any A => site state A;
- otherwise unknown.

This aggregation is defined because the ecological question is whether the geographic site/island is occupied by breeding Adélie penguins, not whether every named breeding subsite within it is occupied.

No missing record and no NR record is converted to absence.

## Consecutive-season transition requirement

Primary transitions require an observed P/A state in season t and season t+1 with consecutive breeding-season years. Gaps are not bridged.

### First colonization
A -> P where the site has no earlier observed P state.

### Recolonization
A -> P where the site has at least one earlier observed P state followed by at least one observed A state before the return.

### Persistence
P -> P.

### Local loss
P -> A.

## Support outputs only

Stage B may report:
- number of explicit P/A site-season states;
- number of A->P, A->A, P->A, P->P consecutive transitions;
- number of first-colonization and recolonization events;
- number of distinct geographic sites, subgroups and seasons contributing each event class;
- island vs continent event counts;
- expert-validation and vantage support counts.

Stage B must not calculate distances, area associations, colonization coefficients, trend effects, or p-values.

## Gates

### Expansion gate
Proceed to a prospective isolation test only if:
- >=10 first-colonization events;
- >=50 explicit A-risk transitions;
- first colonizations occur in >=3 subgroups.

### Recovery gate
Proceed to a prospective recolonization/hysteresis test only if:
- >=10 recolonization events;
- >=30 previously-occupied A-risk transitions;
- recolonizations occur in >=3 subgroups.

### Island-feature interaction gate
Test island-vs-continent modification only if each feature class has >=5 A->P events and >=20 A-risk transitions.

Failing gates stop that inferential route. They cannot be rescued by NR pseudoabsence, nonconsecutive intervals, alternate site aggregation, low-count thresholds, or selective periods.

## Next stage if a gate passes

Distances, site area and any abundance-pressure predictor remain unopened until the corresponding inferential contract is frozen.
