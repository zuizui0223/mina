#!/usr/bin/env python3
"""Explicitly post-source, exploratory ASI peninsula land-polygon contrast.

One fixed model for an observational association, NOT predation effect,
true island identity, or postglacial colonization. ASI 0=not detected.
Breeding-confirmed y=1 if any original visit records ASI state 2 in that
site×species×season; exact binomial source record, not true occupancy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

SOURCE_ASI_RUN=44511340025
SOURCE_ASI_ARTIFACT=14524376093
SOURCE_SCAR_RUN=44512297362
SOURCE_SCAR_ARTIFACT=14524101863
TARGET_SPECIES=("ADPE","CHPE","GEPE")
CONTINENT="CONTINENT_LARGEST_LAND_POLYGON_PROXY"
SEPARATE="NONCONTINENTAL_LAND_POLYGON_PROXY"
FORMULA="breeding_confirmed ~ separate_source_polygon + C(species) + C(spatial_block_100km) + log2_visits + year_decades"

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def build_analysis_frame(panel:pd.DataFrame,geo:pd.DataFrame):
    expected={"Code","season_start","visit_count",*TARGET_SPECIES}
    if not expected.issubset(panel) or not {
       "Code","geography_group","spatial_block_100km"}.issubset(geo):
        raise ValueError("Original source outcome/land fields missing")
    if panel.Code.nunique()!=196 or len(panel)!=827 or len(geo)!=196:
        raise ValueError("ASI original site/year dataset drift")
    if geo.Code.nunique()!=196:
        raise ValueError("ASI geo source site ID is not unique")
    c=geo[geo.geography_group.isin({CONTINENT,SEPARATE})].copy()
    groups=c.groupby(["spatial_block_100km","geography_group"])["Code"].nunique().unstack(fill_value=0)
    for x in (CONTINENT,SEPARATE):
        if x not in groups: raise ValueError("Both geography source strata not available")
    shared=list(groups.index[(groups[CONTINENT]>0)&(groups[SEPARATE]>0)])
    if len(shared)!=6:
        raise ValueError(f"original matched spatial block drift {len(shared)} != 6")
    c=c[c.spatial_block_100km.isin(shared)].copy()
    if c.Code.nunique()!=82:
        raise ValueError(f"matched source sites drift {c.Code.nunique()} != 82")
    x=panel.merge(c[["Code","geography_group","spatial_block_100km"]],
                  on="Code",how="inner",validate="many_to_one")
    y=x.melt(id_vars=["Code","season_start","visit_count","geography_group","spatial_block_100km"],
             value_vars=list(TARGET_SPECIES),var_name="species",value_name="state")
    y=y[y.state!="INCOMPLETE_OR_MISSING"].copy()
    allowed={"ALL_VISITS_NONDETECTION","PRESENCE_ONLY_OBSERVED","BREEDING_OBSERVED"}
    if not set(y.state).issubset(allowed):
        raise ValueError("ASI detection states changed unexpectedly")
    y["breeding_confirmed"]=(y.state=="BREEDING_OBSERVED").astype(int)
    y["separate_source_polygon"]=(y.geography_group==SEPARATE).astype(int)
    y["log2_visits"]=np.log2(y.visit_count.astype(int))
    y["year_decades"]=(y.season_start-2006)/10.0
    y=y.sort_values(["species","Code","season_start"]).reset_index(drop=True)
    if len(y)!=1127:
        raise ValueError(f"matched source site×species×season support drift {len(y)} != 1127")
    return y,shared

def fit_one(df:pd.DataFrame):
    model=smf.glm(FORMULA,data=df,family=sm.families.Binomial())
    ordinary=model.fit(maxiter=100)
    robust=model.fit(maxiter=100,cov_type="cluster",
                     cov_kwds={"groups":df["Code"]})
    return ordinary,robust

def evaluate(panel_file:Path,geo_file:Path):
    panel=pd.read_csv(panel_file)
    geo=pd.read_csv(geo_file)
    dat,shared=build_analysis_frame(panel,geo)
    unclustered,fit=fit_one(dat)
    name="separate_source_polygon"
    if name not in fit.params or not np.isfinite(fit.params[name]):
        raise ValueError("fixed focal source contrast missing or non-finite")
    estimate=float(fit.params[name])
    confidence=[float(x) for x in fit.conf_int().loc[name]]
    loo=[]
    for block in shared:
        sub=dat[dat.spatial_block_100km!=block]
        try:
            f,_=fit_one(sub)
            loo.append({"omitted_spatial_block":block,
                        "source_subsample_site_count":int(sub.Code.nunique()),
                        "beta_source_polygon":float(f.params[name])})
        except Exception as exc:
            loo.append({"omitted_spatial_block":block,"status":"HOLD_FIT",
                        "error":f"{type(exc).__name__}: {str(exc)}"[:150]})
    count_table=[]
    for (species,group),part in dat.groupby(["species","geography_group"]):
        count_table.append({
           "species":species,"geography":group,
           "observed_site_species_seasons":int(len(part)),
           "confirmed_breeding_site_seasons":int(part.breeding_confirmed.sum()),
           "distinct_sites":int(part.Code.nunique()),
        })
    return {
        "status":"EXPLORATORY_POST_SOURCE_GEO_ASSOCIATION_NOT_CONFIRMATORY",
        "original_source_artifacts":{
           "asi_original_run":SOURCE_ASI_RUN,"asi_original_artifact":SOURCE_ASI_ARTIFACT,
           "scar_original_run":SOURCE_SCAR_RUN,"scar_original_artifact":SOURCE_SCAR_ARTIFACT,
           "asi_site_year_sha256":sha256(panel_file),
           "scar_source_geo_sha256":sha256(geo_file),
        },
        "estimand":"conditional observational log odds difference in any confirmed breeding across site×species×season, separate SCAR source land polygon proxy vs largest continental polygon, within matched 100km blocks",
        "model_formula":FORMULA,
        "source_selection":"exact polygon assignment; six matched 100km blocks only; all ADPE/CHPE/GEPE scored site×species×season rows",
        "source_site_codes":int(dat.Code.nunique()),
        "source_site_species_seasons":int(len(dat)),
        "source_spatial_blocks":len(shared),
        "source_spatial_block_ids":shared,
        "source_counts":count_table,
        "estimate_beta":estimate,
        "estimate_odds_ratio":float(np.exp(estimate)),
        "site_cluster_robust_interval_beta":confidence,
        "site_cluster_robust_interval_OR":[float(np.exp(x)) for x in confidence],
        "site_cluster_robust_p_descriptive":float(fit.pvalues[name]),
        "naive_independent_row_p_not_for_inference":float(unclustered.pvalues[name]),
        "leave_one_100km_block_out_descriptive":loo,
        "post_result_timing":"Entire model explicitly exploratory, selected after original species-level ASI states and group support were inspected; not preregistered, not a held-out confirmation.",
        "inference_ceilings":[
           "Original SCAR map features are not validated physical islands; category is source geometric proxy only.",
           "ASI visit-level breeding confirmation has false negatives; this GLM adjusts visits via log2(n) but does NOT explicitly recover detection probability or true latent breeding state.",
           "Survey effort, colony selection, site history, and marine resources differ between groups; no causal predator or refuge effect identified.",
           "Six 100km blocks is a small number of independent regional units; site-cluster confidence intervals can understate geographic uncertainty.",
           "Cannot call a non-significant contrast equivalence or evidence island effect vanishes without predators.",
           "Original literature already models sea ice and wind-wave fetch for these ASI species; no novelty claim for marine-climate associations.",
           "No new-rock occurrence, colonization, dispersal, or future nest-count prediction obtained.",
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asi-panel-csv",required=True,type=Path)
    p.add_argument("--asi-geo-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    r=evaluate(a.asi_panel_csv,a.asi_geo_csv)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({k:r.get(k) for k in ("status","source_site_codes","source_spatial_blocks","source_site_species_seasons","estimate_beta","estimate_odds_ratio","site_cluster_robust_interval_OR")},sort_keys=True))

if __name__=="__main__":
    main()
