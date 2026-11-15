#!/usr/bin/env python3
"""Independent, source-pinned check of Adélie nesting reallocation under 435 region/grid designs.

Original input crosswalk: 35 genuine colony points taken from the publisher-audited
595-source-site inventory, with original EPSG:3031/250-km block verified.
Original biological cohort: 80 nested 19/26/35 Adelie colony observations.
Source output: 435 deterministic grouping/offset envelopes.
Neither source absence, individual migration, climate attribution nor p-values
are inferred. A southward guarantee is CONDITIONAL on locking each group's
actual later-decade summed nest counts.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.optimize import linprog

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
cohorts=pd.read_csv(ROOT/"latitudinal_scale_20261115/original_adelie_19_26_35_site_growth_cohorts.csv")
coordinates=pd.read_csv(HERE/"original_35_adelie_sites_fixed_polar_coordinates.csv")
saved=pd.read_csv(HERE/"all_435_grid_origin_source_envelopes.csv")
summary=pd.read_csv(HERE/"grid_resolution_by_roster_summary.csv")
assert len(cohorts)==80 and len(coordinates)==35 and len(saved)==435 and len(summary)==27
assert cohorts.groupby("cohort").size().to_dict()=={
    "all_three_decades":19,"two_plus_endpoint_years":26,"one_plus_endpoint_year":35
}
assert coordinates.site_id.nunique()==35 and cohorts.site_id.nunique()==35
merged=cohorts.merge(coordinates[["site_id","latitude","longitude","source_region",
    "polar_250km_fixed_grid_block"]],on="site_id",validate="many_to_one",suffixes=("","_atlas"))
assert len(merged)==80
assert np.max(np.abs(merged.latitude-merged.latitude_atlas))<1e-8
assert (merged.source_region==merged.source_region_atlas).all()
assert (merged.polar_250km_block==merged.polar_250km_fixed_grid_block).all()
transformer=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
x,y=transformer.transform(merged.longitude.to_numpy(float),merged.latitude.to_numpy(float))
merged["x"]=x;merged["y"]=y
original_blocks=[f"{int(np.floor(a/250000))}:{int(np.floor(b/250000))}" for a,b in zip(x,y)]
assert (merged.polar_250km_block==original_blocks).all()
assert merged.n_early.ge(0).all() and merged.n_late.ge(0).all()

max_abs_error=0.
verdicts=[]
for row in saved.itertuples(index=False):
    q=merged.loc[merged.cohort==row.cohort].reset_index(drop=True)
    if row.grid_km==0:
        groups=q.source_region.astype(str).to_numpy()
    else:
        dx=np.floor(q.x.to_numpy(float)/(1000*row.grid_km)+row.offset_x).astype(int)
        dy=np.floor(q.y.to_numpy(float)/(1000*row.grid_km)+row.offset_y).astype(int)
        groups=np.array([f"{r}|{a}|{b}" for r,a,b in zip(q.source_region,dx,dy)])
        if row.grid_km==250 and row.offset_x==0 and row.offset_y==0:
            assert (np.array([f"{a}:{b}" for a,b in zip(dx,dy)])==q.polar_250km_block).all()
    ids=sorted(set(groups))
    A=np.array([groups==z for z in ids],dtype=float)
    n0=q.n_early.to_numpy(float)
    n1=q.n_late.to_numpy(float)
    south=-q.latitude.to_numpy(float)
    base=np.dot(n0,south)/n0.sum()
    observed=111.195*(np.dot(n1,south)/n1.sum()-base)
    lo=linprog(south,A_eq=A,b_eq=A@n1,bounds=(0,None),method="highs")
    hi=linprog(-south,A_eq=A,b_eq=A@n1,bounds=(0,None),method="highs")
    assert lo.success and hi.success,(row.cohort,row.grid_km,row.offset_x,row.offset_y)
    lower=111.195*(lo.fun/n1.sum()-base)
    upper=111.195*(-hi.fun/n1.sum()-base)
    max_abs_error=max(max_abs_error,abs(observed-row.observed_southward_km),
                      abs(lower-row.lower_bound_km),abs(upper-row.upper_bound_km))
    assert max_abs_error<1e-8,max_abs_error
    assert len(ids)==row.source_n_region_grid_groups
    sizes=np.array([np.sum(groups==g) for g in ids])
    assert int(np.sum(sizes>1))==int(row.n_groups_with_atleast_two_sites)
    assert int(np.sum(sizes[sizes>1]))==int(row.n_sites_in_multi_site_groups)
    assert bool(lower>0)==bool(row.positive_guaranteed)
    verdicts.append(dict(cohort=row.cohort,grid_km=row.grid_km,positive=lower>0))
v=pd.DataFrame(verdicts)
for row in summary.itertuples(index=False):
    part=v[(v.cohort==row.cohort)&(v.grid_km==row.grid_km)]
    assert len(part)==16
    assert int(part.positive.sum())==int(row.n_origins_guarantee_south)
    if row.grid_km<=300:
        assert part.positive.all()
assert len(verdicts)==435
print("PASS: 80 original observation-cohort rows; 35 verified source locations;")
print("435 source region/grid designs; 870 independent scipy HiGHS LP bounds;")
print(f"maximum numerical mismatch {max_abs_error:.3e} km;")
print("100-300 km guarantee all shifted origins; >=400 km guarantee depends on grid origin.")
