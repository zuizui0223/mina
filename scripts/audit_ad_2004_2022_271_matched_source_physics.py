#!/usr/bin/env python3
"""Source-only physical joint audit on observed Adélie census years. No count response is fit."""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from scipy.linalg import qr
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import connected_components

R=6371.0088
MAPP_SHA="d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89"
def require(condition,message):
    if not bool(condition):raise ValueError("SOURCE FAIL CLOSED "+message)
def blocks(frame,km):
    lon=np.deg2rad(frame.lon.to_numpy(float));lat=np.deg2rad(frame.lat.to_numpy(float))
    pos=np.stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)],axis=-1)
    pp=cKDTree(pos).query_pairs(2*np.sin(km/(2*R)),output_type="ndarray")
    graph=csr_matrix((len(frame),len(frame))) if not len(pp) else coo_matrix((
        np.ones(2*len(pp)),(np.r_[pp[:,0],pp[:,1]],np.r_[pp[:,1],pp[:,0]])),
        shape=(len(frame),len(frame))).tocsr()
    return connected_components(graph,directed=False)
def residual_physical(frame):
    x=frame.sort_values(["site_id","season"]).reset_index(drop=True)
    a=pd.get_dummies(x.site_id,drop_first=True,dtype=float).to_numpy()
    b=pd.get_dummies(x.season.astype(str),drop_first=True,dtype=float).to_numpy()
    d=np.column_stack([np.ones(len(x)),a,b])
    q,_,_=qr(d,mode="economic",pivoting=True);q=q[:,:np.linalg.matrix_rank(d,tol=1e-9)]
    data=x[["coastal_frac","all_open_frac","annual_sic_mean"]].to_numpy(float)
    centered=data-q@(q.T@data)
    coast,allopen,sic=centered.T
    require(np.std(coast)>1e-10 and np.std(sic)>1e-10,"zero centered variance")
    bcoef=(coast@sic)/(sic@sic)
    return dict(rows=int(len(x)),sites=int(x.site_id.nunique()),years=int(x.season.nunique()),
      centered_correlation_coastal_vs_NSIDC_SIC=float(np.corrcoef(coast,sic)[0,1]),
      centered_correlation_allopen_vs_1minusSIC=float(np.corrcoef(allopen,-sic)[0,1]),
      coastal_sd_site_year_FE_pp=float(np.std(coast,ddof=1)*100),
      coastal_sd_site_year_FE_plus_NSIDC_pp=float(np.std(coast-bcoef*sic,ddof=1)*100),
      coast_residual_variance_retained_after_SIC=float(np.var(coast-bcoef*sic,ddof=1)/np.var(coast,ddof=1)),
      original_means_pp=dict(coastal=float(x.coastal_frac.mean()*100),
                             allopen=float(x.all_open_frac.mean()*100),nsidc_open=float((1-x.annual_sic_mean).mean()*100)))
def main(a):
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    p=pd.read_csv(a.deepaa);q=pd.read_csv(a.sic)
    sites=pd.read_csv(a.site_support)
    census=pd.read_csv(a.census)
    b=Path(a.original_mapppd).read_bytes()
    require(hashlib.sha256(b).hexdigest()==MAPP_SHA,"original MAPPPD v5 CSV SHA drift")
    original=pd.read_csv(a.original_mapppd,low_memory=False)
    require((len(p),len(q),len(sites),len(census))==(860,774,43,320),"original inputs source count drift")
    require(len(original)==5487,"MAPPPD 5487 original counts drift")
    for tag,x in [("deepaa",p),("NSIDC",q),("census",census)]:
        require(not x.duplicated(["site_id","season"]).any(),tag+" duplicate site-season")
    m=p.merge(q,on=["site_id","season"],validate="one_to_one",how="left")
    complete=m.loc[m.has_complete_source_winter & m.is_complete.fillna(False)].copy()
    require(len(complete)==731 and complete.site_id.nunique()==43,"joint 43*17 original physical support")
    require(complete.season.nunique()==17,"17 winters drift")
    primary=sites[sites.primary.astype(bool)].sort_values("site_id").reset_index(drop=True)
    require(len(primary)==32,"32 primary sites lost")
    n100,bl100=blocks(primary,100);n200,bl200=blocks(primary,200)
    require((n100,n200)==(7,6),"primary 100km/200km block count changed")
    primary["primary_200km_block"]=bl200
    source=original.loc[original.site_id.isin(primary.site_id)&original.common_name.eq("adelie penguin")&
        original.count_type.eq("nests")&original.season_starting.between(2003,2022)&
        ~original.season_starting.isin([2011,2012])&original.penguin_count.notna()].copy()
    quality=source.groupby("site_id").agg(vantage_n=("vantage","nunique"),
        highest_accuracy_code=("accuracy","max")).reset_index()
    primary=primary.merge(quality,on="site_id",validate="one_to_one")
    primary["consistent_vantage_and_accuracy_le_2"]=primary.vantage_n.eq(1)&primary.highest_accuracy_code.le(2)
    require(int(primary.consistent_vantage_and_accuracy_le_2.sum())==14,"14 quality sites not reproduced")
    counts=census[census.primary.astype(bool)].copy()
    require(len(counts)==284,"primary 284 observed census site-years changed")
    match=counts[["site_id","season"]].merge(complete,on=["site_id","season"],validate="one_to_one")
    require((len(match),match.site_id.nunique())==(271,32),"original 271 matched nest survey site-years changed")
    match=match.merge(primary[["site_id","primary_200km_block","consistent_vantage_and_accuracy_le_2"]],
       on="site_id",validate="many_to_one")
    high=match.loc[match.consistent_vantage_and_accuracy_le_2]
    require((len(high),high.site_id.nunique(),high.primary_200km_block.nunique())==(158,14,4),
       "high-quality physical support changed")
    result={
      "status":"PASS_SOURCE_ONLY_DEEPAA_NSIDC_OBSERVED_NEST_YEARS_PHYSICAL_NOT_ECOLOGICAL_TEST",
      "source_branches":"official DEEP-AA native 6.25km and NOAA/NSIDC original 25km monthly SIC",
      "source_june_oct_winter_years":sorted(complete.season.unique().astype(int).tolist()),
      "all_43_sites_matched_physics":len(complete),"primary_32_sites_matched_physics":int(complete.primary.sum()),
      "primary_census_observed_siteyears":len(counts),
      "primary_census_siteyears_matched_complete_physics":len(match),
      "primary_geographic_independence":{"n100km_groups":n100,"n200km_groups":n200},
      "highquality_sites":14,"highquality_200km_groups":4,
      "balanced_full_physical_43_site_correlations":residual_physical(complete),
      "actual_census_year_source_only":residual_physical(match),
      "consistent_vantage_and_accuracy_1to2_source_only":residual_physical(high),
      "population_response_coefficients":None,
      "no_ecological_regression_per_original_gate":True,
      "reason_for_no_macro_fit":"Only 6 200km-connected groups; high-quality 14 sites occupy 4 groups, below independent-region gate 8",
      "cautions":["All residual correlations are between physical predictors, never against nest counts",
        "93%+ source physical variation remains after continuous SIC but no independent macro demographic inference",
        "DEEP-AA 2003 October is incomplete; 2011-2012 original product has hiatus",
        "Do not translate physical source differences into population dynamics or causal effects"]}
    primary.to_csv(out/"primary32_original_survey_quality_and_independent_blocks.csv",index=False)
    match.sort_values(["site_id","season"]).to_csv(out/"observed_271_source_only_physics_and_census_roster.csv",index=False)
    (out/"AUDITED_CENSUS_YEAR_DEEPAA_NSIDC_PHYSICAL_GATE.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    arg=argparse.ArgumentParser()
    for k in ["deepaa","sic","site_support","census","original_mapppd","out"]:
        arg.add_argument("--"+k.replace("_","-"),dest=k,required=True)
    main(arg.parse_args())
