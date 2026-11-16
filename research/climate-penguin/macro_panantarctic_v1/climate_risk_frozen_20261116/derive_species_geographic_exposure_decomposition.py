#!/usr/bin/env python3
"""Physical-only CMIP6 sea-ice exposure decomposition by penguin species.

The species difference is decomposed into (i) different regional source nest
shares and (ii) different within-region colony shares, referenced to equal-site
regional physical exposure of the EXACT same counted-site cohort.
No species climate response, future nests, colonization, conservation risk
probability, protection or ecological selection is estimated.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd

SP=("ADPE","CHPE","GEPE")
MODS=("ACCESS-CM2","BCC-CSM2-MR","CESM2")
MAIN=("ssp585","2081-2100")

def original_cmip6(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return pd.read_csv(io.BytesIO(z.read("source_root/outputs/cmip6_projection_v1/site_model_changes.csv")))

def mean(x,w):
    return float(np.average(x.astype(float),weights=w.astype(float)))

def audit_counts(counts,inventory):
    assert len(counts)==2456 and inventory.site_id.nunique()==595
    assert not counts.duplicated(["site_id","species","season"]).any()
    assert counts.observed_nest_count.notna().all()
    assert counts.observed_nest_count.ge(0).all()
    c=counts.loc[counts.season.between(2011,2020)]
    s=c.groupby(["site_id","species"],as_index=False).observed_nest_count.median()
    s=s.rename(columns={"observed_nest_count":"source_observed_nest_median"})
    assert len(s)==331 and set(s.species)==set(SP)
    b=s.groupby("site_id",as_index=False).source_observed_nest_median.sum()
    assert len(b)==271 and abs(b.source_observed_nest_median.sum()-2848329.5)<1e-8
    obs=inventory[["site_id","source_region"]].merge(b,on="site_id",how="inner",validate="one_to_one")
    assert obs.source_region.nunique()==16
    assert s.groupby("species").size().to_dict()=={"ADPE":108,"CHPE":138,"GEPE":85}
    return s,obs

def calc_species(physical,counts,obs):
    # same 3 published model IDs, complete years, source identifiers.
    assert len(physical)==21420 and set(physical.source_id)==set(MODS)
    assert physical.site_id.nunique()==595
    assert physical.complete_years.eq(20).all()
    a=physical[physical.variable_id.eq("siconc")].copy()
    assert len(a)==7140
    assert not a.duplicated(["site_id","source_id","experiment_id","period"]).any()
    coast=a.drop_duplicates(["site_id","source_id"])
    assert len(coast)==595*3
    near=coast.groupby("site_id").distance_km.max().le(50).rename("all3_within50km")
    obs=obs.merge(near,on="site_id",validate="one_to_one")
    assert obs.all3_within50km.sum()==158
    b=counts.merge(obs[["site_id","source_region","all3_within50km"]],on="site_id",validate="many_to_one")
    result=[];region_rows=[]
    for (ex,per),zz in a.groupby(["experiment_id","period"]):
        # one ensemble physical delta per genuine site, not species-specific climate.
        d=zz.groupby("site_id",as_index=False).change.mean().rename(columns={"change":"delta_sic_pp"})
        assert len(d)==595
        base=obs.merge(d,on="site_id",validate="one_to_one")
        species=b.merge(d,on="site_id",validate="many_to_one")
        for support in ("counted271","three_model_marine50_158"):
            bs=base if support=="counted271" else base[base.all3_within50km]
            ss=species if support=="counted271" else species[species.all3_within50km]
            assert bs.site_id.nunique()==(271 if support=="counted271" else 158)
            # Equal-colony regional reference, irrespective of which counted
            # focal species makes a given site available.
            reference=bs.groupby("source_region").delta_sic_pp.mean()
            eq=bs.delta_sic_pp.mean()
            species_models={}
            for sp in SP:
                g=ss[ss.species.eq(sp)].copy()
                assert len(g)>0
                wsum=g.source_observed_nest_median.sum()
                g["regional_equal_site_delta"]=g.source_region.map(reference)
                g["within_region_difference"]=g.delta_sic_pp-g.regional_equal_site_delta
                exposed=mean(g.delta_sic_pp,g.source_observed_nest_median)
                between=mean(g.regional_equal_site_delta,g.source_observed_nest_median)
                within=mean(g.within_region_difference,g.source_observed_nest_median)
                assert abs(exposed-between-within)<1e-10
                species_models[sp]={"observed_nest_exposure":exposed,
                    "regional_composition_component":between,
                    "within_region_colony_component":within,
                    "n_source_species_sites":len(g),
                    "species_source_nest_median_sum":float(wsum)}
                result.append({"experiment":ex,"period":per,"cohort":support,
                    "species":sp,"n_species_sites":len(g),
                    "n_source_regions":g.source_region.nunique(),
                    "species_observed_median_nests":float(wsum),
                    "site_equal_original_271_delta":float(eq),
                    "species_weighted_sic_delta_pp":exposed,
                    "counterfactual_region_mean_pp":between,
                    "within_region_delta_from_region_mean_pp":within})
                if (ex,per)==MAIN:
                    for region,gr in g.groupby("source_region"):
                        region_rows.append({"cohort":support,"species":sp,"region":region,
                            "species_source_site_count":len(gr),
                            "species_nest_proxy_share":float(gr.source_observed_nest_median.sum()/wsum),
                            "region_site_equal_physical_sic_pp":float(reference[region]),
                            "within_region_species_weighted_sic_pp":mean(gr.delta_sic_pp,gr.source_observed_nest_median)})
            for other in ("CHPE","GEPE"):
                ag=species_models["ADPE"]
                bg=species_models[other]
                obs_diff=bg["observed_nest_exposure"]-ag["observed_nest_exposure"]
                region_diff=bg["regional_composition_component"]-ag["regional_composition_component"]
                within_diff=bg["within_region_colony_component"]-ag["within_region_colony_component"]
                assert abs(obs_diff-region_diff-within_diff)<1e-10
                result.append({"experiment":ex,"period":per,"cohort":support,
                    "species":other+"_minus_ADPE",
                    "n_species_sites":None,"n_source_regions":None,
                    "species_observed_median_nests":None,
                    "site_equal_original_271_delta":float(eq),
                    "species_weighted_sic_delta_pp":obs_diff,
                    "counterfactual_region_mean_pp":region_diff,
                    "within_region_delta_from_region_mean_pp":within_diff})
    table=pd.DataFrame(result)
    assert len(table)==4*2*5
    p=table[(table.experiment==MAIN[0])&(table.period==MAIN[1])&(table.cohort=="counted271")]
    known={"ADPE":-11.256,"CHPE":-17.534,"GEPE":-34.839}
    for sp,v in known.items():
        got=float(p[p.species.eq(sp)].species_weighted_sic_delta_pp.iloc[0])
        assert abs(got-v)<0.01,(sp,got)
    return table,pd.DataFrame(region_rows)

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--counts",type=Path,required=True)
    pa.add_argument("--inventory",type=Path,required=True)
    pa.add_argument("--cmip6-zip",type=Path,required=True)
    pa.add_argument("--out",type=Path,required=True)
    ar=pa.parse_args();ar.out.mkdir(parents=True,exist_ok=True)
    c=pd.read_csv(ar.counts);i=pd.read_csv(ar.inventory)
    raw=original_cmip6(ar.cmip6_zip)
    s,obs=audit_counts(c,i)
    table,regional=calc_species(raw,s,obs)
    table.to_csv(ar.out/"original_species_climate_geography_decomposition.csv",index=False)
    regional.to_csv(ar.out/"original_species_region_exposure_shares.csv",index=False)
    selected=table[(table.experiment==MAIN[0])&(table.period==MAIN[1])]
    rec={"status":"PASS_ORIGINAL_COUNTED_271_SPECIES_GEOGRAPHIC_PHYSICAL_DECOMPOSITION_ONLY",
      "original_595_sites":595,"original_2456_genuine_counts":2456,
      "counted_2011_2020_sites":271,"counted_species_site_medians":331,
      "all3_marine50_counted_sites":158,"original_cmip6_source_rows":21420,
      "model_count":3,"scenario_count":4,"source_count_sha256":hashlib.sha256(ar.counts.read_bytes()).hexdigest(),
      "source_inventory_sha256":hashlib.sha256(ar.inventory.read_bytes()).hexdigest(),
      "source_cmip6_zip_sha256":hashlib.sha256(ar.cmip6_zip.read_bytes()).hexdigest(),
      "scenario":"SSP5-8.5 2081–2100 relative to model historical 1995–2014, Aug–Nov",
      "original_source_nesting_proxy_non_synchronous":True,
      "reference_regional_mean_equal_counted_sites":True,
      "pure_accounting_not_an_independent_causes_partition":True,
      "no_future_population_prediction":True,
      "selected_case":[{k:(None if pd.isna(v) else v) for k,v in row.items()} for row in selected.to_dict("records")]
    }
    (ar.out/"species_geographic_physical_source_receipt.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    print("SOURCE_VERIFIED_SPECIES_EXPOSURE="+json.dumps({"status":rec["status"],"selected_case":rec["selected_case"]},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
