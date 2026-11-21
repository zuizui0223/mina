#!/usr/bin/env python3
"""Verify source nesting-count sqrt-weight sensitivity to large colonies.

Uses the same original 80 source-census rosters. Descriptive counterfactual,
not a spatially independent significance test or species movement.
"""
from pathlib import Path
import numpy as np
import pandas as pd

here=Path(__file__).resolve().parent
src=pd.read_csv(here.parent/"latitudinal_scale_20261115/original_adelie_19_26_35_site_growth_cohorts.csv")
saved=pd.read_csv(here/"three_level_sqrt_nest_weight_sensitivity.csv").set_index("cohort")
assert len(src)==80 and src.species.eq("ADPE").all()
for cohort,raw in src.groupby("cohort"):
    a=raw.copy()
    a["n_early"]=np.sqrt(a.n_early)
    a["n_late"]=np.sqrt(a.n_late)
    n0=a.n_early.sum();n1=a.n_late.sum()
    total=111.195*(np.average(-a.latitude,weights=a.n_late)-np.average(-a.latitude,weights=a.n_early))
    between=blocks=within=0.
    for _,g in a.groupby("source_region"):
        p0,p1=g.n_early.sum()/n0,g.n_late.sum()/n1
        m0=np.average(-g.latitude,weights=g.n_early)
        m1=np.average(-g.latitude,weights=g.n_late)
        between+=111.195*(p1-p0)*(m0+m1)/2
        anchor=(m0+m1)/2
        for _,h in g.groupby("polar_250km_block"):
            q0,q1=h.n_early.sum()/g.n_early.sum(),h.n_late.sum()/g.n_late.sum()
            v0=np.average(-h.latitude,weights=h.n_early)
            v1=np.average(-h.latitude,weights=h.n_late)
            blocks+=111.195*(p0+p1)/2*(q1-q0)*((v0+v1)/2-anchor)
            within+=111.195*(p0+p1)/2*(q0+q1)/2*(v1-v0)
    assert abs(total-between-blocks-within)<1e-8
    row=saved.loc[cohort]
    assert len(a)==row.n_observed_colonies
    for key,value in (
        ("observed_southward_weighted_latitude_km",total),
        ("between_reporting_regions_km",between),
        ("between_250km_blocks_within_regions_km",blocks),
        ("within_250km_blocks_km",within)):
        assert abs(row[key]-value)<1e-7,(cohort,key)
    assert total>0 and within/total<0.04
print("PASS: 3 original source cohorts, sqrt-weight total and all nested components, no inferred migration")
