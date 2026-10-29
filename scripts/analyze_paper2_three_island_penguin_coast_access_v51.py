#!/usr/bin/env python3
"""Paper2 V51: physical-island coast-to-nest distance from original BAS penguins.

Uses existing immutable V26 BAS nest-point/independent DEM NPZ, GSHHG 2.3.7
full-resolution original coastline; no new bird extraction, rat statuses or
flying-guild effects. Nested four true source localities, three independent
candidate coastline polygons, source geographic eligibility before new
Adelie/Chinstrap island-heldout coastal access predictive stress test.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib,io,json,math,zipfile
from pathlib import Path, PurePosixPath

import numpy as np
import requests
import shapefile
from shapely.geometry import Point,shape
from shapely.ops import transform
from shapely import points, distance
from pyproj import Transformer
from sklearn.linear_model import LogisticRegression

SOURCE_NPZ="BAS_HART_PUBLIC_GLO30_NEST_TERRAIN_V26.npz"
SOURCE_NPZ_SHA="1566f4fef4ac5370f40f6482e9f76f7b252e32ade8915a190cf0d2fc946883ec"
SOURCE_NPZ_EXPECTED={"Ashen_Hills":77583,"Bellingshausen":14435,"Beach_Point":7683,"Hewison_Point":22438}
ORIGINAL_LOCALITIES=tuple(SOURCE_NPZ_EXPECTED)
PARENT={"Ashen_Hills":"Saunders","Bellingshausen":"Bellingshausen","Beach_Point":"Thule","Hewison_Point":"Thule"}
SPECIES=("ADELIE","CHINSTRAP","GENTOO","MACARONI")
GSHHG_URL="https://github.com/GenericMappingTools/gshhg-gmt/releases/download/2.3.7/gshhg-shp-2.3.7.zip"
GSHHG_SHA="8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41"
STEM="GSHHS_f_L1"
MAX_GSHHG_BYTES=200_000_000
MAX_UNCOMPRESSED_ONE=700_000_000
ROI=(-29.,-61.,-24.,-56.) # longitude/min latitude/source envelope, WGS84
D_GRID_M=30.
MAX_ISLAND_KM2=1000.
MIN_ISLAND_KM2=.02
MIN_INSIDE_SOURCE=.95
MIN_VALID_TERRAIN=.95
MIN_LABELLED_PER_SITE=100
FIXED_C=.3
MIN_ISLANDS_IMPROVED=2
MIN_EQUAL_ISLAND_GAIN=.005

WGS84_TO_UTM=Transformer.from_crs(4326,32726,always_xy=True)
UTM_TO_WGS84=Transformer.from_crs(32726,4326,always_xy=True)

def read_original_npz(path:Path):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_NPZ_SHA:
        raise ValueError("SOURCE_ORIGINAL_BAS_V26_NPZ_SHA_MISMATCH")
    arrays=np.load(io.BytesIO(raw),allow_pickle=False)
    expected={f"{site}_{suffix}" for site in ORIGINAL_LOCALITIES
              for suffix in ("xy","label","DEM_elevation_m","DEM_slope_degrees")}
    if set(arrays.files)!=expected:
        raise ValueError("SOURCE_BAS_V26_ORIGINAL_KEYS_CHANGED")
    data={}
    for site,n in SOURCE_NPZ_EXPECTED.items():
        xy=np.asarray(arrays[site+"_xy"],dtype=np.float64)
        labels=np.asarray(arrays[site+"_label"],dtype=np.uint8)
        el=np.asarray(arrays[site+"_DEM_elevation_m"],dtype=float)
        sl=np.asarray(arrays[site+"_DEM_slope_degrees"],dtype=float)
        if (xy.shape!=(n,2) or labels.shape!=(n,) or
            el.shape!=(n,) or sl.shape!=(n,)):
            raise ValueError("SOURCE_BAS_V26_ORIGINAL_LOCALITY_ROWS_DRIFT:"+site)
        if (not np.isfinite(xy).all() or
            not np.isin(labels,list(range(len(SPECIES)))).all()):
            raise ValueError("ORIGINAL_NEST_COORDINATE_OR_TAXON_INVALID")
        if np.isnan(el).mean()>.05 or np.isnan(sl).mean()>.05 or (
            np.nanmin(sl)<0 or np.nanmax(sl)>90):
            raise ValueError("SOURCE_BAS_V26_NEST_DEM_QA_DRIFT")
        _,reverse,nocc=np.unique(xy,axis=0,return_inverse=True,return_counts=True)
        keep=nocc[reverse]==1
        if np.mean(~keep)>=.1:
            raise ValueError("SOURCE_BAS_V27_DUPLICATE_NEST_REJECTION_GATE")
        data[site]={"xy":xy[keep],"label":labels[keep],"elev":el[keep],"slope":sl[keep],
                    "total_original_rows":n,"original_collision_rows_excluded":int(np.sum(~keep))}
    if sum(x["total_original_rows"] for x in data.values())!=122139:
        raise ValueError("SOURCE_BAS_ORIGINAL_TOTAL_DRIFT")
    return data,{"original_2019_20_bird_nest_rows":122139,
                 "derived_V26_original_NPZ_sha256":SOURCE_NPZ_SHA,
                 "duplicate_source_nest_coordinates_excluded_n":{
                     k:v["original_collision_rows_excluded"] for k,v in data.items()},
                 "original_country_or_physical_island_replicates":3,
                 "same_actual_4_BAS_source_localities":list(ORIGINAL_LOCALITIES),
                 "all_original_NPZ_bird_species_are_flightless_penguins":True}


def download_original_coast():
    with requests.get(GSHHG_URL,stream=True,timeout=(20,120),
                      headers={"User-Agent":"mina-original-physical-coast-to-bird-nests-v51/1.0"}) as resp:
        resp.raise_for_status()
        from urllib.parse import urlparse
        final=urlparse(resp.url)
        if final.scheme!="https" or not(
            final.hostname=="github.com"
            or final.hostname.endswith(".githubusercontent.com")
            or final.hostname.endswith(".github.com")):
            raise ValueError("ORIGINAL_GSHHG_SOURCE_NOT_OFFICIAL_GITHUB_RELEASE")
        buf=bytearray()
        for part in resp.iter_content(chunk_size=1024*1024):
            if not part:continue
            buf.extend(part)
            if len(buf)>MAX_GSHHG_BYTES:
                raise ValueError("SOURCE_GSHHG_ZIP_SIZE_LIMIT")
    content=bytes(buf)
    if hashlib.sha256(content).hexdigest()!=GSHHG_SHA:
        raise ValueError("ORIGINAL_GSHHG_PUBLISHER_ZIP_SHA_CHANGED")
    return content


def read_original_full_coast_shapes(raw:bytes,reference_medians):
    if raw[:2]!=b"PK":
        raise ValueError("ORIGINAL_GSHHG_NOT_ZIP")
    with zipfile.ZipFile(io.BytesIO(raw)) as arc:
        for entry in arc.infolist():
            p=PurePosixPath(entry.filename)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("UNSAFE_GSHHG_ARCHIVE_PATH")
        files={}
        for ext in (".shp",".shx",".dbf"):
            matches=[z for z in arc.infolist()
                     if PurePosixPath(z.filename).name==STEM+ext]
            if len(matches)!=1:
                raise ValueError("ORIGINAL_GSHHS_FULL_SOURCE_FILE_MISSING:"+ext)
            if matches[0].file_size>MAX_UNCOMPRESSED_ONE:
                raise ValueError("ORIGINAL_GSHHG_ZIP_ENTRY_TOO_LARGE")
            files[ext]=arc.read(matches[0])
    reader=shapefile.Reader(
        shp=io.BytesIO(files[".shp"]),shx=io.BytesIO(files[".shx"]),
        dbf=io.BytesIO(files[".dbf"]))
    medians={k:Point(v[0],v[1]) for k,v in reference_medians.items()}
    matched={k:[] for k in medians}
    n_bbox=0
    for sr in reader.iterShapeRecords(bbox=ROI):
        n_bbox+=1
        shp=sr.shape
        if not shp.bbox:continue
        xmin,ymin,xmax,ymax=shp.bbox
        eligible=[k for k,pt in medians.items()
                  if xmin<=pt.x<=xmax and ymin<=pt.y<=ymax]
        if not eligible:continue
        obj=shape(shp.__geo_interface__)
        if obj.is_empty or not obj.is_valid:
            raise ValueError("ORIGINAL_GSHHG_LAND_CANDIDATE_POLYGON_INVALID")
        rec=sr.record.as_dict()
        sid=rec.get("id") or rec.get("ID")
        if sid is None:
            raise ValueError("GSHHG_SOURCE_POLYGON_ID_MISSING")
        for k in eligible:
            if obj.contains(medians[k]):
                matched[k].append((str(sid),obj))
    if any(len(items)!=1 for items in matched.values()):
        raise ValueError("GSHHG_ORIGINAL_ISLAND_UNIQUE_POINT_IN_LAND_SUPPORT_FAIL:"+str(
            {k:len(v) for k,v in matched.items()}))
    ids={k:v[0][0] for k,v in matched.items()}
    if len(set(ids.values()))!=3:
        raise ValueError("SOURCE_THREE_CANDIDATE_ISLANDS_NOT_THREE_POLYGONS")
    island_shapes={}
    landarea={}
    for k,pairs in matched.items():
        utm=transform(WGS84_TO_UTM.transform,pairs[0][1])
        km2=float(utm.area/1e6)
        if utm.is_empty or not utm.is_valid or not(MIN_ISLAND_KM2<=km2<=MAX_ISLAND_KM2):
            raise ValueError("SOURCE_GSHHG_ACTUAL_SMALL_ISLAND_AREA_GATE_FAIL")
        island_shapes[k]=utm
        landarea[k]=km2
    return island_shapes,{
        "original_GSHHG_SHA256":GSHHG_SHA,
        "original_layer":"GSHHS_f_L1",
        "original_full_resolution_L1_polygons_in_ROI":n_bbox,
        "original_GSHHG_source_ids_for_three_coast_islands":ids,
        "original_projected_island_land_area_km2":landarea,
        "original_three_independently_mapped_physical_coast_islands":3,
        "original_nest_GPS_measured_breeding_coastline_NOT_proven":True
    }


def coast_distance_for_locs(data,island_shapes):
    from shapely import contains_xy
    access={}
    geographic={}
    for site,d in data.items():
        coast=island_shapes[PARENT[site]]
        xy=d["xy"]
        inside=contains_xy(coast,xy[:,0],xy[:,1])
        if float(np.mean(inside))<MIN_INSIDE_SOURCE:
            raise ValueError("ORIGINAL_GSHHG_SOURCE_NESTS_OUTSIDE_ISLAND_GATE:"+site)
        # One coastline distance per independent 30m cell, backproject to
        # exactly corresponding source nest. Max local quantization 21.22m.
        pixel=np.floor(xy/D_GRID_M).astype(np.int64)
        unique,rev=np.unique(pixel,axis=0,return_inverse=True)
        cent=unique*D_GRID_M+D_GRID_M/2
        boundary=coast.boundary
        distances=np.asarray(distance(points(cent[:,0],cent[:,1]),boundary),dtype=float)
        pernest=distances[rev]
        if not np.isfinite(pernest).all():
            raise ValueError("ORIGINAL_COAST_GEOMETRY_DISTANCE_NONFINITE:"+site)
        elev=d["elev"];sl=d["slope"]
        good=inside & np.isfinite(elev)&np.isfinite(sl)&np.isfinite(pernest)
        if np.mean(good)<MIN_VALID_TERRAIN:
            raise ValueError("SOURCE_COAST_AND_TERRAIN_COMPLETE_NEST_SUPPORT_FAIL:"+site)
        access[site]={"D_coast":pernest,"keep":good}
        # Site observations are species-nest samples, NOT independent islands.
        bysp={}
        for code,name in enumerate(SPECIES):
            use=good&(d["label"]==code)
            if not np.any(use):continue
            distance_km=pernest[use]
            bysp[name]={
                "source_distinct_original_nest_positions_n":int(np.sum(use)),
                "D_coast_30m_grid_m_q05_median_q95":[
                    float(x) for x in np.quantile(distance_km,[.05,.50,.95])],
                "source_mapped_DEM_slope_median_degrees":float(np.median(sl[use])),
            }
        geographic[site]={
            "source_candidate_physical_island":PARENT[site],
            "source_original_unique_nest_coordinate_n":len(xy),
            "strict_original_source_nest_points_inside_f_L1_polygon_n":int(inside.sum()),
            "source_polygon_interior_fraction":float(np.mean(inside)),
            "source_nest_geographic_and_terrain_valid_fraction":float(np.mean(good)),
            "source_30m_grid_centres_at_unique_nest_cells_n":len(unique),
            "max_distance_quantization_error_bound_m":D_GRID_M*math.sqrt(2)/2,
            "by_original_penguin_taxon":bysp,
        }
    return access,geographic


def balanced_brier(y,p):
    y=np.asarray(y,dtype=np.uint8);p=np.asarray(p,dtype=float)
    return .5*float(np.mean(p[y==0]**2))+.5*float(np.mean((1-p[y==1])**2))


def train_fold_scaled(xtrain,xtest):
    midpoint=np.median(xtrain,axis=0)
    q=np.percentile(xtrain,[25,75],axis=0)
    scale=np.where(q[1]-q[0]>1e-7,q[1]-q[0],1.)
    return (xtrain-midpoint)/scale,(xtest-midpoint)/scale


def source_heldout_predictive_qa(data,access):
    # Source V27 compares ADELIE vs CHINSTRAP only (both on all 3 source islands).
    groups=sorted(set(PARENT.values()))
    site={}
    for name in ORIGINAL_LOCALITIES:
        x=data[name]
        a=access[name]
        mask=a["keep"] & np.isin(x["label"],[0,1])
        if not np.any(mask):
            raise ValueError("SOURCE_BINARY_PENGUIN_PANEL_EMPTY")
        xx=np.column_stack((x["elev"][mask],x["slope"][mask],
                             np.log1p(a["D_coast"][mask])))
        yy=x["label"][mask]
        if np.sum(yy==0)<MIN_LABELLED_PER_SITE or np.sum(yy==1)<MIN_LABELLED_PER_SITE:
            raise ValueError("ORIGINAL_V27_TWO_SPECIES_PER_SITE_SUPPORT_NOT_PRESERVED")
        site[name]={"X":xx,"y":yy}
    held={}
    for omitted in groups:
        train_sites=[k for k in ORIGINAL_LOCALITIES if PARENT[k]!=omitted]
        test_sites=[k for k in ORIGINAL_LOCALITIES if PARENT[k]==omitted]
        Xtrain=np.vstack([site[k]["X"] for k in train_sites])
        ytrain=np.concatenate([site[k]["y"] for k in train_sites])
        train_weights=[]
        for key in train_sites:
            y=site[key]["y"]
            # Same geographic source-island/site/taxon balancing as original V27
            within_island_n=sum(PARENT[z]==PARENT[key] for z in train_sites)
            weights=np.empty(len(y),dtype=float)
            for code in (0,1):
                group=(y==code)
                weights[group]=.5/(within_island_n*np.sum(group))
            train_weights.append(weights)
        w=np.concatenate(train_weights)
        w/=np.mean(w)
        if not np.all(w>0) or len(np.unique(ytrain))!=2:
            raise ValueError("V51_TRAIN_SOURCE_WEIGHTS_OR_SOURCE_TAXA_INVALID")
        island_results={}
        for features,key in ((2,"B1_elevation_slope"),(3,"B2_plus_coastal_access")):
            Xt,unused=train_fold_scaled(Xtrain[:,:features],Xtrain[:,:features])
            estimator=LogisticRegression(C=FIXED_C,solver="lbfgs",max_iter=500)
            estimator.fit(Xt,ytrain,sample_weight=w)
            for source_site in test_sites:
                Xm=site[source_site]["X"][:,:features]
                y=site[source_site]["y"]
                xtrain_scaled,xm_scaled=train_fold_scaled(Xtrain[:,:features],Xm)
                # One model fitted with training-only scaler; recomputing here
                # uses exact same Xtrain and cannot access heldout ecology labels.
                if not np.allclose(Xt,xtrain_scaled):
                    raise ValueError("TRAIN_TRANSFORM_DRIFT")
                pred=estimator.predict_proba(xm_scaled)[:,1]
                island_results.setdefault(source_site,{})[key]=balanced_brier(y,pred)
                island_results[source_site]["original_nest_source_n"]=len(y)
        b1=float(np.mean([island_results[k]["B1_elevation_slope"] for k in test_sites]))
        b2=float(np.mean([island_results[k]["B2_plus_coastal_access"] for k in test_sites]))
        held[omitted]={
            "source_heldout_original_localities":test_sites,
            "source_train_original_islands":sorted({PARENT[k] for k in train_sites}),
            "heldout_island_equal_site_B1":b1,
            "heldout_island_equal_site_B2":b2,
            "Brier_gain_from_published_coast_distance_B1_minus_B2":b1-b2,
            "source_locality_balanced_Brier":island_results,
        }
    gains=[v["Brier_gain_from_published_coast_distance_B1_minus_B2"] for v in held.values()]
    return {
        "original_species_comparison":("ADELIE","CHINSTRAP"),
        "original_frozen_holdout_groups_n":len(held),
        "original_actual_GSHHG_polygon_groups_held_out":list(sorted(held)),
        "heldout_island_Brier":held,
        "island_equal_mean_B1_minus_B2_gain":float(np.mean(gains)),
        "original_3_island_groups_with_positive_access_gain":int(sum(x>0 for x in gains)),
        "fixed_coast_increment_at_least_two_islands_and_gain_ge_0p005_pass":bool(
            sum(x>0 for x in gains)>=MIN_ISLANDS_IMPROVED and
            float(np.mean(gains))>=MIN_EQUAL_ISLAND_GAIN),
        "individual_penguin_nests_independent_island_replicates":False,
        "coastal_distance_is_not_observed_sea_to_nest_walk_or_true_empty_habitat":True,
        "no_flying_species_or_mammalian_predator_contrast":True,
        "post_V27_species_outcome_exploratory_not_independent_validation":True,
    }


def analyze(source_path:Path):
    data,src=read_original_npz(source_path)
    medians={}
    for island in sorted(set(PARENT.values())):
        sites=[x["xy"] for k,x in data.items() if PARENT[k]==island]
        concat=np.vstack(sites)
        X,Y=np.median(concat,axis=0)
        lon,lat=UTM_TO_WGS84.transform(float(X),float(Y))
        medians[island]=(lon,lat)
    raw=download_original_coast()
    polygon,source=read_original_full_coast_shapes(raw,medians)
    access,geography=coast_distance_for_locs(data,polygon)
    # Coast+terrain sample gate passed before opening new B1 vs B2 scores.
    comparison=source_heldout_predictive_qa(data,access)
    return {
        "status":"V51_ORIGINAL_THREE_GSHHG_ISLAND_COAST_PENGUIN_NEST_ACCESS_COMPLETED",
        "BAS_2019_20_original_source":src,
        "GSHHG_full_resolution_original_coast_source":source,
        "coast_distance_per_source_locality":geography,
        "original_three_island_coast_access_predictor_test":comparison,
        "original_reused_bird_nest_source_not_new_observations":True,
        "no_mammal_or_volant_seabird_exposure_or_biological_p_values":True,
        "no_observed_p_routed_penguin_trajectories":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v26-npz",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    receipt={
        "status":"V51_ORIGINAL_COAST_OR_SAMPLE_HOLD",
        "contract":"contracts/PAPER2_THREE_ISLAND_PENGUIN_COAST_ACCESS_V51.md",
        "original_NPZ_expected_SHA":SOURCE_NPZ_SHA,
        "GSHHG_full_original_expected_sha":GSHHG_SHA,
        "source_breeding_outcome_fitted":False,
        "no_flying_or_invasive_mammal_effect_fitted":True,
    }
    try:
        receipt.update(analyze(args.v26_npz))
    except Exception as e:
        receipt["status"]="V51_ORIGINAL_COAST_OR_SAMPLE_HOLD"
        receipt["error"]=type(e).__name__+": "+str(e)[:800]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    brief={
        "status":receipt["status"],
        "coast_sha":receipt.get("GSHHG_full_resolution_original_coast_source",{}).get("original_GSHHG_SHA256"),
        "island_ids":receipt.get("GSHHG_full_resolution_original_coast_source",{}).get("original_GSHHG_source_ids_for_three_coast_islands"),
        "source_nest_source_per_locality":receipt.get("coast_distance_per_source_locality"),
        "heldout":receipt.get("original_three_island_coast_access_predictor_test"),
        "error":receipt.get("error"),
    }
    print(json.dumps(brief,ensure_ascii=False))
    if receipt["status"]!="V51_ORIGINAL_THREE_GSHHG_ISLAND_COAST_PENGUIN_NEST_ACCESS_COMPLETED":
        raise SystemExit(2)

if __name__=="__main__":
    main()
