#!/usr/bin/env python3
"""Make source-verified noninferential manuscript figures for mina unified macroecology.

Figure1 UK/Irish country coverage and count-only positive proportions.
Figure2 species network-average concentration Y, not an observation-error CI.
Figure3 three separately scaled CR1 coefficient/CI panels, not comparable units.
No new models, tests, fitted effects, time windows or cohort selection.
"""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
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
MAIN=DATA/"network_species.csv"
META=OUT/"STEP6_JNCC_METHOD_QA.json"
INFER=OUT/"STEP4_FIXED_ASSOCIATIONS.json"
SOURCE_BLOB="e089c4525226c156a1554ce4f480a7611c946ae7"

def readcsv(p):
    with p.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def draw(path,fig):
    FIG.mkdir(exist_ok=True)
    for fmt in ("png","svg"):
        target=FIG/(path+"."+fmt)
        fig.savefig(target,format=fmt,dpi=180,bbox_inches="tight",
                    facecolor="white")
        if target.stat().st_size<2000:
            raise ValueError("Figure unexpectedly empty "+str(target))
    plt.close(fig)

def main():
    meta=json.loads(META.read_text())
    inference=json.loads(INFER.read_text())
    main=[r for r in readcsv(MAIN) if r["dataset_id"]=="JNCC"
          and r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    if len(main)!=663 or meta["complete_main"]["positive"]!=436:
        raise ValueError("Source cohort or original report changed")
    if sorted(inference["results"])!=["H3","H4D","H4W"]:
        raise ValueError("Frozen association results changed")
    # Table rather than an ecological plot of islands: Country is an admin label.
    bycountry=meta["stratified_original_outcome_descriptives"]["by_country"]
    countries=sorted(bycountry,key=lambda k:bycountry[k]["n_rows"])
    pos=np.array([bycountry[k]["positive"] for k in countries])
    neg=np.array([bycountry[k]["negative"] for k in countries])
    fig,ax=plt.subplots(figsize=(10.8,5.4))
    yp=np.arange(len(countries))
    ax.barh(yp,pos,label="Excess concentration > 0",height=.66,color="0.26")
    ax.barh(yp,neg,left=pos,label="Excess concentration < 0",height=.66,color="0.81")
    ax.set_yticks(yp,labels=countries)
    for i,k in enumerate(countries):
        v=bycountry[k]
        ax.text(v["n_rows"]+5,i,f"n={v['n_rows']}  ({v['fraction_positive']:.1%} positive)",
                va="center",fontsize=9)
    ax.set_xlim(0,560)
    ax.set_xlabel("Eligible network × species rows (not independent physical islands)")
    ax.set_title("JNCC geographical sample imbalance",loc="left",fontweight="bold")
    ax.legend(loc="lower right",frameon=False,fontsize=9)
    ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    draw("FIG1_COUNTRY_MONITORING_SUPPORT",fig)

    species_groups=defaultdict(list)
    for r in main:
        species_groups[r["species_id"]].append(float(r["concentration_excess_decade"]))
    means={k:float(np.mean(v)) for k,v in species_groups.items()}
    order=sorted(means,key=lambda k:means[k])
    ys=np.arange(len(order))
    vals=np.array([means[k] for k in order])
    fig,ax=plt.subplots(figsize=(10.8,7.8))
    ax.axvline(0,color="0.4",lw=1.1)
    ax.scatter(vals,ys,s=50,color="0.2",zorder=3)
    ax.hlines(ys,0,vals,color="0.65",lw=1.3,zorder=1)
    ax.set_yticks(ys,labels=[f"{sp}  (n={len(species_groups[sp])})" for sp in order],fontsize=9)
    ax.set_xlabel("Mean Y_excess / decade within each taxon's eligible networks")
    ax.set_title("Mean excess concentration across 17 monitored JNCC taxa",
                 loc="left",fontweight="bold")
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(axis="x",alpha=.15)
    fig.text(.04,.015,"Points show species means only. No observation-error confidence intervals are available.",
             fontsize=9)
    fig.tight_layout(rect=(0,.035,1,1))
    draw("FIG2_TAXON_CONCENTRATION",fig)

    data=inference["results"]
    rows=[("H3","SST change and concentration","Coefficient per +1 °C/decade"),
          ("H4D","Pair decline and overlap","Coefficient per +1 log-unit/decade decline"),
          ("H4W","SST change and overlap","Coefficient per +1 °C/decade")]
    fig,axes=plt.subplots(1,3,figsize=(13,4.0),sharey=False)
    for ax,(key,title,xlabel) in zip(axes,rows):
        v=data[key]
        ax.axvline(0,color="0.6",ls="--",lw=1)
        x=float(v["coef"]);lo=float(v["ci_low"]);hi=float(v["ci_high"])
        ax.errorbar(x,0,xerr=[[x-lo],[hi-x]],fmt="o",color="0.2",
                    ecolor="0.2",capsize=4,markersize=7,lw=1.5)
        margin=max(0.007,(hi-lo)*.25)
        ax.set_xlim(lo-margin,hi+margin)
        ax.set_ylim(-.5,.5)
        ax.set_yticks([])
        ax.set_xlabel(xlabel,fontsize=9)
        ax.set_title(title,fontsize=11,loc="left",fontweight="bold")
        ax.text(.03,.95,f"{key}: beta={x:+.4f}\nHolm p={v['holm_4']:.3f}\n{v['m']} network blocks",
                ha="left",va="top",transform=ax.transAxes,fontsize=9)
        ax.spines[["top","right","left"]].set_visible(False)
        ax.tick_params(axis="x",labelsize=9)
    fig.suptitle("Frozen H3/H4 associations: no Holm-supported directional effect",
                 fontsize=13,fontweight="bold")
    fig.text(.03,.01,"Point ± network-cluster CR1 95% CI. Separate axes and different predictor units; do not compare raw coefficients across panels.",
             fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.91))
    draw("FIG3_FIXED_ASSOCIATION_ESTIMATES",fig)

    figures=[]
    for stem in ("FIG1_COUNTRY_MONITORING_SUPPORT","FIG2_TAXON_CONCENTRATION",
                 "FIG3_FIXED_ASSOCIATION_ESTIMATES"):
        png=FIG/(stem+".png");svg=FIG/(stem+".svg")
        with Image.open(png) as im:
            width,height=im.size
            if width<1100 or height<500:
                raise ValueError("Figure raster dimensions unexpectedly small")
        figures.append(dict(stem=stem,png_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),
                            svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),
                            png_width=width,png_height=height))
    summary=dict(status="SOURCE_VERIFIED_DESCRIPTIVE_MANUSCRIPT_FIGURES",
        source_main_sha256=hashlib.sha256(MAIN.read_bytes()).hexdigest(),
        source_measurement_QA_sha256=hashlib.sha256(META.read_bytes()).hexdigest(),
        source_associations_QA_sha256=hashlib.sha256(INFER.read_bytes()).hexdigest(),
        sample_N=663,positive_N=436,species_count=len(means),
        no_new_inference=True,figures=figures)
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP6_FIGURES_QA.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    captions=[
        "# Figure captions v0.1 — source-locked descriptive outputs",
        "",
        "**Figure 1.** Original JNCC Country label × Master-site source comparison records by whether Y_excess was positive or negative. Bar lengths represent the 663 eligible species-network rows, not independent islands. The countries and counts are source-reported, and Scotland contributes 497/663 (75.0%).",
        "",
        "**Figure 2.** Mean excess inverse-Simpson concentration change per decade in 17 source JNCC taxa. Each point is the mean across that taxon's eligible network rows; parenthetical values are actual network sample sizes. These are not uncertainty intervals, calibrated observation-error effects or evidence that all breeding sites disappeared.",
        "",
        "**Figure 3.** Fixed H3, H4D and H4W regression coefficients and separate non-simultaneous network-cluster CR1 95% confidence intervals. All three four-test Holm-adjusted p-values fail the predefined positive-direction criterion. Axes have distinct units, scales and response definitions; dot magnitudes are not directly comparable. H2 remains unestimable, preserving its original multiplicity slot.",
        "",
        "Full source receipts: STEP6_FIGURES_QA.json, STEP6_JNCC_METHOD_QA.json and STEP4_FIXED_ASSOCIATIONS.json. These figures do not alter Step1 or Step4 hypotheses."
    ]
    (FIG/"FIGURE_CAPTIONS_V0_1.md").write_text("\n".join(captions)+"\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"figures":figures,
                      "n":summary["sample_N"],"positive":summary["positive_N"]},ensure_ascii=False))

if __name__=="__main__":
    main()
