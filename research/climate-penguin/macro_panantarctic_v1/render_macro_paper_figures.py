#!/usr/bin/env python3
"""Reproducible paper figures from already VERIFIED source/macro outputs.

No new model, parameter search or resampling; this script only renders three
separate quantitative figures with all 250-km source-block uncertainty and
site-count limitations retained. The 173 mapped land points are positive source
detections, NOT botanical abundance/annual greening.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def csvrows(p):
    with Path(p).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def openjson(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))
def save(fig,out,name):
    for ext in ("png","svg"):
        fig.savefig(out/f"{name}.{ext}",dpi=190,bbox_inches="tight")
    plt.close(fig)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--land-data",type=Path,required=True)
    ap.add_argument("--land-summary",type=Path,required=True)
    ap.add_argument("--trend-summary",type=Path,required=True)
    ap.add_argument("--pair-summary",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    site=csvrows(a.land_data)
    land=openjson(a.land_summary)
    trend=openjson(a.trend_summary)
    pair=openjson(a.pair_summary)
    if len(site)!=173 or land["n_original_2017to2023_positive_mapped_land_sites"]!=173:
        raise ValueError("Original positive mapped land site count changed")
    if trend["original_macro_site_support"]["eligible_trend_site_species"]!=100:
        raise ValueError("Original 100 breeding-site species cohort changed")
    if len(pair["pairs_fixed_before_statistical_outcome"])!=3:
        raise ValueError("Original 3-pair co-census family changed")
    labels={"ADPE":"Adelie","CHPE":"Chinstrap","GEPE":"Gentoo"}

    # Fig 2: actual SITE-LEVEL mean SIC vs static mapped positive plant area.
    fig,ax=plt.subplots(figsize=(7.5,5.5))
    regions=sorted({z["source_region"] for z in site})
    for reg in regions:
        ss=[z for z in site if z["source_region"]==reg]
        ax.scatter([float(z["mean_SIC"]) for z in ss],
                   [float(z["log_plant_area"]) for z in ss],
                   s=34,alpha=.75,label=f"{reg} (n={len(ss)})")
    r0=land["environment_environment_173_unique_sites"]
    ax.set_xlabel("Nearshore SIC, 1991–2020 Aug–Nov mean (%)")
    ax.set_ylabel("log(1 + positive mapped land vegetation area, m²)")
    ax.set_title("Region-structured marine and terrestrial environments\n173 observed penguin colony sites")
    ax.text(.02,.98,f"Across sites r = {r0['r_raw_SIC_vs_log1p_static_mapped_area']:+.3f}\n"
           f"Within region r = {r0['r_within_region_demeaned']:+.3f}",
           transform=ax.transAxes,va="top",ha="left",
           bbox=dict(boxstyle="round",facecolor="white",alpha=.85))
    ax.legend(fontsize=7,loc="center left",bbox_to_anchor=(1,0.5))
    ax.grid(alpha=.2)
    save(fig,a.out,"Figure2_original_173site_ice_static_land")

    # Fig 3: 100 fixed species/site long-term trends, one result per species.
    species=["ADPE","CHPE","GEPE"]
    mu=[];lo=[];hi=[];names=[]
    for sp in species:
        x=trend["pre_fixed_family_three_species"][sp]
        ci=x["250km_spatial_block_bootstrap"]["interval_95_percentile"]
        if ci is None or not ci[0]<=0<=ci[1]:
            raise ValueError("Unexpected publication inference boundary in species result")
        mu.append(x["within_region_demeaned_correlation"])
        lo.append(ci[0]);hi.append(ci[1])
        names.append(f"{labels[sp]}  (n={x['matched_original_series']}, blocks={x['n_original_250km_blocks']})")
    fig,ax=plt.subplots(figsize=(7.6,4.6))
    ypos=np.arange(len(species))
    mu=np.asarray(mu,dtype=float);lo=np.asarray(lo);hi=np.asarray(hi)
    ax.errorbar(mu,ypos,xerr=np.vstack((mu-lo,hi-mu)),fmt="o",capsize=5)
    ax.axvline(0,linestyle="--")
    ax.set_yticks(ypos,labels=names)
    ax.invert_yaxis()
    ax.set_xlim(-1.05,1.05)
    ax.set_xlabel("Within-region r: colony trend in SIC vs observed nest counts")
    ax.set_title("Species-dependent but spatially uncertain breeding response\n1991–2020 original matched census years")
    ax.grid(axis="x",alpha=.2)
    save(fig,a.out,"Figure3_100_colony_species_longterm_ice_nest_trends")

    # Supplement figure: regional pair balance, all three pairs predeclared.
    PAIRS=[("ADPE__GEPE","Adelie / Gentoo"),
           ("ADPE__CHPE","Adelie / Chinstrap"),
           ("CHPE__GEPE","Chinstrap / Gentoo")]
    mu=[];lo=[];hi=[];names=[]
    for sp,title in PAIRS:
        x=pair["pairs_fixed_before_statistical_outcome"][sp]
        ci=x["region_demeaned_250km_block_interval"]["95pct_interval"]
        if ci is None or not ci[0]<=0<=ci[1]:
            raise ValueError("Unexpected spatial error interval for original co-censused pair")
        mu.append(x["site_equal_region_demeaned_r"])
        lo.append(ci[0]);hi.append(ci[1])
        names.append(f"{title}  (sites={x['unique_original_colony_sites']}, "
                     f"blocks={x['n_polar_250km_blocks']})")
    fig,ax=plt.subplots(figsize=(7.6,4.6))
    ypos=np.arange(len(PAIRS))
    mu=np.asarray(mu);lo=np.asarray(lo);hi=np.asarray(hi)
    ax.errorbar(mu,ypos,xerr=np.vstack((mu-lo,hi-mu)),fmt="o",capsize=5)
    ax.axvline(0,linestyle="--")
    ax.set_yticks(ypos,labels=names)
    ax.invert_yaxis()
    ax.set_xlim(-1.05,1.05)
    ax.set_xlabel("Within-region site-equal r: SIC vs log nest ratio")
    ax.set_title("Co-censused species' nesting balances\nPeninsula-biased subpanel, 1991–2020")
    ax.grid(axis="x",alpha=.2)
    save(fig,a.out,"Supplement_original_species_pair_seaice")

    receipt={
      "status":"SOURCE_VERIFIED_PANANTARCTIC_THREE_FIGURES_RENDERED",
      "n_antarctic_original_colony_sites":595,
      "n_mapped_terrestrial_sites":len(site),
      "n_original_breeding_trend_site_species":100,
      "n_original_cocensused_pairs":3,
      "original_marine_site_months":71400,
      "figures":[
        "Figure2_original_173site_ice_static_land",
        "Figure3_100_colony_species_longterm_ice_nest_trends",
        "Supplement_original_species_pair_seaice"
      ],
      "no_novel_statistical_test_fitted":True,
      "source_note":"Plantarctica original land extent is static 2017–2023; do not relabel it as annual greening. All 250km intervals include zero; no regional climate effect is confirmed."
    }
    (a.out/"figure_source_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("MACRO_PAPER_FIGURE_RENDER_GATE="+json.dumps(receipt))

if __name__=="__main__":
    main()
