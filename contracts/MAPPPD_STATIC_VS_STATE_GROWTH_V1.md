# MAPPPD static-place versus demographic-state decomposition v1

**Status:** post-outcome descriptive analysis. No inferential p-values. This cannot alter or delay the frozen Ecology submission.

## Question

In the three already-exposed increasing MAPPPD networks, which pre-existing property best tracks which monitored sites gain **regional share** during population growth?

This analysis distinguishes three candidate descriptions:

1. **Demographic state:** sites that already held a large share of breeders gain still more share.
2. **Static breeding-space amount:** sites with more mapped ice-free area gain share.
3. **Geographic isolation:** sites closer to another retained occupied site gain share.

The response is fixed before execution as:

```
delta_share = last-season regional share - first-season regional share
```

This avoids treating absolute count gain as independent of total network growth.

## Frozen inputs

- Site-level first/last counts and share changes from `MAPPPD_INTENSIFICATION_DESCRIPTIVE_RESULT_V1`.
- Static site traits reproduced from the previously frozen Antarctic breeding-options hierarchy artifact:
  - `mapped_ice_free_area_ha_2000m`
  - latitude / longitude
- Exactly the same 23 retained sites in the three increasing networks.

No site, network, season, radius or habitat metric can be changed after this document.

## Predictors

For each network:

- `first_share`: first-season share of regional breeders.
- `log1p_ice_free_area`: log(1 + mapped ice-free area within 2 km).
- `nearest_neighbor_km`: great-circle distance to the nearest other retained site in the same network.

Also report the non-inferential density proxy:

```
first_count / mapped_ice_free_area_ha_2000m
```

but do not interpret it as true nesting density because the 2-km mapped ice-free area is not occupied breeding habitat.

## Outputs

For each network, report:

- Spearman rho between `delta_share` and each fixed predictor;
- final dominant site's initial share rank, ice-free-area rank and nearest-neighbor-distance rank;
- whether the final dominant was also the initially dominant site;
- all site-level values for auditability.

No p-values, model selection, pooled regression, alternate distance kernel, or threshold search is allowed.

## Interpretation

This analysis can only say whether exposed redistribution aligns descriptively with static place properties or demographic state.

It cannot identify:
- individual dispersal;
- conspecific attraction;
- true habitat capacity;
- causal effects of area or isolation;
- colonisation of empty sites.
