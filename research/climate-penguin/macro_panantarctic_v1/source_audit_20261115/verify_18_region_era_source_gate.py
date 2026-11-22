#!/usr/bin/env python3
"""Reproduce the source-era GLORYS salinity common-year fractions from 504 archived region years.

No penguin outcome data, independent in-situ observations, p-value, or causal
climate attribution is involved. Input: original 18-region original-source CSV
retained in this directory (archived from pinned GitHub Actions artifact).
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--region-csv", type=Path, default=HERE/"original_18_region_28year_PC1_PC2_source_panel.csv")
ap.add_argument("--out", type=Path, default=HERE/"era_source_gate_recomputed.json")
a=ap.parse_args()
df=pd.read_csv(a.region_csv)
assert len(df)==504 and df.source_region.nunique()==18
assert df.year.nunique()==28 and set(df.year)==set(range(1993,2021))
assert df.groupby("source_region").year.nunique().eq(28).all()
unique=df.drop_duplicates("source_region")
supported=sorted(unique.loc[(unique.n_colonies>=3)&(unique.n_wet_cells>=2)&(unique.n_blocks>=2),"source_region"])
assert len(supported)==13
groups={"all18":sorted(df.source_region.unique()),"supported13":supported}
periods={"1993-2020":list(range(1993,2021)),"1993-2018":list(range(1993,2019)),
         "2011-2020":list(range(2011,2021)),"2011-2018":list(range(2011,2019))}
rows=[]
for group,regs in groups.items():
 for period,yrs in periods.items():
  subset=df.loc[df.year.isin(yrs)]
  for weight in ("site_equal","wet_cell_equal"):
   result={"region_cohort":group,"n_regions":len(regs),"period":period,
           "year_count":len(yrs),"weight":weight}
   for pc in ("PC1","PC2"):
    mat=subset.pivot(index="year",columns="source_region",
                     values=f"{weight}_{pc}").loc[yrs,regs].to_numpy(dtype=float)
    assert np.isfinite(mat).all()
    z=(mat-mat.mean(axis=0))/mat.std(axis=0)
    shared=float(len(regs)*np.sum(z.mean(axis=1)**2)/np.sum(z**2))
    corr=np.corrcoef(z.T)
    pair=corr[np.triu_indices(len(regs),1)]
    check=1/len(regs)+(len(regs)-1)/len(regs)*float(pair.mean())
    assert abs(shared-check)<1e-12
    result[pc+"_common_year_fraction"]=shared
   rows.append(result)
out=pd.DataFrame(rows).sort_values(["region_cohort","period","weight"])
def val(cohort,period,weight,pc):
 return float(out[(out.region_cohort==cohort)&(out.period==period)&(out.weight==weight)].iloc[0][pc+"_common_year_fraction"])
assert abs(val("all18","1993-2020","site_equal","PC1")-.1970997514644)<1e-8
assert abs(val("all18","1993-2020","site_equal","PC2")-.5214067551570)<1e-8
assert abs(val("all18","1993-2018","site_equal","PC2")-.2928647)<1e-5
delta=df.groupby("source_region").apply(lambda q:pd.Series({
 "pre19":q.loc[q.year<=2018,"site_equal_salinity"].mean(),
 "2019":q.loc[q.year==2019,"site_equal_salinity"].iloc[0],
 "2020":q.loc[q.year==2020,"site_equal_salinity"].iloc[0]}),include_groups=False)
assert ((delta["2019"]-delta.pre19)<0).sum()==18
assert ((delta["2020"]-delta.pre19)<0).sum()==18
result={"status":"POST_RESULT_GLORYS_2019_2020_SOURCE_HOLD",
 "verified_source_region_years":len(df),"verified_regions":18,"n_supported_geographic_regions":13,
 "source_all18_site_equal_full":{"PC1":val("all18","1993-2020","site_equal","PC1"),
                                 "PC2":val("all18","1993-2020","site_equal","PC2")},
 "source_all18_site_equal_pre2019":{"PC1":val("all18","1993-2018","site_equal","PC1"),
                                    "PC2":val("all18","1993-2018","site_equal","PC2")},
 "n_regions_below_1993_2018_salinity_baseline":{"2019":18,"2020":18},
 "forcing_transition_documented_2019":True,
 "source_break_cause_established":False,"independent_in_situ_confirmation":False,
 "all_32_region_year_weight_period_summaries":rows}
a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:v for k,v in result.items() if k!="all_32_region_year_weight_period_summaries"},indent=2))
