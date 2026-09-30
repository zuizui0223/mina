"""Render the four integrated Palmer–Antarctic manuscript figures."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def rows(path:Path):
    with path.open("r",encoding="utf-8",newline="") as h:
        return list(csv.DictReader(h))


def save(fig,out:Path,stem:str):
    out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/f"{stem}.png",dpi=300,bbox_inches="tight")
    fig.savefig(out/f"{stem}.pdf",bbox_inches="tight")


def figure1(palmer:Path,out:Path):
    import matplotlib.pyplot as plt
    sites=rows(palmer/"figure1_sites.csv")
    traj=rows(palmer/"figure2_trajectories.csv")
    islands=["CHR","COR","HUM","LIT","TOR"]
    focal_names={"Christine Island","Cormorant Island","Humble Island","Litchfield Island","Torgersen Island"}
    focal_sites=[r for r in sites if r["site_name"] in focal_names]

    fig,axes=plt.subplots(1,2,figsize=(11.2,4.7))
    ax=axes[0]
    ax.scatter(
        [float(r["longitude"]) for r in focal_sites],
        [float(r["latitude"]) for r in focal_sites],
        marker="o",s=58,
    )
    for r in focal_sites:
        ax.annotate(
            r["site_name"].replace(" Island",""),
            (float(r["longitude"]),float(r["latitude"])),
            xytext=(4,3),textcoords="offset points",fontsize=7.5,
        )
    ax.set_xlabel("Longitude");ax.set_ylabel("Latitude")
    ax.set_title("A  Palmer breeding-island system")
    ax.grid(alpha=.2)

    ax=axes[1]
    for island in islands:
        local=[r for r in traj if r["island"]==island]
        ax.plot(
            [int(r["year"]) for r in local],
            [float(r["breeding_pairs"]) for r in local],
            marker="o",markersize=2.5,linewidth=1.1,label=island,
        )
    ax.set_yscale("symlog",linthresh=1)
    ax.set_xlabel("Year");ax.set_ylabel("Breeding pairs (symlog)")
    ax.set_title("B  Shared long-term decline, divergent endpoints")
    ax.legend(frameon=False,ncol=2,fontsize=8)
    fig.tight_layout()
    save(fig,out,"figure1_shared_decline")
    plt.close(fig)


def figure2(palmer:Path,out:Path):
    import matplotlib.pyplot as plt
    trajectories=rows(palmer/"figure3_concentration_trajectories.csv")
    slopes=rows(palmer/"figure3_concentration_slopes.csv")
    islands=("COR","HUM","LIT")
    fig,axes=plt.subplots(1,2,figsize=(11.2,4.7))

    for island in islands:
        local=[r for r in trajectories if r["island"]==island]
        axes[0].plot(
            [int(r["year"]) for r in local],
            [float(r["relative_to_first"]) for r in local],
            marker="o",markersize=2.8,linewidth=1.2,label=island,
        )
    axes[0].axhline(1.0,linewidth=.8)
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Effective colony number / first value")
    axes[0].set_title("A  Within-island concentration during decline")
    axes[0].legend(frameon=False)

    y=np.arange(len(slopes))
    observed=np.asarray([float(r["observed_slope"]) for r in slopes])
    means=np.asarray([float(r["null_mean_slope_cv20"]) for r in slopes])
    lower=np.asarray([float(r["null_q025_slope_cv20"]) for r in slopes])
    upper=np.asarray([float(r["null_q975_slope_cv20"]) for r in slopes])
    xerr=np.vstack([means-lower,upper-means])
    axes[1].errorbar(means,y,xerr=xerr,fmt="o",capsize=3,label="CV20 null (95%)")
    axes[1].scatter(observed,y,marker="D",s=50,label="Observed")
    axes[1].axvline(0,linewidth=.8)
    axes[1].set_yticks(y,[r["island"] for r in slopes]);axes[1].invert_yaxis()
    axes[1].set_xlabel("N_eff slope per year")
    axes[1].set_title("B  Concentration exceeds fixed-composition null")
    axes[1].legend(frameon=False,fontsize=8)
    fig.tight_layout()
    save(fig,out,"figure2_palmer_concentration")
    plt.close(fig)


def figure3(data:Path,out:Path):
    import matplotlib.pyplot as plt
    spp=rows(data/"figure3_species_interactions.csv")
    null=rows(data/"figure3_paper_level_null.csv")[0]
    species_names={"ADPE":"Adélie","CHPE":"Chinstrap","GEPE":"Gentoo"}
    labels=[species_names.get(r["species_id"],r["species_id"]) for r in spp]
    values=np.asarray([float(r["gamma_ah"]) for r in spp])
    y=np.arange(len(spp))

    fig,axes=plt.subplots(1,2,figsize=(10.8,4.5))
    axes[0].scatter(values,y,marker="D",s=55)
    axes[0].axvline(0,linewidth=.8)
    axes[0].set_yticks(y,labels);axes[0].invert_yaxis()
    axes[0].set_xlabel(r"$\gamma_{AH}$")
    axes[0].set_title("A  Species-specific interaction")
    for i,r in enumerate(spp):
        axes[0].text(
            .98,i,
            f"raw p={float(r['raw_p_value']):.3f}; Holm={float(r['holm_p_value']):.3f}",
            transform=axes[0].get_yaxis_transform(),
            ha="right",va="center",fontsize=7,
        )

    obs=float(null["observed_median_gamma_ah"])
    q01=float(null["null_q01"]);q05=float(null["null_q05"])
    med=float(null["null_median"]);q95=float(null["null_q95"]);q99=float(null["null_q99"])
    axes[1].hlines(0,q01,q99,linewidth=2)
    axes[1].hlines(0,q05,q95,linewidth=8,alpha=.35)
    axes[1].scatter([med],[0],s=45,label="Null median")
    axes[1].scatter([obs],[0],marker="D",s=70,label="Observed median")
    axes[1].axvline(0,linewidth=.8)
    axes[1].set_yticks([])
    axes[1].set_xlabel(r"Cross-species median $\gamma_{AH}$")
    axes[1].set_title("B  Frozen 9,999-permutation null")
    axes[1].legend(frameon=False,fontsize=8,loc="upper left")
    axes[1].text(
        .02,.12,
        f"one-sided p={float(null['permutation_p']):.4f}",
        transform=axes[1].transAxes,fontsize=9,
    )
    fig.tight_layout()
    save(fig,out,"figure3_antarctic_interaction")
    plt.close(fig)


def figure4(data:Path,out:Path):
    import matplotlib.pyplot as plt
    scale=rows(data/"figure4_scale_sensitivity.csv")
    power=rows(data/"figure4_detectable_effect.csv")

    fig,axes=plt.subplots(1,2,figsize=(11.0,4.5))
    rich=[r for r in scale if r["metric"]=="tier2_richness"]
    rich=sorted(rich,key=lambda r:int(r["radius_m"]))
    x=[int(r["radius_m"])/1000 for r in rich]
    y=[float(r["median_gamma_ah"]) for r in rich]
    axes[0].plot(x,y,marker="o",linewidth=1.3)
    axes[0].axhline(0,linewidth=.8)
    axes[0].set_xticks(x,[f"{v:g} km" for v in x])
    axes[0].set_ylabel(r"Cross-species median $\gamma_{AH}$")
    axes[0].set_title("A  Radius sensitivity")
    axes[0].text(
        .03,.06,"joint sign-switch + contrast null p=0.081",
        transform=axes[0].transAxes,fontsize=8,
    )

    xx=[float(r["abs_truth_gamma_ah"]) for r in power]
    yy=[float(r["detection_fraction"]) for r in power]
    lo=[float(r["wilson_low"]) for r in power]
    hi=[float(r["wilson_high"]) for r in power]
    order=np.argsort(xx)
    xx=np.asarray(xx)[order];yy=np.asarray(yy)[order]
    lo=np.asarray(lo)[order];hi=np.asarray(hi)[order]
    axes[1].plot(xx,yy,marker="o",linewidth=1.3)
    axes[1].fill_between(xx,lo,hi,alpha=.15)
    axes[1].axhline(.8,linewidth=.8,linestyle="--")
    axes[1].axhline(.9,linewidth=.8,linestyle="--")
    axes[1].axvline(.31822603579776854,linewidth=1.0,linestyle="--")
    axes[1].axvline(.49765625,linewidth=.8,linestyle=":")
    axes[1].axvline(.5385714285714286,linewidth=.8,linestyle=":")
    axes[1].set_ylim(-.02,1.02)
    axes[1].set_xlabel(r"True common $|\gamma_{AH}|$")
    axes[1].set_ylabel("Detection probability")
    axes[1].set_title("B  Retrospective detectability")
    axes[1].text(
        .03,.06,"observed=0.318; MDE80=0.498; MDE90=0.539",
        transform=axes[1].transAxes,fontsize=8,
    )
    fig.tight_layout()
    save(fig,out,"figure4_limits_of_transfer")
    plt.close(fig)


def main()->int:
    import matplotlib
    matplotlib.use("Agg")
    p=argparse.ArgumentParser()
    p.add_argument("--palmer-data",required=True,type=Path)
    p.add_argument("--integrated-data",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    figure1(a.palmer_data,a.out_dir)
    figure2(a.palmer_data,a.out_dir)
    figure3(a.integrated_data,a.out_dir)
    figure4(a.integrated_data,a.out_dir)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
