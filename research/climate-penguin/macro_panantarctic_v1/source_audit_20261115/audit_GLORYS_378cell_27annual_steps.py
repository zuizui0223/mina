#!/usr/bin/env python3
"""Source-only annual GLORYS/OSI SAF jump diagnostic; not physical attribution.

Input: original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv
from publisher-verified Actions artifact 13829236358.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

p=argparse.ArgumentParser()
p.add_argument("--source",required=True,type=Path)
p.add_argument("--out",required=True,type=Path)
args=p.parse_args()
x=pd.read_csv(args.source)
keys=["GLORYS_cell_y","GLORYS_cell_x"]
assert len(x)==588*28 and x.site_id.nunique()==588
assert set(x.year)==set(range(1993,2021))
assert x[keys].drop_duplicates().shape[0]==378
for name in ["mean_GLORYS_salinity","mean_GLORYS_thetao_C"]:
    assert x.groupby(keys+["year"])[name].agg(lambda z:float(z.max()-z.min())).abs().max()<1e-10
regions=x.drop_duplicates(keys).set_index(keys).source_region
assert x.groupby(keys).source_region.nunique().max()==1 and regions.nunique()==18
frame=x.groupby(keys+["year"],as_index=False).agg(
    sal=("mean_GLORYS_salinity","mean"),
    temp=("mean_GLORYS_thetao_C","mean"),
    sic=("mean_source_SIC_pp","mean")
)
assert len(frame)==378*28 and frame.groupby(keys).year.nunique().eq(28).all()
rows=[]
for field in ("sal","temp","sic"):
    W=frame.pivot(index=keys,columns="year",values=field)
    D=W.diff(axis=1).loc[:,1994:2020]
    baseline=D.loc[:,1994:2018]
    z=(D.sub(baseline.mean(axis=1),axis=0)
        .div(baseline.std(axis=1,ddof=0).replace(0,np.nan),axis=0))
    for year in range(1994,2021):
        change=D[year]
        byreg=pd.DataFrame({"region":list(regions.loc[change.index].values),
                            "value":change.to_numpy()}).groupby("region").value.median()
        rows.append({
            "variable":field,"year":year,
            "median_cell_step":float(change.median()),
            "mean_cell_step":float(change.mean()),
            "median_step_z":float(z[year].median()),
            "n_cells_with_negative_annual_step":int((change<0).sum()),
            "n_cells_below_minus2_baseline_step_sd":int((z[year]<-2).sum()),
            "n_cells_above_plus2_baseline_step_sd":int((z[year]>2).sum()),
            "n_regions_with_negative_cell_median_step":int((byreg<0).sum())
        })
out=pd.DataFrame(rows)
assert len(out)==27*3
sal=out.loc[out.variable=="sal"].set_index("year")
assert int(sal.loc[2019,"n_cells_with_negative_annual_step"])==346
assert int(sal.loc[2019,"n_cells_below_minus2_baseline_step_sd"])==188
assert int(sal.loc[2020,"n_cells_below_minus2_baseline_step_sd"])==54
assert int(sal.loc[2019,"n_regions_with_negative_cell_median_step"])==18
assert int(sal.median_cell_step.idxmin())==2019
args.out.mkdir(parents=True,exist_ok=True)
out.to_csv(args.out/"GLORYS_378cell_27annual_steps_3variable_summary.csv",index=False)
meta={
 "status":"PASS_SOURCE_ONLY_ANNUAL_STEP_DIAGNOSTIC",
 "input":"original source 588 site×28 years, 378 unique GLORYS cells",
 "prior_year_to_year_reference":"1994–2018 differences, 25 source intervals",
 "n_regions":18,"n_original_wet_cells":378,
 "salinity_2019_median_year_to_year_step":float(sal.loc[2019,"median_cell_step"]),
 "salinity_2020_median_year_to_year_step":float(sal.loc[2020,"median_cell_step"]),
 "2019_largest_negative_median_step_among_original_27_intervals":True,
 "n_source_yearly_steps":27,
 "source_discontinuity_cause_identified":False,
 "source_independent_in_situ_validation":False,
 "no_cell_independence_assumed":True
}
(args.out/"GLORYS_378cell_step_audit_summary.json").write_text(
    json.dumps(meta,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(meta,indent=2,ensure_ascii=False))
