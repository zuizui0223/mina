#!/usr/bin/env python3
"""Original-source CMIP6 exposure x observed nesting audit, not a biological forecast.

Input source zip files:
  GitHub Actions 42610664607 artifact 13669533413 (2456 nest observations, 595 sites)
  GitHub Actions 43845907301 artifact 14214704362 (27 Zarr source -> 595 site model deltas)
Never infer unobserved species abundance, climate-response coefficients or CCAMLR protection.
"""
import argparse,io,json,zipfile,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
MODS=("ACCESS-CM2","BCC-CSM2-MR","CESM2")
def get(z,name):
    with zipfile.ZipFile(z) as src:
        assert src.testzip() is None
        return pd.read_csv(io.BytesIO(src.read(name)))
def calc(counts,inventory,source):
    assert (len(counts),len(inventory),len(source))==(2456,595,21420)
    assert inventory.site_id.is_unique
    assert not counts.duplicated(["site_id","species","season"]).any()
    assert counts.observed_nest_count.ge(0).all()
    assert set(source.source_id)==set(MODS)
    assert source.site_id.nunique()==595 and source.complete_years.eq(20).all()
    assert set(source.variable_id)=={"tas","sos","siconc"}
    assert not source.duplicated(["site_id","source_id","variable_id","experiment_id","period"]).any()
    original=counts[counts.season.between(2011,2020)]
    species=original.groupby(["site_id","species"]).observed_nest_count.median().rename("n").reset_index()
    assert len(species)==331
    baseline=species.groupby("site_id").n.sum().rename("n").reset_index()
    years=original.groupby(["site_id","species"]).season.nunique().groupby(level=0).max().rename("max_years").reset_index()
    base=baseline.merge(years,on="site_id").merge(inventory[["site_id","source_region","polar_250km_fixed_grid_block"]],on="site_id")
    assert len(base)==271 and base.source_region.nunique()==16
    full_n=base.n.sum()
    coast=source[source.variable_id=="siconc"].drop_duplicates(["site_id","source_id"])
    marine=coast.groupby("site_id").distance_km.apply(lambda x:(x<=50).all()).rename("all3_marine_50").reset_index()
    base=base.merge(marine,on="site_id")
    assert int(base.all3_marine_50.sum())==158
    # Calculate one physical delta per site by equal weighting of three original CMIP6 models.
    sources=source.groupby(["site_id","variable_id","experiment_id","period"]).change.mean().rename("delta").reset_index()
    all_rows=[];model_rows=[];decomp=[];region_rows=[];threshold_rows=[]
    for (scenario,period,variable),whole in sources.groupby(["experiment_id","period","variable_id"]):
        actual=whole.merge(base,on="site_id",validate="one_to_one")
        for subset_name,t in [
          ("observed_271",actual),
          ("marine50_158",actual[actual.all3_marine_50]),
          ("at_least_one_species_two_year_92",actual[actual.max_years>=2])
        ]:
            all_rows.append(dict(experiment=scenario,period=period,variable=variable,cohort=subset_name,
               sites=len(t),regions=t.source_region.nunique(),source_count_weight_fraction=t.n.sum()/full_n,
               equal_sites_delta=float(t.delta.mean()),observed_nest_medians_weighted_delta=float(np.average(t.delta,weights=t.n)),
               all595_site_equal_delta=float(whole.delta.mean())))
        if variable!="siconc":continue
        for model,g in source[(source.variable_id=="siconc")&(source.experiment_id==scenario)&(source.period==period)].groupby("source_id"):
            t=g.merge(base[["site_id","n"]],on="site_id")
            model_rows.append(dict(experiment=scenario,period=period,model=model,sites=len(t),
                 equal_sites_delta=float(t.change.mean()),weighted_delta=float(np.average(t.change,weights=t.n))))
        eq=float(actual.delta.mean());weighted=float(np.average(actual.delta,weights=actual.n))
        counterfactual=0.0
        for name,g in actual.groupby("source_region"):
            p=g.n.sum()/actual.n.sum()
            counterfactual+=p*g.delta.mean()
            region_rows.append(dict(experiment=scenario,period=period,region=name,sites=len(g),
              count_proxy_share=p,region_equal_sic_delta=float(g.delta.mean()),
              region_count_weighted_sic_delta=float(np.average(g.delta,weights=g.n))))
        a=counterfactual-eq;b=weighted-counterfactual
        assert abs((a+b)-(weighted-eq))<1e-9
        decomp.append(dict(experiment=scenario,period=period,sites=271,
            equal_sic_delta=eq,weighted_sic_delta=weighted,
            between_region_accounting=a,within_region_accounting=b,
            weighted_minus_equal=weighted-eq))
        full=source[(source.variable_id=="siconc")&(source.experiment_id==scenario)&(source.period==period)]
        three=full.pivot(index="site_id",columns="source_id",values="change")
        for label,t in [("observed_271",actual),("marine50_158",actual[actual.all3_marine_50])]:
            test=three.loc[t.site_id]
            for cutoff in (5,10,20,30):
                for rule,eligible in [
                    ("three_model_mean",t.delta.le(-cutoff).to_numpy()),
                    ("all_three_models",test.le(-cutoff).all(axis=1).to_numpy())
                ]:
                    threshold_rows.append(dict(experiment=scenario,period=period,cohort=label,
                      threshold_decline_pp=cutoff,threshold_rule=rule,sites=len(t),
                      sites_below=int(eligible.sum()),
                      observed_nest_proxy_share_of_all_counted=float(t.n.to_numpy()[eligible].sum()/full_n)))
    assert len(all_rows)==36 and len(model_rows)==12 and len(decomp)==4 and len(threshold_rows)==64
    summary=pd.DataFrame(all_rows)
    ss=summary.query("experiment=='ssp585' and period=='2081-2100' and variable=='siconc' and cohort=='observed_271'").iloc[0]
    assert abs(ss.equal_sites_delta+28.634133941766486)<1e-9
    assert abs(ss.observed_nest_medians_weighted_delta+13.27624091727433)<1e-9
    return {"summary":pd.DataFrame(all_rows),"models":pd.DataFrame(model_rows),
        "region":pd.DataFrame(region_rows),"decomposition":pd.DataFrame(decomp),
        "threshold":pd.DataFrame(threshold_rows),"source_site_nest_proxy":base}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--count-zip",type=Path,required=True)
    p.add_argument("--physical-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    c=get(a.count_zip,"source_observed_2456.csv")
    i=get(a.count_zip,"panantarctic_595_site_inventory.csv")
    x=get(a.physical_zip,"source_root/outputs/cmip6_projection_v1/site_model_changes.csv")
    out=calc(c,i,x)
    for k,v in out.items():v.to_csv(a.out/(k+".csv"),index=False)
    receipt={"status":"PASS_PHYSICAL_SOURCE_ONLY",
      "n_known_colonies":595,"n_source_counted_2011_2020":271,"source_species_medians":331,
      "n_all_three_model_marine_grid_within_50km":158,
      "count_zip_sha256":hashlib.sha256(a.count_zip.read_bytes()).hexdigest(),
      "physical_zip_sha256":hashlib.sha256(a.physical_zip.read_bytes()).hexdigest(),
      "n_original_three_model_future_delta_rows":21420,
      "no_future_nest_growth_or_mpa_protection_inferred":True}
    (a.out/"source_gate.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
if __name__=="__main__":main()
