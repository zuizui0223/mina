#!/usr/bin/env python3
"""Four original-source paper figures, v0.6 candidate.

This is rendering/recalculation of FROZEN derived source inputs, not a fourth
independent ecological experiment or a causal climate-to-breeding inference.
Biological sources have distinct sampling units, months and geography.
"""
from __future__ import annotations
import argparse,ast,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Transformer

SOURCE_SHA={
    "atlas":"add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a",
    "ocean":"30c311ef8312e8424919bec0230c72eec7ab0a9db40997275fccfde0fa7e95c8",
    "isotope":"dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205",
    "future":"4cf7c2324f029d9951b4fe22502f650205f8a8c711646f7645427e747fe0240a",
    "coupling":"bbea3379b69c8475c1e89275fe33471a7886abe811b7443a016f5bcb61ddbe3d"
}
BG="#FFFFFF"
INK="#253449"
BLUE="#40699C"
ORANGE="#CB7959"
TEAL="#3B807A"
GREY="#A6AFB7"
def zipdata(filename,key,sha):
    raw=Path(filename).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError(f"Source ZIP SHA256 mismatch {filename}")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:raise ValueError(f"Source ZIP corrupt {filename}")
        return pd.read_csv(io.BytesIO(z.read(key)))
def commit(fig,out,name):
    fig.savefig(out/(name+".png"),dpi=240,bbox_inches="tight",facecolor="white")
    fig.savefig(out/(name+".svg"),bbox_inches="tight",facecolor="white")
    plt.close(fig)
def make_figures(a):
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                         "axes.spines.right":False,"figure.facecolor":"white",
                         "axes.labelcolor":INK,"text.color":INK,"axes.titleweight":"bold",
                         "axes.titlesize":12,"savefig.facecolor":"white"})
    atlas=zipdata(a.atlas,"panantarctic_595_site_inventory.csv",SOURCE_SHA["atlas"])
    ocean=zipdata(a.ocean,"all_original_18region_1993_2020_real_joint_marine_3var_site_year.csv",SOURCE_SHA["ocean"])
    iso=zipdata(a.isotope,"matched_860_original_isotope_ocean_ice_site_seasons.csv",SOURCE_SHA["isotope"])
    regions=zipdata(a.isotope,"region_specific_exploratory_coefficients.csv",SOURCE_SHA["isotope"])
    future=zipdata(a.future,"original_595_CMIP6_4scenario_joint_ice_sos_main_summary.csv",SOURCE_SHA["future"])
    coupling=zipdata(a.coupling,"original_12_CMIP6_model_SIC_SOS_future_spatial_coupling.csv",SOURCE_SHA["coupling"])
    roster=pd.read_csv(a.roster)
    pairs=pd.read_csv(a.pairs)
    if (len(atlas),atlas.site_id.nunique(),len(ocean),ocean.site_id.nunique(),len(iso),iso.site_id.nunique())!=(595,595,16464,588,860,88):
        raise ValueError("Original 595 / 588 / 860 source denominators drift")
    if (len(roster),set(roster.n_sites))!=(3,{19,26,35}):raise ValueError("Actual Adélie roster drift")
    pair=pairs.query("pair == 'ADPE__GEPE'").copy()
    if len(pair)!=6 or not pair.ratio_slope.gt(0).all() or pair.pair_subtotal_pct_change.gt(0).sum()!=5:
        raise ValueError("Original six strictly shared source-pair colony results changed")
    if len(future)!=16 or len(coupling)!=12:raise ValueError("Future 4 scenario and 12 model tests not original")

    # Fig 1: one climate PCA from full original 588×28 actual source years,
    # plus the known colony and isotope-observation source location footprint.
    x=ocean[["SIC_pp","GLORYS_thetao_C","GLORYS_salinity"]].to_numpy(dtype=float)
    z=(x-x.mean(0))/x.std(0,ddof=0)
    cov=np.cov(z,rowvar=False)
    eigval,eigvec=np.linalg.eigh(cov)
    order=np.argsort(eigval)[::-1]
    vals=eigval[order]; vec=eigvec[:,order]
    if vec[1,0]<0:vec[:,0]*=-1
    if vec[2,1]<0:vec[:,1]*=-1
    variance=vals/vals.sum()
    if not (abs(variance[0]-.603654)<3e-5 and abs(variance[1]-.333773)<3e-5):
        raise ValueError("Original thermal–ice/salinity PCA unexplained deviation")
    if not (abs(vec[0,0]+.70734)<.003 and abs(vec[1,0]-.70583)<.003 and abs(vec[2,1]-.99772)<.003):
        raise ValueError("Signed original source marine axes changed")

    fig,axs=plt.subplots(1,2,figsize=(12.5,5.7),gridspec_kw={"width_ratios":[1,1.08]})
    ax=axs[0]
    tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    coords=atlas.copy()
    cx,cy=tr.transform(coords.longitude.to_numpy(),coords.latitude.to_numpy())
    coords["x"]=np.asarray(cx)/1e6;coords["y"]=np.asarray(cy)/1e6
    ax.scatter(coords.x,coords.y,s=18,c=GREY,alpha=.50,linewidths=0,label="Known sites, n=595",zorder=1)
    ids=set(iso.site_id)
    chosen=coords.loc[coords.site_id.isin(ids)]
    if len(chosen)!=88:raise ValueError("Original isotope unique site IDs not in MAPPPD 595")
    ax.scatter(chosen.x,chosen.y,s=28,c=BLUE,alpha=.88,marker="o",
               edgecolors="white",linewidths=.3,label="Optical isotope, n=88",zorder=2)
    for lat in [-60,-70,-80]:
        lons=np.linspace(-180,180,361)
        rr,ss=tr.transform(lons,np.full(len(lons),lat))
        ax.plot(np.asarray(rr)/1e6,np.asarray(ss)/1e6,color=GREY,alpha=.32,linewidth=.65,linestyle=":")
    ax.set_aspect("equal");ax.set_title("a. Original Antarctic colony coverage",loc="left")
    ax.set_xlabel("Polar stereographic x (1000 km)");ax.set_ylabel("Polar stereographic y (1000 km)")
    ax.legend(loc="lower left",fontsize=8,frameon=False)
    ax.grid(alpha=.10)
    ax=axs[1]
    xpos=np.arange(3)
    width=.33
    ax.bar(xpos-width/2,vec[:,0],width,label=f"PC1 — {100*variance[0]:.1f}%",color=BLUE)
    ax.bar(xpos+width/2,vec[:,1],width,label=f"PC2 — {100*variance[1]:.1f}%",color=TEAL)
    ax.axhline(0,color=GREY,linewidth=.8)
    ax.set_xticks(xpos,["Sea ice","Seawater temp.","Salinity"])
    ax.set_ylabel("Signed principal component loading")
    ax.set_ylim(-.90,1.12)
    ax.set_title("b. Nearshore marine conditions are multidimensional",loc="left")
    ax.text(.44,.07,"588 sites · 378 unique ocean cells\n1993–2020 · 16,464 site-years",fontsize=8.3,
            transform=ax.transAxes,va="bottom",ha="left",color=INK)
    ax.legend(loc="upper left",fontsize=9,frameon=False)
    fig.suptitle("Figure 1 | Antarctic marine environment and true observation footprint",fontsize=14,fontweight="bold")
    fig.tight_layout()
    commit(fig,out,"Fig1_Marine_axes_and_source_footprint")

    # Fig 2: actual colony reweighting and same-source 6-pair site biology.
    fig,axs=plt.subplots(1,2,figsize=(12.7,5.5))
    reg={"all_three_decades":"19 sites / three decades",
         "two_plus_endpoint_years":"26 sites / endpoints",
         "one_plus_endpoint_year":"35 sites / endpoints"}
    rs=roster.set_index("cohort").loc[list(reg)]
    ax=axs[0]
    yt=np.arange(3)
    vals=rs.observed_nest_count_weighted_south_shift_km.to_numpy(dtype=float)
    ax.barh(yt,vals,color=BLUE,alpha=.89,height=.52)
    ax.set_yticks(yt,list(reg.values()),fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("More southerly nest-count-weighted position (km)")
    ax.set_xlim(0,135)
    for k,shift in enumerate(vals):ax.text(shift+3,k,f"{shift:.1f} km",va="center",fontsize=9)
    ax.set_title("a. Fixed-colony Adélie nesting reweighting",loc="left")
    ax=axs[1]
    ax.scatter(pair.ratio_slope,pair.pair_subtotal_pct_change,c=np.where(pair.pair_subtotal_pct_change>0,TEAL,ORANGE),
               s=65,edgecolors="white",linewidth=.6,zorder=3)
    for p in pair.itertuples(index=False):
        ax.annotate(str(p.site),(p.ratio_slope,p.pair_subtotal_pct_change),xytext=(4,5),
                    textcoords="offset points",fontsize=9)
    ax.axvline(0,color=GREY,linewidth=1,linestyle="--")
    ax.axhline(0,color=GREY,linewidth=1,linestyle="--")
    ax.set_xlabel("Change in log(gentoo / Adélie nest ratio), per decade")
    ax.set_ylabel("First-to-last observed two-species nest sum (%)")
    ax.set_title("b. Relative change ≠ total nesting change",loc="left")
    ax.text(.98,.05,"Same source/method, 6 sites in 2 regions\n6/6 ratios rose; 5/6 subtotals rose",
            transform=ax.transAxes,ha="right",va="bottom",fontsize=8.6)
    fig.suptitle("Figure 2 | Breeding allocation and local species composition",fontsize=14,fontweight="bold")
    fig.tight_layout()
    commit(fig,out,"Fig2_Nest_reweighting_and_species_ratio")

    # Fig 3: observational salinity x isotope: region-specific coefficients and
    # two legitimate intervals (wet-cell vs conservative source region).
    def interval(v):
        if not isinstance(v,str) or not v.strip():return None
        y=ast.literal_eval(v)
        return [float(y[0]),float(y[1])]
    q=regions.loc[regions.beta_salinity.notna()].copy()
    q["ci"]=q.normal_95ci.map(interval)
    q=q.loc[q.ci.notna()].sort_values("beta_salinity")
    if len(q)!=8:raise ValueError(f"Original supported region slope count changed: {len(q)}")
    fig,axs=plt.subplots(1,2,figsize=(13,6),gridspec_kw={"width_ratios":[1.3,.9]})
    ax=axs[0]
    ycoords=np.arange(len(q))
    for k,p in enumerate(q.itertuples(index=False)):
        lo,hi=p.ci
        color=TEAL if p.beta_salinity>=0 else ORANGE
        ax.plot([lo,hi],[k,k],color=color,lw=2)
        ax.plot([lo,lo],[k-.10,k+.10],color=color,lw=1.3)
        ax.plot([hi,hi],[k-.10,k+.10],color=color,lw=1.3)
        ax.scatter([p.beta_salinity],[k],c=[color],s=48,zorder=3)
    ax.axvline(0,linewidth=1,color=GREY,ls="--")
    ax.set_yticks(ycoords,[f"{r.region} (n={int(r.n)})" for r in q.itertuples(index=False)],fontsize=8.3)
    ax.set_xlabel("δ¹⁵N proxy slope per salinity unit (within-region model)")
    ax.set_title("a. Region-specific, exploratory associations",loc="left")
    ax.grid(axis="x",alpha=.15)
    ax=axs[1]
    b=.8341458422
    for y,lo,hi,title,color in [(1,.38863,1.27967,"82 marine-cell clusters",BLUE),
                                (0,-.01594,1.68424,"13 reporting-region clusters",ORANGE)]:
        ax.plot([lo,hi],[y,y],color=color,lw=3)
        ax.scatter([b],[y],s=70,c=[color])
        ax.text((lo+hi)/2,y+.16,title,ha="center",fontsize=8.8)
    ax.axvline(0,linewidth=1,color=GREY,ls="--")
    ax.set_ylim(-.6,1.7);ax.set_xlim(-.45,2.0)
    ax.set_yticks([])
    ax.set_xlabel("Pooled conditional salinity slope (δ¹⁵N ‰ per salinity unit)")
    ax.set_title("b. Geographic uncertainty matters",loc="left")
    ax.text(.03,.13,"860 site-seasons · 88 colonies · 13 regions\nPartial residual R² = 2.88%\nPositive pooled association; region CI includes 0.\nOptical isotope proxy, not direct fish fraction.",
            transform=ax.transAxes,ha="left",va="bottom",fontsize=8.6)
    fig.suptitle("Figure 3 | Salinity-associated Adélie isotope variation (1996–2012)",fontsize=14,fontweight="bold")
    fig.tight_layout()
    commit(fig,out,"Fig3_Positive_salinity_isotope_geography")

    # Fig 4: same 271 counted sites, equal-site versus observed nest-median
    # weighting is the focal comparison; separate panel shows the three-model
    # geographic coupling of future SIC and salinity. No future nest forecast.
    fig,axs=plt.subplots(1,2,figsize=(13.6,5.9),gridspec_kw={"width_ratios":[1.2,.8]})
    order=[("ssp245","2041-2060"),("ssp245","2081-2100"),
           ("ssp585","2041-2060"),("ssp585","2081-2100")]
    labels=["Lower emissions\n2041–2060","Lower emissions\n2081–2100",
            "Higher emissions\n2041–2060","Higher emissions\n2081–2100"]
    q271eq=future[future.weight_cohort=="271_source_counted_colonies_equal_site"].copy()
    q271nest=future[future.weight_cohort=="271_source_counted_colonies_nest_proxy_weight"].copy()
    if len(q271eq)!=4 or len(q271nest)!=4:
        raise ValueError("Same-271 site-equal versus recorded-nest-weight source cohorts missing")
    eq=q271eq.set_index(["scenario","period"]).loc[order]
    wt=q271nest.set_index(["scenario","period"]).loc[order]
    if not (eq.n_source_site_ids.eq(271).all() and wt.n_source_site_ids.eq(271).all()
            and np.isclose(eq.mean_delta_sic_pp.iloc[-1],-28.634,atol=.01)
            and np.isclose(wt.mean_delta_sic_pp.iloc[-1],-13.276240917274329,atol=.00001)):
        raise ValueError("Source matched 271 sites and expected future ice exposure changed")
    delta_equal=eq.mean_delta_sic_pp.to_numpy()
    delta_nest=wt.mean_delta_sic_pp.to_numpy()
    if not np.all(delta_equal<delta_nest):
        raise ValueError("Original 4 scenarios site-vs-nest source contrast drift")
    ax=axs[0]
    xx=np.arange(4)
    ax.bar(xx-.18,delta_equal,.36,color=BLUE,label="271 sites, equal weights")
    ax.bar(xx+.18,delta_nest,.36,color=ORANGE,label="Same 271 sites, fixed recorded nest medians")
    ax.set_xticks(xx,labels,fontsize=8.1)
    ax.set_ylim(-37,2)
    ax.set_ylabel("Projected change in coastal sea ice (percentage points)")
    ax.set_title("a. Location counts and recorded nests yield different exposure",loc="left")
    ax.axhline(0,lw=.9,color=GREY)
    ax.grid(axis="y",alpha=.17)
    ax.legend(loc="lower left",fontsize=8.3,frameon=False)
    ax.annotate("+15.36 points",
        xy=(xx[-1]+.18,float(delta_nest[-1])),xytext=(2.38,-4.5),
        arrowprops={"arrowstyle":"->","color":INK,"lw":.9},
        fontsize=8.6,color=INK)
    ax.text(.02,.02,
        "All four bars compare the same counted sites per scenario.\n"
        "Higher-emissions late-century difference:\n"
        "+15.66 between regions −0.30 within regions.",
        transform=ax.transAxes,fontsize=8.1,ha="left",va="bottom",
        bbox={"facecolor":"white","edgecolor":"none","alpha":.92,"pad":2.5})

    modelcol={"ACCESS-CM2":BLUE,"BCC-CSM2-MR":TEAL,"CESM2":ORANGE}
    q=coupling[(coupling.scenario=="ssp585")&(coupling.period=="2081-2100")].sort_values("source_model")
    if len(q)!=3 or not (q.site_equal_within_region_corr_delta_sic_delta_sos.gt(0).sum()==1):
        raise ValueError("Original CMIP6 future coupling model sign split changed")
    ax=axs[1]
    for k,p in enumerate(q.itertuples(index=False)):
        c=modelcol[p.source_model]
        ax.plot([p.site_equal_raw_corr_delta_sic_delta_sos,
                 p.model_cell_region_equal_within_region_corr_delta_sic_delta_sos],[k,k],
                 lw=2,color=c,alpha=.65)
        ax.scatter([p.site_equal_raw_corr_delta_sic_delta_sos],[k],c=[c],s=72,marker="o")
        ax.scatter([p.model_cell_region_equal_within_region_corr_delta_sic_delta_sos],[k],c=[c],s=72,marker="s")
    ax.set_yticks(range(3),q.source_model.tolist())
    ax.set_xlim(-.9,1.0)
    ax.axvline(0,ls="--",color=GREY,lw=.9)
    ax.set_xlabel("Spatial correlation: projected sea-ice vs salinity changes")
    ax.set_title("b. Their joint geography differs across climate models",loc="left")
    ax.text(.05,.06,
        "Circle: all 595 known sites\nSquare: one native ocean cell × region\n"
        "Higher emissions, 2081–2100",
        transform=ax.transAxes,fontsize=8.5,va="bottom")
    fig.suptitle("Figure 4 | Nest-weighted climate exposure and marine-model disagreement",
                 fontsize=13.3,fontweight="bold")
    fig.tight_layout()
    commit(fig,out,"Fig4_Future_ice_freshening_model_disagreement")

    report={
        "status":"PASS_FOUR_V06_ORIGINAL_SOURCE_FIGURES_WITH_DISTINCT_BIOLOGICAL_DENOMINATORS",
        "figures":[
            "Fig1_Marine_axes_and_source_footprint",
            "Fig2_Nest_reweighting_and_species_ratio",
            "Fig3_Positive_salinity_isotope_geography",
            "Fig4_Future_ice_freshening_model_disagreement"
        ],
        "source_sha256":SOURCE_SHA,
        "n_original_known_colony_sites":595,
        "n_original_marine_annual_site_years":16464,
        "n_original_distinct_GLORYS_wet_cells":int(ocean[["source_original_wet_grid_x","source_original_wet_grid_y"]].drop_duplicates().shape[0]),
        "marine_pca_pc1_fraction":float(variance[0]),
        "marine_pca_pc2_fraction":float(variance[1]),
        "marine_pca_loadings_columns_SIC_temperature_salinity":vec[:,:2].tolist(),
        "original_Adelie_rosters":roster[["cohort","n_sites","observed_nest_count_weighted_south_shift_km"]].to_dict("records"),
        "strict_actual_Adelie_Gentoo_species_pair_sites":int(len(pair)),
        "strict_pair_positive_ratios":int(pair.ratio_slope.gt(0).sum()),
        "strict_pair_subtotals_positive":int(pair.pair_subtotal_pct_change.gt(0).sum()),
        "historical_positive_salt_optical_isotope_beta":.8341458422,
        "historical_optical_isotope_region_conservative_CI_crosses_zero":True,
        "n_original_isotope_source_site_seasons":860,
        "future_three_selected_model_only":True,
        "same_271_counted_sites_equal_weight_late_sic_pp":float(delta_equal[-1]),
        "same_271_counted_sites_recorded_nest_weight_late_sic_pp":float(delta_nest[-1]),
        "same_271_counted_sites_late_sic_weighting_gap_pp":float(delta_nest[-1]-delta_equal[-1]),
        "source_counted_site_denominator_held_fixed_between_weights":True,
        "original_271_counted_sites_not_future_population":True,
        "no_fish_or_krill_fraction_forecast":True,
        "no_salinity_mechanism_or_penguin_abundance_forecast":True,
        "observed_data_and_model_scenarios_have_distinct_months_and_grid_units":True}
    (out/"v06_four_figure_original_source_receipt.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ["atlas","ocean","isotope","future","coupling","roster","pairs","out"]:
        p.add_argument("--"+k,required=True)
    make_figures(p.parse_args())
