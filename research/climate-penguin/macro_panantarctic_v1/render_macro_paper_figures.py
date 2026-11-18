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
from pyproj import Transformer

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
    ap.add_argument("--all-colony-site-inventory",type=Path,required=True)
    ap.add_argument("--breeding-trend-site-data",type=Path,required=True)
    ap.add_argument("--land-data",type=Path,required=True)
    ap.add_argument("--land-summary",type=Path,required=True)
    ap.add_argument("--trend-summary",type=Path,required=True)
    ap.add_argument("--pair-summary",type=Path,required=True)
    ap.add_argument("--strict-publisher-summary",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    all_sites=csvrows(a.all_colony_site_inventory)
    breeding_sites=csvrows(a.breeding_trend_site_data)
    site=csvrows(a.land_data)
    land=openjson(a.land_summary)
    trend=openjson(a.trend_summary)
    pair=openjson(a.pair_summary)
    strict=openjson(a.strict_publisher_summary)
    if len(all_sites)!=595 or len({r["site_id"] for r in all_sites})!=595:
        raise ValueError("Original full 595 colony site map input changed")
    if len(breeding_sites)!=100 or len({r["site_id"] for r in breeding_sites})!=77:
        raise ValueError("Original 77 colony long-term trend geographic cohort changed")
    if len(site)!=173 or land["n_original_2017to2023_positive_mapped_land_sites"]!=173:
        raise ValueError("Original positive mapped land site count changed")
    if trend["original_macro_site_support"]["eligible_trend_site_species"]!=100:
        raise ValueError("Original 100 breeding-site species cohort changed")
    if len(pair["pairs_fixed_before_statistical_outcome"])!=3:
        raise ValueError("Original 3-pair source family changed")
    if strict["all_original_known_nest_count_same_site_season_pair_comparisons"]!=357 or strict["strict_shared_source_vantage_pairs"]!=277:
        raise ValueError("Original publisher citation/source pairing has changed")
    labels={"ADPE":"Adelie","CHPE":"Chinstrap","GEPE":"Gentoo"}

    # Fig 1: source coordinates only; do not claim an Antarctic coastline mask.
    all_ids={z["site_id"] for z in all_sites}
    land_ids={z["site_id"] for z in site}
    trend_ids={z["site_id"] for z in breeding_sites}
    if not land_ids<=all_ids or not trend_ids<=all_ids:
        raise ValueError("Figure site subsets are not subsets of 595 original colonies")
    to_polar=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    polar={}
    for z in all_sites:
        x,y=to_polar.transform(float(z["longitude"]),float(z["latitude"]))
        if not np.isfinite([x,y]).all():
            raise ValueError("Original colony cannot be positioned in Antarctic polar projection")
        polar[z["site_id"]]=(x/1e6,y/1e6)
    fig,ax=plt.subplots(figsize=(7.7,7.3))
    for latitude in (-60,-70,-80):
        lon=np.linspace(-180,180,361)
        xx,yy=to_polar.transform(lon,np.full(len(lon),latitude))
        ax.plot(np.array(xx)/1e6,np.array(yy)/1e6,linestyle=":",alpha=.25,linewidth=.8)
        lx,ly=to_polar.transform(10,latitude)
        ax.text(lx/1e6,ly/1e6,f"{abs(latitude)}°S",fontsize=8,alpha=.7)
    for longitude in range(-180,180,45):
        lats=np.linspace(-85,-60,100)
        xx,yy=to_polar.transform(np.full(len(lats),longitude),lats)
        ax.plot(np.array(xx)/1e6,np.array(yy)/1e6,linestyle=":",alpha=.2,linewidth=.65)
    xx=[polar[k][0] for k in sorted(all_ids)]
    yy=[polar[k][1] for k in sorted(all_ids)]
    ax.scatter(xx,yy,s=16,alpha=.5,label="Original surveyed penguin colonies (n=595)")
    ax.scatter([polar[k][0] for k in sorted(land_ids)],
               [polar[k][1] for k in sorted(land_ids)],
               s=25,marker="^",alpha=.7,
               label="Positive static mapped land sites (n=173)")
    ax.scatter([polar[k][0] for k in sorted(trend_ids)],
               [polar[k][1] for k in sorted(trend_ids)],
               s=26,marker="x",alpha=.9,
               label="Long-term nest/ice trend sites (n=77)")
    ax.set_aspect("equal")
    ax.set_title("Antarctic penguin colony observation coverage\n"
                 "Polar stereographic source coordinates (not a habitat map)")
    ax.set_xlabel("EPSG:3031 x (million metres)")
    ax.set_ylabel("EPSG:3031 y (million metres)")
    ax.legend(loc="lower center",bbox_to_anchor=(.5,-.17),fontsize=8)
    ax.grid(alpha=.1)
    save(fig,a.out,"Figure1_595colony_original_observation_coverage")

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

    # Original 357 nominal-season pairs versus publisher-citation-matched 277.
    PAIRS=[("ADPE__GEPE","Adelie / Gentoo"),("ADPE__CHPE","Adelie / Chinstrap"),
           ("CHPE__GEPE","Chinstrap / Gentoo")]
    broadmu=[];broadlo=[];broadhi=[]
    strictmu=[];strictlo=[];stricthi=[];names=[]
    for key,title in PAIRS:
        x=pair["pairs_fixed_before_statistical_outcome"][key]
        ci=x["region_demeaned_250km_block_interval"]["95pct_interval"]
        y=strict["fixed_all_three_species_pairs"][key]
        sci=y["strict_250km_block_interval"]["percentile_interval"]
        if ci is None or sci is None or not ci[0]<=0<=ci[1] or not sci[0]<=0<=sci[1]:
            raise ValueError("Unexpected source-matched spatial uncertainty")
        broadmu.append(x["site_equal_region_demeaned_r"])
        broadlo.append(ci[0]);broadhi.append(ci[1])
        strictmu.append(y["strict_region_demeaned_site_equal_r"])
        strictlo.append(sci[0]);stricthi.append(sci[1])
        names.append(f"{title} (n={x['source_same_year_co_census_observations']}/"
                     f"{y['n_strict_same_source_vantage_pairs']})")
    fig,ax=plt.subplots(figsize=(8.3,5.0))
    ypos=np.arange(len(PAIRS))
    bm=np.asarray(broadmu);bl=np.asarray(broadlo);bh=np.asarray(broadhi)
    sm=np.asarray(strictmu);sl=np.asarray(strictlo);sh=np.asarray(stricthi)
    ax.errorbar(bm,ypos-.12,xerr=np.vstack((bm-bl,bh-bm)),
                fmt="o",capsize=4,label="Both species recorded in same nominal season")
    ax.errorbar(sm,ypos+.12,xerr=np.vstack((sm-sl,sh-sm)),
                fmt="s",capsize=4,label="Original publisher citation + method match")
    ax.axvline(0,linestyle="--")
    ax.set_yticks(ypos,labels=names)
    ax.invert_yaxis()
    ax.set_xlim(-1.05,1.05)
    ax.set_xlabel("Within-region site-equal r: SIC vs observed log nest ratio")
    ax.set_title("Same-colony-season species-pair nesting associations\n"
                 "Spatial-block percentile intervals (250 km)")
    ax.legend(loc="upper center",bbox_to_anchor=(0.5,-.14),fontsize=8)
    ax.grid(axis="x",alpha=.2)
    fig.text(.5,.016,"Original survey date and effort not verified within either source cohort.",
             fontsize=8,ha="center")
    save(fig,a.out,"Supplement_original_species_pair_seaice")

    receipt={
      "status":"SOURCE_VERIFIED_PANANTARCTIC_FOUR_FIGURES_RENDERED",
      "n_antarctic_original_colony_sites":595,
      "n_mapped_terrestrial_sites":len(site),
      "n_original_breeding_trend_site_species":100,
      "n_original_cocensused_pairs":3,
      "n_source_pair_siteyears_broad":357,
      "n_source_pair_siteyears_shared_publisher_citation_method":277,
      "original_marine_site_months":71400,
      "figures":[
        "Figure1_595colony_original_observation_coverage",
        "Figure2_original_173site_ice_static_land",
        "Figure3_100_colony_species_longterm_ice_nest_trends",
        "Supplement_original_species_pair_seaice"
      ],
      "no_novel_statistical_test_fitted":True,
      "source_note":"Plantarctica original land extent is static 2017–2023; do not relabel it as annual greening. The publisher audit verified 277/357 pairs with matching citation and vantage; exact field days unknown. All original and strict 250km intervals include zero."
    }
    (a.out/"figure_source_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("MACRO_PAPER_FIGURE_RENDER_GATE="+json.dumps(receipt))

if __name__=="__main__":
    main()
