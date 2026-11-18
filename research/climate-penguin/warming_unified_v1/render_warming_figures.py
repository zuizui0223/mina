#!/usr/bin/env python3
"""Create three original warming-first manuscript figures from frozen source-joined data."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

BASE=Path(__file__).resolve().parent
DATA=BASE/"data"
OUT=BASE/"outputs"
FIG=BASE/"figures"

def read(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def export(fig,stem):
    FIG.mkdir(parents=True,exist_ok=True)
    for ext in ("png","svg"):
        f=FIG/(stem+"."+ext)
        fig.savefig(f,dpi=200,format=ext,bbox_inches="tight",facecolor="white")
        if f.stat().st_size<1500:raise ValueError("Unexpectedly empty plot "+str(f))
    plt.close(fig)

def main():
    original=json.loads((OUT/"WARMING_UNIFIED_EVIDENCE.json").read_text())
    assert original["same_location_community"]["strict_shared_breeding_sites"]==6
    assert original["same_year_Signy"]["n_climate_years"]==9
    six=read(DATA/"six_site_original_breeding_ice.csv")
    nine=read(DATA/"signy_same_year_diet_phenology.csv")
    fut=read(DATA/"six_site_future_physical.csv")
    assert (len(six),len(nine),len(fut))==(6,9,24)
    six=sorted(six,key=lambda r:(r["region"],r["site_id"]))
    site=[x["site_id"] for x in six]
    region=[x["region"] for x in six]
    vals=np.array([float(x["log_ratio_slope_decade"]) for x in six])
    observed=np.array([float(x["sep_SIC_observed_years_pp_decade"]) for x in six])
    long=np.array([float(x["aug_nov_SIC_full_1991_2020_pp_decade"]) for x in six])
    fig,ax=plt.subplots(1,2,figsize=(12,5.0),gridspec_kw={"width_ratios":[1,1.3]})
    y=np.arange(6)
    ax[0].barh(y,vals,color="0.33",height=.6)
    ax[0].axvline(0,color="0.25",lw=.9)
    ax[0].set_yticks(y,[f"{x}  ({region[i].replace('Antarctic Peninsula','AP')})" for i,x in enumerate(site)],fontsize=9)
    ax[0].set_title("Observed nesting: all 6 true ratios increase",loc="left",fontsize=11)
    ax[0].set_xlabel("log(Gentoo/Adelie) nest ratio slope / decade")
    ax[0].invert_yaxis()
    ax[1].barh(y-.18,observed,height=.34,color="0.3",label="September, counted years only")
    ax[1].barh(y+.18,long,height=.34,color="0.73",label="Aug–Nov, all 1991–2020 years")
    ax[1].axvline(0,color="0.25",lw=.9)
    ax[1].set_yticks(y,site,fontsize=9)
    ax[1].set_xlabel("Observed nearshore SIC slope (percentage points / decade)")
    ax[1].set_title("Sea-ice trend changes with the observation window",loc="left",fontsize=11)
    # Avoid covering LLAN data bar; legend beneath the right panel.
    ax[1].legend(loc="upper center",bbox_to_anchor=(.52,-.20),
                 ncol=2,fontsize=8,frameon=False)
    ax[1].invert_yaxis()
    for a in ax:a.spines[["top","right"]].set_visible(False)
    fig.suptitle("Fixed six-site breeding-community reorganization and climate timescales",fontsize=13,fontweight="bold")
    fig.tight_layout(rect=(0,.07,1,.93))
    export(fig,"FIG1_SIX_SITE_BREEDING_VS_SIC_TIMESCALE")

    nine=sorted(nine,key=lambda r:int(r["year"]))
    ice=np.array([float(x["sic_aug_nov_pct"]) for x in nine])
    fish=np.array([float(x["diet_gap_fish_fraction"]) for x in nine])
    gap=np.array([float(x["hatching_gap_days"]) for x in nine])
    years=[x["year"] for x in nine]
    a=original["same_year_Signy"]
    fig,axes=plt.subplots(1,2,figsize=(11,4.9))
    for k,(ax,yy,title,r) in enumerate(((axes[0],fish,"Gentoo – Adelie fish-fraction contrast",a["r_sic_vs_fish_gap"]),(axes[1],gap,"Chinstrap – Adelie hatching gap",a["r_sic_vs_hatching_gap"]))):
        ax.scatter(ice,yy,color="0.15",s=36,zorder=3)
        for year,x,y in zip(years,ice,yy):
            ax.annotate(year[-2:],(x,y),xytext=(4,4),textcoords="offset points",fontsize=8)
        ax.set_title(f"{title}\nr = {r:+.3f} on same 9 climate years",loc="left",fontsize=11)
        ax.set_xlabel("Signy GOPT Aug–Nov sea ice (%)")
        ax.set_ylabel("Fish fraction (0–1)" if k==0 else "Mean hatching date difference (days)")
        ax.grid(alpha=.2)
        ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Same season, different ecological niche measures",fontsize=13,fontweight="bold")
    fig.text(.06,.012,"Marine pair: Gentoo–Adelie (422 stomachs over 9 seasons); temporal pair: Chinstrap–Adelie (9 annual means). No causal regression or p values.",fontsize=8)
    fig.tight_layout(rect=(0,.045,1,.91))
    export(fig,"FIG2_SIGNY_SHARED_YEARS_MARINE_TEMPORAL")

    target=original["future_six_sites"]["scenario_site_equal_means"]
    labels=[("245" if x["experiment"]=="ssp245" else "585")+" / "+("mid" if x["period"]=="2041-2060" else "late") for x in target]
    air=[float(x["mean_tas_C"]) for x in target]
    sic=[float(x["mean_SIC_pp"]) for x in target]
    y=np.arange(4)
    fig,axes=plt.subplots(1,2,figsize=(11,4.8))
    axes[0].barh(y,air,color="0.35",height=.65)
    axes[1].barh(y,sic,color="0.55",height=.65)
    for ax,v,title in [(axes[0],air,"Surface-air temperature ∆ (°C)\n6/6 source sites"),(axes[1],sic,"Marine ice concentration ∆ (pp)\n4/6 sites, 2 distinct grid fingerprints")]:
        ax.axvline(0,color="0.2",linewidth=.8)
        ax.set_yticks(y,labels)
        ax.invert_yaxis()
        ax.set_title(title,loc="left",fontsize=11)
        ax.spines[["top","right"]].set_visible(False)
        for i,x in enumerate(v):
            ax.text(x+(0.1 if x>=0 else -0.1),i,f"{x:+.2f}",ha="left" if x>=0 else "right",va="center",fontsize=9)
        mn=min([0]+v);mx=max([0]+v)
        span=max(.01,mx-mn)
        ax.set_xlim(mn-.20*span,mx+.28*span)
    fig.suptitle("Six original breeding sites: physical CMIP6 exposure only",fontsize=13,fontweight="bold")
    fig.text(.03,.012,"3 climate models; scenario means are model/site summaries, not observed biological future or uncertainty intervals. PCHA/PETE have no ≤50 km verified marine cell.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.91))
    export(fig,"FIG3_PHYSICAL_CMIP6_NOT_BREEDING_FORECAST")

    items=[]
    for stem in ("FIG1_SIX_SITE_BREEDING_VS_SIC_TIMESCALE",
                 "FIG2_SIGNY_SHARED_YEARS_MARINE_TEMPORAL",
                 "FIG3_PHYSICAL_CMIP6_NOT_BREEDING_FORECAST"):
        f=FIG/(stem+".png")
        with Image.open(f) as img:
            w,h=img.size
            assert w>1100 and h>600
        items.append({"stem":stem,"png_size":[w,h],
            "png_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
            "svg_sha256":hashlib.sha256((FIG/(stem+".svg")).read_bytes()).hexdigest()})
    receipt={"status":"WARMING_FIGURES_FROM_LOCKED_OBSERVATIONAL_AND_PHYSICAL_INPUTS",
       "sample_six_sites":6,"same_year_climate_n":9,"stomach_data_n":422,
       "future_scenarios":4,"future_marine_sites":4,"new_inference":False,
       "source_evidence_sha256":hashlib.sha256((OUT/"WARMING_UNIFIED_EVIDENCE.json").read_bytes()).hexdigest(),
       "figures":items}
    (OUT/"WARMING_FIGURES_QA.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"status":receipt["status"],"figures":items,"same_season_r":[a["r_sic_vs_fish_gap"],a["r_sic_vs_hatching_gap"]]}))

if __name__=="__main__":
    main()
