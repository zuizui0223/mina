#!/usr/bin/env python3
"""Original-source nested-region transfer gate for Antarctic penguin response channels.

Audits:
 - True Youngflesh original-image 860 Adélie δ15N proxy site×seasons
 - True MAPPPD same-site same-year paired nesting counts (351)
 - True method-fixed observed counts 2456 and 588 source colony marine panel

Primary source restriction is PRE-OUTCOME: include only reporting regions with
observed co-census species pairs, independent of isotope or salinity values.
Re-estimate the same isotope model, preserving original explanatory season
(11–February), site and region-by-year fixed effects, 150 km author SIC, GLORYS
SST and salinity, and source original cell-cluster standard errors.

This tests geographic scope and observation support, NOT equality of channel
causal effects or different-species niche parameters.
"""
from __future__ import annotations
import argparse,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

BIO_Y="predicted_d15N_season_day_equal"
X_BASE=["mean_doy_centered","mean_doy_sq",
        "GLORYS_NovFeb_thetao_C","author_SIC_150km_NovFeb_center_approx_fraction"]
SALT="GLORYS_NovFeb_salinity"

def read_zip_csv(path,member):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, "Corrupt original archived source"
        return pd.read_csv(io.BytesIO(archive.read(member)))

def demean_two_ways(values,site,regionseason):
    v=np.asarray(values,dtype=float).copy()
    s=pd.Series(site).reset_index(drop=True)
    g=pd.Series(regionseason).reset_index(drop=True)
    for _ in range(3000):
        old=v.copy()
        v-=pd.Series(v).groupby(s,sort=False).transform("mean").to_numpy()
        v-=pd.Series(v).groupby(g,sort=False).transform("mean").to_numpy()
        if np.max(np.abs(v-old))<1e-10:
            break
    else:
        raise ValueError("Original fixed-effect projection did not converge")
    if max(np.max(abs(pd.Series(v).groupby(s).mean())),
           np.max(abs(pd.Series(v).groupby(g).mean())))>1e-7:
        raise ValueError("Nonzero original fixed effects after projection")
    return v

def isotope_fit(data):
    d=data.reset_index(drop=True).copy()
    regionyear=d.source_region.astype(str)+"__"+d.season.astype(str)
    x=np.column_stack([demean_two_ways(d[k],d.site_id,regionyear)
                       for k in X_BASE+[SALT]])
    y=demean_two_ways(d[BIO_Y],d.site_id,regionyear)
    cells=d.source_wet_grid_y.astype(str)+":"+d.source_wet_grid_x.astype(str)
    report={
        "n_isotope_site_seasons":len(d),
        "n_sites":int(d.site_id.nunique()),
        "n_regions":int(d.source_region.nunique()),
        "n_original_wet_cells":int(cells.nunique()),
        "n_source_region_seasons":int(regionyear.nunique()),
        "rank_with_original_fe":int(np.linalg.matrix_rank(x,tol=1e-8)),
        "same_original_conditions":"site FE + source region×season FE + DOY + DOY squared + Nov-Feb thetao + Nov-Feb native SIC 150km + Nov-Feb GLORYS salinity",
    }
    if len(d)<30 or report["rank_with_original_fe"]!=5:
        report["estimate_status"]="UNIDENTIFIABLE_OR_TOO_SMALL"
        return report
    fit0=sm.OLS(y,x[:,:4]).fit()
    fit1=sm.OLS(y,x).fit(cov_type="cluster",cov_kwds={"groups":cells})
    b=float(fit1.params[-1])
    ci=fit1.conf_int()[-1]
    report.update({
        "estimate_status":"SOURCE_CONDITIONAL_EXPLORATORY",
        "beta_salt":b,
        "cluster_cell_95ci":[float(ci[0]),float(ci[1])],
        "partial_residual_r2":float(1-(fit1.resid@fit1.resid)/(fit0.resid@fit0.resid)),
        "n_source_residual_df_proxy_not_ecological_replicates":int(len(d)-5),
    })
    return report

def audit(args):
    iso=read_zip_csv(args.isotope_860_zip,"matched_860_original_isotope_ocean_ice_site_seasons.csv")
    co=read_zip_csv(args.marine_588_zip,"original_true_cocensus_3species_pairs_1993_2020_with_18region_marine_PC1.csv")
    ocean=read_zip_csv(args.marine_588_zip,"all_original_18region_1993_2020_real_joint_marine_3var_site_year.csv")
    counts=read_zip_csv(args.original_counts_zip,"source_observed_2456.csv")
    if (len(iso),iso.site_id.nunique(),iso.source_region.nunique())!=(860,88,13):
        raise ValueError("Original Youngflesh 860 isotope source denominator changed")
    if (len(co),co.species_pair.value_counts().sort_index().to_dict())!=(
        351,{"ADPE__CHPE":88,"ADPE__GEPE":98,"CHPE__GEPE":165}):
        raise ValueError("True 351 same-site co-census source changed")
    if len(counts)!=2456 or len(ocean)!=16464 or ocean.site_id.nunique()!=588:
        raise ValueError("Original paired marine/count source dimensions changed")
    if iso.duplicated(["site_id","season"]).any() or co.duplicated(["site_id","season","species_pair"]).any():
        raise ValueError("Original site-season record duplicated")
    if counts.duplicated(["site_id","species","season"]).any():
        raise ValueError("True census site×species×season duplicated")
    # All geographic restrictions are computed from observed co-census source SUPPORT,
    # never chosen based on isotope/salinity coefficients or sample fit.
    co_regions=sorted(set(co.source_region))
    common_regions=sorted(set(co.source_region)&set(iso.source_region))
    shared_regionseason=co[["source_region","season"]].drop_duplicates().merge(
        iso[["source_region","season"]].drop_duplicates(),
        on=["source_region","season"],how="inner",validate="one_to_one")
    exact_pairs=co.merge(iso[["site_id","season"]],on=["site_id","season"],how="inner")
    region_restricted=iso.loc[iso.source_region.isin(common_regions)].copy()
    regionyear_iso=iso.merge(shared_regionseason,on=["source_region","season"],validate="many_to_one")
    regionyear_co=co.merge(shared_regionseason,on=["source_region","season"],validate="many_to_one")
    original_adpe=counts[counts.species=="ADPE"]
    same_adpe=iso.merge(original_adpe[["site_id","season","observed_nest_count","original_survey_method"]],
                        on=["site_id","season"],how="inner",validate="one_to_one")
    counts_same=iso.merge(counts,on=["site_id","season"],how="inner",validate="one_to_many")
    repeat_counts=same_adpe.groupby("site_id").size()
    if (len(exact_pairs),len(shared_regionseason),len(region_restricted),len(regionyear_iso),
        len(regionyear_co),len(same_adpe),len(counts_same))!=(0,7,227,38,24,70,72):
        raise ValueError("Original biological response source overlap unexpectedly changed")
    total=isotope_fit(iso)
    restricted=isotope_fit(region_restricted)
    if abs(total["beta_salt"]-.8341458422028288)>1e-7 or abs(total["partial_residual_r2"]-.02880176895240346)>1e-9:
        raise ValueError("Original 860 source isotope/salt coefficient changed")
    if abs(restricted["beta_salt"]-.07989526387544739)>1e-7:
        raise ValueError("Source-preselected geographical scope sensitivity changed")
    if not np.sign(total["beta_salt"])==np.sign(restricted["beta_salt"]):
        raise ValueError("Unexpected salinity coefficient sign drift")
    byregion=[]
    allregions=sorted(set(iso.source_region)|set(co.source_region))
    for reg in allregions:
        d=iso[iso.source_region==reg]
        c=co[co.source_region==reg]
        n=d.merge(c[["season"]].drop_duplicates(),on="season",how="inner")
        byregion.append({
            "source_region":reg,"isotope_site_seasons":len(d),
            "isotope_sites":int(d.site_id.nunique()),
            "co_census_pair_records":len(c),
            "co_census_sites":int(c.site_id.nunique()),
            "same_region_season_isotope_rows":len(n),
            "same_region_season_cocensus_rows":len(c.merge(d[["season"]].drop_duplicates(),on="season")),
            "both_biological_response_channels_observed_in_region":bool(len(d) and len(c)),
        })
    pairs=[]
    for sp,d in sorted(co.groupby("species_pair")):
        r=sorted(set(d.source_region)&set(iso.source_region))
        rs=d[["source_region","season"]].drop_duplicates().merge(
            iso[["source_region","season"]].drop_duplicates(),on=["source_region","season"])
        a=iso[iso.source_region.isin(r)]
        pairs.append({"species_pair":sp,"original_cocensus_site_seasons":len(d),
                      "cocensus_regions":int(d.source_region.nunique()),
                      "shared_isotope_cocensus_regions":len(r),
                      "shared_region_seasons":len(rs),
                      "exact_same_site_seasons":int(len(d.merge(iso[["site_id","season"]],on=["site_id","season"]))),
                      "isotope_region_only_restricted":{"n":len(a),
                          "sites":int(a.site_id.nunique())},
                      "same_regionseason_isotope_rows":int(len(iso.merge(rs,on=["source_region","season"]))),
                      "same_regionseason_cocensus_rows":int(len(d.merge(rs,on=["source_region","season"]))),
                     })
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(byregion).to_csv(out/"original_response_region_by_region_source_support.csv",index=False)
    pd.DataFrame(pairs).to_csv(out/"original_three_pair_response_overlap_support.csv",index=False)
    shared_regionseason.sort_values(["source_region","season"]).to_csv(
        out/"original_seven_shared_response_region_seasons.csv",index=False)
    same_adpe[["site_id","season","source_region","observed_nest_count",
             BIO_Y,"GLORYS_NovFeb_salinity"]].to_csv(
        out/"source_70_exact_Adelie_nests_isotope_overlap_observation_only.csv",index=False)
    summary={
        "status":"PASS_ORIGINAL_SOURCE_REGION_TRANSFER_SCOPE_NEGATIVE_CONTROL",
        "original_588_marine_sites":int(ocean.site_id.nunique()),
        "original_physical_site_years":len(ocean),
        "original_method_fixed_census_records":len(counts),
        "original_Adelie_isotope_site_seasons":len(iso),
        "original_true_same_site_species_pair_records":len(co),
        "exact_isotope_to_cocensus_site_season_matches":len(exact_pairs),
        "cross_channel_same_region_season_pairs":len(shared_regionseason),
        "cross_channel_regionseason_subset_isotope_rows":len(regionyear_iso),
        "cross_channel_regionseason_subset_cocensus_rows":len(regionyear_co),
        "cross_channel_shared_regions":common_regions,
        "original_Adelie_actual_count_and_isotope_exact_site_seasons":len(same_adpe),
        "original_Adelie_nest_and_isotope_same_site_seasons_repeated_sites":int((repeat_counts>=2).sum()),
        "original_Adelie_nest_and_isotope_same_site_seasons_on_repeated_sites":int(repeat_counts[repeat_counts>=2].sum()),
        "original_Adelie_nest_and_isotope_source_regions_with_repeated_site":int(
            same_adpe[same_adpe.site_id.isin(repeat_counts[repeat_counts>=2].index)].source_region.nunique()),
        "original_any_penguin_nest_and_isotope_site_seasons":int(counts_same[["site_id","season"]].drop_duplicates().shape[0]),
        "original_all_species_nest_records_exact_site_seasons":len(counts_same),
        "isotope_all_source_regions":total,
        "isotope_restricted_to_preselected_cocensus_regions":restricted,
        "same_regionseason_isotope_scope_estimate":isotope_fit(regionyear_iso),
        "co_census_by_pair":pairs,
        "source_coverage_restricted_without_using_observed_response_or_salt_coefficients":True,
        "positive_full_isotope_salinity_association_retained":True,
        "transfer_to_other_biological_response_not_established":True,
        "ecological_caveat":"Zero exact isotope–two-species co-census site×seasons. Separate response datasets have different geography/season/grain; regional restriction coefficient change does NOT prove salinity is biologically absent or significantly different.",
        "no_fish_krill_share_measured":True,"not_future_nest_projection":True,
    }
    (out/"original_response_channel_geographical_transfer_verdict.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({
        "status":summary["status"],
        "full_isotope_beta":total["beta_salt"],
        "full_isotope_partial_r2":total["partial_residual_r2"],
        "cocensus_region_isotope_beta":restricted["beta_salt"],
        "cocensus_region_isotope_partial_r2":restricted["partial_residual_r2"],
        "common_regions":common_regions,
        "exact_site_season_overlap":len(exact_pairs),
        "shared_regionseason":len(shared_regionseason),
        "exact_adpe_nests_isotope":len(same_adpe),
    },indent=2,ensure_ascii=False))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--isotope-860-zip",required=True)
    p.add_argument("--marine-588-zip",required=True)
    p.add_argument("--original-counts-zip",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    audit(args)
