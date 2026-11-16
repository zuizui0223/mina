#!/usr/bin/env python3
"""Source-counted Antarctic penguin physical SIC exposure on matched geography.

Pairwise comparisons at four explicit observation supports:
1. Original species-specific site rosters (different sites/regions).
2. Identical original source regions with equal region weights (different sites
   within those reporting regions remain possible).
3. Identical original recorded site IDs, species medians from 2011-2020
   (possibly different original census years).
4. Identical original site AND season AND known method in 2011-2020,
   using only paired survey years to define each species' site median.
Each support is evaluated with/without the original all-3-model marine <=50km
wet-grid criterion. Never interpret weighted contrasts as physiological
species response, same-day nests, foraging exposure or future demographics.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from derive_species_geographic_exposure_decomposition import (
    MODS,MAIN,SP,original_cmip6,audit_counts,mean
)

PAIRS=(("ADPE","CHPE"),("ADPE","GEPE"),("CHPE","GEPE"))
SUPPORT=("original_species_rosters","shared_regions_equal_region_weights",
         "same_site_original_medians","same_site_sameyear_samemethod_medians")
COLS=["experiment_id","period","source_id","site_id","sic_delta_pp"]

def read_fixed(count_file,site_file,climate_zip):
    counts=pd.read_csv(count_file)
    inventory=pd.read_csv(site_file)
    physical=original_cmip6(climate_zip)
    species,observed=audit_counts(counts,inventory)
    assert set(species.species)==set(SP) and species[["site_id","species"]].duplicated().sum()==0
    assert physical.site_id.nunique()==595 and len(physical)==21420
    assert physical.complete_years.eq(20).all() and set(physical.source_id)==set(MODS)
    assert not physical.duplicated(
        ["site_id","source_id","variable_id","experiment_id","period"]).any()
    ocean=physical[physical.variable_id.isin(("siconc","sos"))][
        ["site_id","source_id","variable_id","distance_km"]
    ].drop_duplicates(["site_id","source_id","variable_id"])
    assert len(ocean)==595*3*2
    marine=ocean.groupby("site_id").distance_km.max().le(50).rename("all_model_marine50")
    observed=observed.merge(marine,on="site_id",validate="one_to_one")
    assert (len(observed),observed.all_model_marine50.sum())==(271,158)
    species=species.merge(
        observed[["site_id","source_region","all_model_marine50"]],
        on="site_id",validate="many_to_one"
    )
    assert len(species)==331
    ice=physical[physical.variable_id.eq("siconc")].copy()
    assert len(ice)==7140
    ensemble=ice.groupby(["site_id","experiment_id","period"],as_index=False).change.mean()
    ensemble["source_id"]="three_model_equal_mean"
    ice=pd.concat([ice[["site_id","experiment_id","period","source_id","change"]],
                  ensemble],ignore_index=True).rename(columns={"change":"sic_delta_pp"})
    ice=ice[COLS]
    assert len(ice)==595*4*4
    assert ice[COLS[:-1]].duplicated().sum()==0
    return counts,species,observed,ice

def direct_cocensuses(counts,species):
    c=counts[counts.season.between(2011,2020)].copy()
    assert c[["site_id","species","season"]].duplicated().sum()==0
    assert c.original_survey_method.notna().all()
    annual={}
    for a,b in PAIRS:
        ga=c[c.species.eq(a)][["site_id","season","observed_nest_count","original_survey_method"]]
        gb=c[c.species.eq(b)][["site_id","season","observed_nest_count","original_survey_method"]]
        pair=ga.merge(gb,on=["site_id","season"],suffixes=("_a","_b"),validate="one_to_one")
        strict=pair[pair.original_survey_method_a.eq(pair.original_survey_method_b)].copy()
        if len(strict):
            s=strict.groupby("site_id",as_index=False).agg(
                weight_a=("observed_nest_count_a","median"),
                weight_b=("observed_nest_count_b","median"),
                n_same_year_method=("season","nunique"),
                earliest_paired_year=("season","min"),latest_paired_year=("season","max"))
            assert not s.duplicated("site_id").any()
            sa=set(species[species.species.eq(a)].site_id)
            sb=set(species[species.species.eq(b)].site_id)
            assert set(s.site_id).issubset(sa&sb)
        else:
            s=pd.DataFrame(columns=["site_id","weight_a","weight_b","n_same_year_method",
                                    "earliest_paired_year","latest_paired_year"])
        annual[(a,b)]={"sites":s,"siteyears":len(strict),
                       "excluded_different_source_method_siteyears":len(pair)-len(strict),
                       "all_sameyear_siteyears_irrespective_of_method":len(pair)}
    return annual

def pair_sites(species,a,b):
    aa=species[species.species.eq(a)][["site_id","source_observed_nest_median"]].rename(
        columns={"source_observed_nest_median":"weight_a"})
    bb=species[species.species.eq(b)][["site_id","source_observed_nest_median"]].rename(
        columns={"source_observed_nest_median":"weight_b"})
    return aa.merge(bb,on="site_id",validate="one_to_one")

def wmean(frame,key="source_observed_nest_median"):
    if frame.empty or frame[key].sum()<=0:return None
    return mean(frame.sic_delta_pp,frame[key])

def pair_result(species,grid,obs,coannual,sp1,sp2,subset,screen,scenario,period,model):
    sd=species[species.species.isin([sp1,sp2])].copy()
    baseline_weights={s:float(sd[sd.species.eq(s)].source_observed_nest_median.sum())
                      for s in (sp1,sp2)}
    assert all(x>0 for x in baseline_weights.values())
    view=sd if not screen else sd[sd.all_model_marine50]
    current=view.merge(grid,on="site_id",validate="many_to_one")
    w1=wmean(current[current.species.eq(sp1)])
    w2=wmean(current[current.species.eq(sp2)])
    support_sites=0;support_regions=0;co_years=None
    common_sites_fraction={sp1:None,sp2:None}
    common_geography_site_equal=None
    if subset=="original_species_rosters":
        support_sites=current.site_id.nunique()
        support_regions=current.source_region.nunique()
        common_sites_fraction={
            s:float(current[current.species.eq(s)].source_observed_nest_median.sum()/baseline_weights[s])
            for s in (sp1,sp2)}
    elif subset=="shared_regions_equal_region_weights":
        # Within each original source region, use each species' recorded
        # nest medians to average source sites; then weight each common
        # positive-weight region equally for BOTH species.
        reg_species={}
        for s in (sp1,sp2):
            groups={}
            for region,g in current[current.species.eq(s)].groupby("source_region"):
                if g.source_observed_nest_median.sum()>0:
                    groups[region]=wmean(g)
            reg_species[s]=groups
        common=set(reg_species[sp1])&set(reg_species[sp2])
        support_regions=len(common)
        x=current[current.source_region.isin(common)]
        support_sites=x.site_id.nunique()
        w1=float(np.mean([reg_species[sp1][r] for r in sorted(common)])) if common else None
        w2=float(np.mean([reg_species[sp2][r] for r in sorted(common)])) if common else None
        common_sites_fraction={
            s:float(x[x.species.eq(s)].source_observed_nest_median.sum()/baseline_weights[s])
            for s in (sp1,sp2)}
    elif subset in ("same_site_original_medians","same_site_sameyear_samemethod_medians"):
        if subset=="same_site_original_medians":
            shared=pair_sites(species,sp1,sp2)
        else:
            shared=coannual[(sp1,sp2)]["sites"].copy()
            co_years=coannual[(sp1,sp2)]["siteyears"]
        shared=shared.merge(obs[["site_id","source_region","all_model_marine50"]],
                            on="site_id",validate="one_to_one")
        if screen:shared=shared[shared.all_model_marine50]
        x=shared.merge(grid,on="site_id",validate="one_to_one")
        support_sites=len(x)
        support_regions=x.source_region.nunique()
        if support_sites:
            common_geography_site_equal=float(x.sic_delta_pp.mean())
        # Even identical sites only share a *physical* climate delta; the
        # two count-weighted site distributions may differ.
        w1=wmean(x,"weight_a")
        w2=wmean(x,"weight_b")
        # Selection coverage must use the SAME original species baseline
        # median weights; matched-year medians are a different estimator and
        # must never appear as a fraction of the full baseline denominator.
        selected_sites=set(x.site_id)
        common_sites_fraction={
            ss:float(species[(species.species.eq(ss)) &
                 (species.site_id.isin(selected_sites))].source_observed_nest_median.sum()
                 /baseline_weights[ss]) for ss in (sp1,sp2)}
    else:raise ValueError("Unexpected support definition")

    estimable=w1 is not None and w2 is not None
    return {
        "scenario":scenario,"period":period,"model":model,
        "species_a":sp1,"species_b":sp2,
        "support":subset,"marine_grid50_screen":screen,
        "n_support_sites":int(support_sites),"n_source_reporting_regions":int(support_regions),
        "n_true_sameyear_samemethod_siteyears":co_years,
        "support_species_a_nest_weight_fraction":common_sites_fraction[sp1],
        "support_species_b_nest_weight_fraction":common_sites_fraction[sp2],
        "species_a_weighted_sic_delta_pp":w1,
        "species_b_weighted_sic_delta_pp":w2,
        "species_b_minus_a_sic_delta_pp":w2-w1 if estimable else None,
        "same_site_equal_weight_sic_delta_pp":common_geography_site_equal,
        "both_species_exposures_estimable":estimable,
        "same_site_physical_sic_identical_by_construction":subset.startswith("same_site"),
        "source_period_nests_non_synchronous_except_restricted_pair_siteyear":True,
        "physical_geography_not_future_species_vulnerability":True
    }

def run(counts,species,obs,ice):
    coannual=direct_cocensuses(counts,species)
    all_results=[]
    for (scenario,period,model),g in ice.groupby(["experiment_id","period","source_id"],sort=True):
        assert len(g)==595 and g.site_id.is_unique
        val=g[["site_id","sic_delta_pp"]]
        for pair in PAIRS:
            for screening in (False,True):
                for support in SUPPORT:
                    all_results.append(pair_result(species,val,obs,coannual,*pair,
                        support,screening,scenario,period,model))
    table=pd.DataFrame(all_results)
    assert len(table)==4*4*3*2*4
    assert table[["scenario","period","model","species_a","species_b",
                  "marine_grid50_screen","support"]].duplicated().sum()==0
    for (scenario,period,model,a,b,screen),g in table.groupby(
        ["scenario","period","model","species_a","species_b","marine_grid50_screen"]):
        f=g[g.support.eq("same_site_original_medians")].iloc[0]
        if f.both_species_exposures_estimable:
            # Shared physical SIC, hence same equal-site exposure for each
            # species. Weighted difference merely reweights this same list.
            assert pd.notna(f.same_site_equal_weight_sic_delta_pp)
        st=g[g.support.eq("same_site_sameyear_samemethod_medians")].iloc[0]
        assert st.n_support_sites<=f.n_support_sites
    receipt={"status":"PASS_SOURCE_SAME_SITE_SPECIES_PHYSICAL_EXPOSURE_SUPPORT",
      "n_original_count_sites":271,
      "n_original_species_site_medians":331,
      "n_original_physical_delta_rows":21420,
      "n_model_scenarios":4*4,
      "n_support_rows":len(table),
      "no_physiological_or_demographic_inference":True,
      "true_method_matched_sameyear_pair_support":{
         a+"__"+b:{"n_site_years":x["siteyears"],
                    "n_distinct_sites":len(x["sites"]),
                    "all_sameyear_siteyears":x["all_sameyear_siteyears_irrespective_of_method"],
                    "excluded_different_source_method_siteyears":x["excluded_different_source_method_siteyears"]}
         for (a,b),x in coannual.items()},
      "main_ensemble":[
          {k:(None if pd.isna(v) else (v.item() if isinstance(v,np.generic) else v))
           for k,v in r.items()}
          for r in table[
             table.scenario.eq(MAIN[0])&table.period.eq(MAIN[1])&
             table.model.eq("three_model_equal_mean")
          ].to_dict("records")],
      "limitations":[
         "Same colony site physical SIC is identical regardless of penguin species, algebraically; source medians assign different site weights.",
         "Equal original-reporting-region weight is standardization, not a source-wide species preference or causal intervention.",
         "2011-2020 site-species medians can arise from different census years; do not call a recorded site overlapping species same-year co-census.",
         "Same-year, same-method does not guarantee identical survey day, author citation, area, or calibrated method.",
         "Model wet-grid center distance is not an ecological foraging range or colony-specific forecast uncertainty.",
         "No true demographic responses, source absences, 2050/2100 colony nests or species vulnerability estimated."
      ]
    }
    return table,receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--counts",type=Path,required=True)
    p.add_argument("--inventory",type=Path,required=True)
    p.add_argument("--cmip6-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    counts,species,obs,ice=read_fixed(a.counts,a.inventory,a.cmip6_zip)
    table,receipt=run(counts,species,obs,ice)
    table.to_csv(a.out/"source_matched_species_geographic_support_comparison.csv",index=False)
    receipt["input_sha256"]={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in
                             [("count",a.counts),("inventory",a.inventory),("physical_zip",a.cmip6_zip)]}
    (a.out/"source_matched_species_geographic_support_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("SOURCE_MATCHED_SPECIES_SUPPORT="+json.dumps(
        {k:receipt[k] for k in ("status","n_support_rows",
                                 "true_method_matched_sameyear_pair_support","main_ensemble")},
        ensure_ascii=False),flush=True)

if __name__=="__main__":main()
