#!/usr/bin/env python3
"""Source-verified Adélie nesting reallocation across region, 250-km block, colony.

Post-result accounting identity, not bird migration, climate causality or p-value.
The 19/26/35 cohorts are overlapping actual original census rosters.
"""
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
MACRO=HERE.parent
D=pd.read_csv(MACRO/"latitudinal_scale_20261115/original_adelie_19_26_35_site_growth_cohorts.csv")
P=pd.read_csv(HERE/"three_level_nested_allocation_results.csv").set_index("cohort")
R=pd.read_csv(HERE/"three_level_region_contributions.csv")
B=pd.read_csv(HERE/"three_level_block_contributions.csv")
expected={"all_three_decades":19,"two_plus_endpoint_years":26,"one_plus_endpoint_year":35}
assert len(D)==80 and D.groupby("cohort").size().to_dict()==expected
assert D.species.eq("ADPE").all()
assert (D[["n_early","n_late"]]>=0).all().all() # genuine zero counts retained
assert not D.duplicated(["cohort","site_id"]).any()

# Cross-check the original-count roster identities against archived census
# source-level tables, not the already-computed summary alone.
T=pd.read_csv(MACRO/"allocation_20261115/original_three_decade_43_source_site_species.csv")
U=pd.read_csv(MACRO/"allocation_20261115/original_strict_paired_end_50_source_site_species.csv")
V=pd.read_csv(MACRO/"latitudinal_scale_20261115/original_35_adelie_2decade_source_rows.csv")
for cohort,raw,c0,c1 in [
 ("all_three_decades",T[T.species=="ADPE"],"median_original_nest_count_0","median_original_nest_count_2"),
 ("two_plus_endpoint_years",U[U.species=="ADPE"],"site_median_observed_nests_early","site_median_observed_nests_late"),
 ("one_plus_endpoint_year",V,"n_early","n_late")]:
 d=D[D.cohort==cohort].set_index("site_id").sort_index()
 q=raw.set_index("site_id").sort_index()
 assert len(d)==len(q) and set(d.index)==set(q.index)
 for target,source in [("n_early",c0),("n_late",c1),("latitude","latitude")]:
  assert np.max(np.abs(d[target]-q[source]))<1e-7
 assert (d.source_region==q.source_region).all()
 assert (d.polar_250km_block==q.polar_250km_block).all()

def weighted(series,weights):
 return float(np.dot(np.asarray(series,float),np.asarray(weights,float))/sum(weights))
comparisons=0
for cohort,d in D.groupby("cohort"):
 N0=d.n_early.sum(); N1=d.n_late.sum()
 total=111.195*(weighted(-d.latitude,d.n_late)-weighted(-d.latitude,d.n_early))
 source=P.loc[cohort]
 reg=block=within=fixregion=fixblock=0.0
 for region,g in d.groupby("source_region"):
  a,b=g.n_early.sum(),g.n_late.sum();pa,pb=a/N0,b/N1
  mu0,mu1=weighted(-g.latitude,g.n_early),weighted(-g.latitude,g.n_late)
  reg+=111.195*(pb-pa)*(mu0+mu1)/2
  fixregion+=111.195*pa*(mu1-mu0)
  row=R[(R.cohort==cohort)&(R.region==region)]
  assert len(row)==1
  assert abs(row.iloc[0].within_region_southward_shift_km-111.195*(mu1-mu0))<1e-8
  gw0=g.n_early.to_numpy(float)/a;gw1=g.n_late.to_numpy(float)/b
  si0=g.sic_early.to_numpy(float);si1=g.sic_late.to_numpy(float)
  ice0=float(gw0@si0);ice1=float(gw1@si1)
  climate=float((gw0+gw1)/2@(si1-si0))
  allocation=float((gw1-gw0)@((si0+si1)/2))
  assert abs(ice1-ice0-(climate+allocation))<1e-8
  assert abs(row.iloc[0].observed_within_region_nest_weighted_SIC_change_pp-(ice1-ice0))<1e-8
  assert abs(row.iloc[0].within_region_ice_nest_reallocation_component_pp-allocation)<1e-8
  comparisons+=3
  for key,h in g.groupby("polar_250km_block"):
   x0,x1=h.n_early.sum()/a,h.n_late.sum()/b
   v0,v1=weighted(-h.latitude,h.n_early),weighted(-h.latitude,h.n_late)
   block+=111.195*(pa+pb)/2*(x1-x0)*((v0+v1)/2-(mu0+mu1)/2)
   within+=111.195*(pa+pb)/2*(x0+x1)/2*(v1-v0)
   fixblock+=111.195*pa*x0*(v1-v0)
   q=B[(B.cohort==cohort)&(B.region==region)&(B.polar_250km_block==key)]
   assert len(q)==1
   assert abs(q.iloc[0].share_early_given_region-x0)<1e-8
   assert abs(q.iloc[0].share_late_given_region-x1)<1e-8
   comparisons+=2
 for name,v in [
  ("observed_nest_weighted_southward_km",total),
  ("between_reporting_regions_km",reg),
  ("between_250km_blocks_within_regions_km",block),
  ("within_250km_blocks_km",within),
  ("counterfactual_fixed_1990s_region_shares_southward_km",fixregion),
  ("counterfactual_fixed_1990s_region_and_block_shares_southward_km",fixblock)]:
  assert abs(source[name]-v)<1e-8,(cohort,name,source[name],v)
  comparisons+=1
 assert abs(total-reg-block-within)<1e-8
print("PASS: 80 source-real overlapping cohort observations; 19/26/35 original IDs, "+str(comparisons)+" 3-level geographic/ice identity checks; no p-values")
