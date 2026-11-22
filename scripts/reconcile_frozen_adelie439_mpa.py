#!/usr/bin/env python3
"""Reproduce the frozen 439/85 panel from pinned PR #214, then map descriptive winter polynya variation.
Absolutely no new biological response fit. Two distinct source stages remain traceable.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Geod, Transformer
from shapely.geometry import Polygon, shape
from shapely.ops import transform, unary_union

FROZEN_PR_COMMIT="c67e55c9f4f657ef308c02a85c6ff366dce8e1f4"
BLOBS={
 "matched_isotope860.csv":"66184a09576297aea12f408fffc524185a3671f2",
 "polynya_physical860.csv":"5b3d79f65738cb2474c2c7f437cefa81010713c5",
 "colony_geography.csv":"5662badeedd43bc8e2dacbfdfc157f8d4fdf9a69",
}
KEYS=["site_id","season"]
POLY="direct_DEEPAA_coastal_polynya_fraction"
REGION="source_region"
def git_blob_sha(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def check(x,message):
    if not bool(x):raise ValueError("AUDIT STOP: "+message)
def geodesic_buffer(lon,lat):
    geod=Geod(ellps="WGS84")
    azimuth=np.arange(0.,360.,1.5)
    lo,la,_=geod.fwd(np.full(azimuth.shape,lon),np.full(azimuth.shape,lat),
                     azimuth,np.full(azimuth.shape,100000.0))
    geom=Polygon(zip(lo,la))
    trans=Transformer.from_crs(4326,6932,always_xy=True)
    return transform(trans.transform,geom)
def paint_poly(ax,g,color,linewidth=1,alpha=.9):
    if g.geom_type=="Polygon":items=[g]
    else:items=list(g.geoms)
    for polygon in items:
        xy=np.asarray(polygon.exterior.coords)
        ax.plot(xy[:,0]/1e6,xy[:,1]/1e6,color=color,lw=linewidth,alpha=alpha,zorder=2)
def main(args):
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    p=Path(args.source)
    for name,sha in BLOBS.items():
        path=p/name
        check(path.exists(),"frozen original input missing "+name)
        check(git_blob_sha(path)==sha,"GitHub blob drift in "+name)
    iso=pd.read_csv(p/"matched_isotope860.csv")
    phy=pd.read_csv(p/"polynya_physical860.csv")
    geo=pd.read_csv(p/"colony_geography.csv")
    for tag,df in [("isotope860",iso),("physical860",phy)]:
        check((len(df),df.site_id.nunique(),df[REGION].nunique())==(860,88,13),tag+" original 860/88/13 changed")
        check(not df.duplicated(KEYS).any(),tag+" duplicate key")
    joined=iso.merge(phy[KEYS+[REGION,POLY]],on=KEYS,suffixes=("","_physical"),validate="one_to_one")
    check(len(joined)==860 and joined[REGION].equals(joined[REGION+"_physical"]),
          "original physics and optical source mismatch")
    frozen=joined.loc[joined[POLY].notna()].copy().reset_index(drop=True)
    check((len(frozen),frozen.site_id.nunique(),frozen[REGION].nunique())==(439,85,11),
          "original frozen support not 439/85/11")
    check(sorted(frozen.season.unique())==list(range(2004,2011)),"original frozen years changed")
    check((frozen[POLY]>=0).all(),"negative polynya fraction")
    check((frozen[POLY].eq(0)).sum()==34,"original zero-polynya count changed")
    check(abs(frozen[POLY].mean()*100-7.03)<.03,"mean exposure does not reproduce manuscript")
    check(abs(frozen[POLY].std()*100-6.32)<.03,"SD exposure does not reproduce manuscript")
    # Match source pixel stage (author rule) by keys, not the erroneous 4-year site screen.
    a=pd.read_csv(args.original_author)
    check((len(a),a.site_id.nunique())==(583,113),"original author source 583/113 changed")
    check(not a.duplicated(KEYS).any(),"original 583 duplicate site/year")
    akeys=set(map(tuple,a[KEYS].itertuples(index=False,name=None)))
    m=iso.loc[iso.season.between(2004,2010)].copy()
    mkeys=set(map(tuple,m[KEYS].itertuples(index=False,name=None)))
    fkeys=set(map(tuple,frozen[KEYS].itertuples(index=False,name=None)))
    # Save diagnoses even for unexpected source-stage mismatch; errors should not be silently reconciled.
    missing_from_raw=sorted(fkeys-akeys)
    extra_in_2004_matched=sorted(mkeys-akeys)
    stages=a.merge(m[KEYS],on=KEYS,how="left",indicator=True,validate="one_to_one")
    stages["matched_iso860_source"]=stages["_merge"].eq("both")
    stages=stages.drop(columns="_merge")
    stages=stages.merge(frozen[KEYS+[POLY]],on=KEYS,how="left",validate="one_to_one")
    stages["frozen439"]=stages[POLY].notna()
    stages["why_not_439"]=np.where(stages.frozen439,"included_frozen_439",
                         np.where(~stages.matched_iso860_source,
                             "no_860_environment_optical_match",
                             "winter_exposure_missing_in_frozen_physical"))
    stages.to_csv(output/"source_583_to_frozen_439_exact_key_crosswalk.csv",index=False)
    check(not missing_from_raw, "frozen 439 keys missing from RDS author source: "+str(missing_from_raw[:10]))
    check(not extra_in_2004_matched, "matched 860 selected keys outside published RDS source: "+str(extra_in_2004_matched[:10]))
    check(int(stages.frozen439.sum())==439,"583->439 key lineage failed")
    # Authoritative author-derivation geography (not pixel-estimated point centroids).
    geos=geo.loc[geo.radius_km.eq(100)].copy()
    check(not geos.duplicated("site_id").any(),"duplicated 100-km geographic centroids")
    check(set(frozen.site_id).issubset(set(geos.site_id)),"unmapped 439 colony")
    check(geos.colony_lat.between(-90,-60).all(),"colony latitude range")
    frozen=frozen.merge(geos[["site_id","colony_lat","colony_lon"]],on="site_id",
                        validate="many_to_one")
    frozen.sort_values(KEYS).to_csv(output/"frozen439_original_values_geocoded.csv",index=False)
    groups=frozen.groupby("site_id").agg(
        source_region=(REGION,"first"),n_valid_winters=("season","nunique"),
        lat=("colony_lat","first"),lon=("colony_lon","first"),
        mean_exposure=(POLY,"mean"),sd_exposure=(POLY,"std"),
        min_exposure=(POLY,"min"),max_exposure=(POLY,"max"),
        n_source_pixels=("n_source_pixels","sum"),n_observed_days=("n_observed_days","sum")
    ).reset_index()
    groups["mean_pp"]=groups.mean_exposure*100
    groups["sd_pp"]=groups.sd_exposure*100
    groups["sd_reliable_4y"]=groups.n_valid_winters>=4
    groups.loc[~groups.sd_reliable_4y,"sd_pp"]=np.nan
    # CCAMLR designated, not proposed, MPA polygon, official EPSG:6932.
    mpa_json=json.loads(Path(args.mpa).read_text())
    check(mpa_json.get("type")=="FeatureCollection" and
          len(mpa_json.get("features",[]))==6 and "6932" in str(mpa_json.get("crs")),
          "official MPA GeoJSON does not match EPSG6932 six zones")
    zgeom={f["properties"]["GAR_Short_Label"]:shape(f["geometry"]) for f in mpa_json["features"]}
    check(set(zgeom)=={"GPZi","GPZii","GPZiii","KRZ","SRZ","SOSS"},
          "MPA zones changed")
    combined=unary_union(list(zgeom.values()))
    overlays=[]
    for site in groups.itertuples(index=False):
        c=geodesic_buffer(site.lon,site.lat)
        row={"site_id":site.site_id,
             "current_mpa_union_intersection_100km_km2":float(c.intersection(combined).area/1e6),
             "current_mpa_union_intersection_100km_pct_full_circle":
                 float(100*c.intersection(combined).area/c.area)}
        for lab,g in zgeom.items():
            row["mpa_"+lab+"_100km_intersection_km2"]=float(c.intersection(g).area/1e6)
        overlays.append(row)
    groups=groups.merge(pd.DataFrame(overlays),on="site_id",validate="one_to_one")
    groups["mpa_intersect"]=groups.current_mpa_union_intersection_100km_km2>0
    groups.to_csv(output/"frozen85_site_variation_and_ccamlr_mpa.csv",index=False)
    # Full 85-site map, sites with less than 4 winter observations clearly unranked.
    fig,ax=plt.subplots(figsize=(10,9),dpi=145)
    trans=Transformer.from_crs(4326,6932,always_xy=True)
    for lat in (-60,-65,-70,-75,-80,-85):
        L=np.linspace(-180,180,361)
        X,Y=trans.transform(L,np.full_like(L,float(lat)))
        ax.plot(np.asarray(X)/1e6,np.asarray(Y)/1e6,color="gray",lw=.6,alpha=.26,zorder=1)
    for lab,g in zgeom.items():
        paint_poly(ax,g,color="#29303b",linewidth=1.1)
        c=g.representative_point()
        ax.text(c.x/1e6,c.y/1e6,lab,fontsize=7,ha="center",va="center",
                color="#343a44",fontweight="bold",zorder=3)
    xs,ys=trans.transform(groups.lon.to_numpy(),groups.lat.to_numpy())
    x=np.asarray(xs)/1e6;y=np.asarray(ys)/1e6
    use=groups.sd_reliable_4y.to_numpy()
    values=groups.sd_pp.to_numpy(float)
    if use.any():
        scatter=ax.scatter(x[use],y[use],c=values[use],cmap="viridis",
                           s=51,edgecolors="white",linewidths=.6,zorder=4)
        cb=fig.colorbar(scatter,ax=ax,fraction=.044,pad=.02,shrink=.82)
        cb.set_label("Within-site SD of winter coastal-polynya fraction (pp)",fontsize=8)
    if (~use).any():
        ax.scatter(x[~use],y[~use],c="gray",marker="x",s=32,
                   label="Fewer than 4 observed winters (not ranked)",zorder=4)
        ax.legend(loc="lower left",fontsize=8)
    ax.set_xlim(-3.55,3.55);ax.set_ylim(-3.55,3.55)
    ax.set_aspect("equal")
    ax.set_xlabel("Antarctic equal-area projected x (million m)")
    ax.set_ylabel("Antarctic equal-area projected y (million m)")
    ax.set_title("Frozen 85 Adélie colonies: winter coastal-polynya exposure variability\nand current designated CCAMLR marine protected areas",fontsize=11)
    fig.text(.5,.012,"Frozen manuscript cohort: 439 colony-seasons (2004–2010). Variability of exposure, NOT dietary sensitivity.\n"
             "Current MPA geography (Ross Sea designated 2016) is not historical protection of 2004–2010 observations.",
             ha="center",fontsize=7.5)
    fig.tight_layout(rect=(0,.055,1,1))
    fig.savefig(output/"FROZEN_85_polynya_variation_designated_MPA.png",bbox_inches="tight",dpi=200)
    fig.savefig(output/"FROZEN_85_polynya_variation_designated_MPA.svg",bbox_inches="tight")
    plt.close(fig)
    labelled=groups.loc[groups.sd_reliable_4y].copy()
    report={
        "status":"FROZEN_439_85_REPRODUCED_INDEPENDENTLY_FROM_PINNED_PR214_SOURCE",
        "original_commit":FROZEN_PR_COMMIT,
        "source_files_verified_blobs":BLOBS,
        "original_iso860":{"n":len(iso),"sites":iso.site_id.nunique(),"regions":iso[REGION].nunique()},
        "original_matched860_years2004_2010":{"n":len(m),"sites":m.site_id.nunique()},
        "author_source_583":{"n":len(a),"sites":a.site_id.nunique()},
        "frozen":{"n":len(frozen),"sites":frozen.site_id.nunique(),"regions":frozen[REGION].nunique(),
           "observed_years":sorted(frozen.season.unique().tolist()),
           "zero_polynya_records":int(frozen[POLY].eq(0).sum()),
           "polynya_pct_mean":float(100*frozen[POLY].mean()),
           "polynya_pct_sd":float(100*frozen[POLY].std(ddof=1))},
        "lineage":{"full_source_site_years_not_in_frozen":len(a)-len(frozen),
           "excluded_before_matched_environment_panel":int((~stages.matched_iso860_source).sum()),
           "excluded_at_winter_polynya_exposure":int((stages.matched_iso860_source&~stages.frozen439).sum()),
           "source_sites_not_in_final":len(set(a.site_id)-set(frozen.site_id)),
           "matched_years_outside_author_support":len(extra_in_2004_matched),
           "frozen_keys_missing_from_author_support":len(missing_from_raw)},
        "site_summary":{"n_sites":len(groups),
            "n_with_4_or_more_winter_records":int(groups.sd_reliable_4y.sum()),
            "median_sd_pp_reliable":float(labelled.sd_pp.median()),
            "mean_sd_pp_reliable":float(labelled.sd_pp.mean()),
            "n_sites_100km_overlap_designated_current_mpa":int(groups.mpa_intersect.sum()),
            "n_reliable_sites_overlap":int((groups.sd_reliable_4y&groups.mpa_intersect).sum()),
            "median_sd_pp_reliable_overlap":float(labelled.loc[labelled.mpa_intersect,"sd_pp"].median()) if labelled.mpa_intersect.any() else None,
            "median_sd_pp_reliable_nonoverlap":float(labelled.loc[~labelled.mpa_intersect,"sd_pp"].median()) if (~labelled.mpa_intersect).any() else None},
        "restrictions":["No model fitting; source-only variability descriptive",
          "MPA circle intersection not the protected share of foraging habitat; full geodesic 100km disc",
          "MPA current geometry, designated Ross Sea 2016, after 2004–2010",
          "Sites with <4 observed winters unranked for SD; included visibly as grey crosses",
          "Current MPA overlap cannot be interpreted causally; geography and observation support confound"],
    }
    (output/"frozen439_85_reconciliation_receipt.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    print(json.dumps(report,indent=2,default=str))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,help="Path to PR214 pinned source_inputs")
    p.add_argument("--original-author",required=True,help="583 Youngflesh original source support rows")
    p.add_argument("--mpa",required=True,help="CCAMLR current designated EPSG6932 GeoJSON")
    p.add_argument("--output",required=True)
    main(p.parse_args())
