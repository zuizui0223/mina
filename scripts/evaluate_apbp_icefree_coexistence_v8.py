#!/usr/bin/env python3
"""V8: abiotic Antarctic ecosystem mosaic and co-censused Pygoscelis nest balance.

First standalone exploratory ecological test of a NEW predictor family, NOT
V6 retuning. Scientific design frozen in contract V8 BEFORE reading raster.
Only Tier1 independent ABIOTIC categories used; no biotic/range layers.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import requests
import shapefile

APBP_INPUT_SHA="75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59"
GEO_INPUT_SHA="b93c4e85667d7a12ae76166620e5ff5d4ea6482c182457cf3ca4cd0321551c41"
ZENODO_RECORD="11629115"
TIF="AntarcticaEcosystemInventory_IceFreeLands_v1_int.tif"
DBF=TIF+".vat.dbf"
TIF_MD5="cde880d73f7f18b44aecf5690aa2dc92"
DBF_MD5="fa5363b1c0d882b4343e239d03dc2ba4"
BANDS_M=(5000,2000)
BLOCK_M=250000
MIN_VALID_5KM_PIXELS=30
RIDGE_ALPHA=10.
TAXA=(
    "Pygoscelis adeliae",
    "Pygoscelis antarcticus",
    "Pygoscelis papua",
)
PAIRS=tuple("|".join(pair) for pair in combinations(TAXA,2))
BASE=["latitude","longitude_sin","longitude_cos","log_pair_nests",
      "median_accuracy","log_event_count","pair_AG","pair_CG"]
PLUS=BASE+["tier1_entropy_5km","icefree_fraction_5km"]
MIN_CV_BLOCK_SITES=3
MIN_CV_BLOCKS=4
MIN_OBSERVATIONS=40


def download_zenodo(name,path,original_md5,limit):
    urls=(
        f"https://zenodo.org/records/{ZENODO_RECORD}/files/{name}?download=1",
        f"https://zenodo.org/api/records/{ZENODO_RECORD}/files/{name}/content",
    )
    errors=[]
    for url in urls:
        try:
            with requests.get(url,timeout=(25,85),stream=True,
                              headers={"User-Agent":"Antarctic macro reproducible habitat analysis/1.0"}) as res:
                res.raise_for_status()
                final=res.url
                if not final.startswith("https://"):
                    raise ValueError("SOURCE_STOP insecure remote Zenodo file")
                digest=hashlib.md5()
                sha=hashlib.sha256()
                total=0
                with path.open("wb") as out:
                    for chunk in res.iter_content(65536):
                        total+=len(chunk)
                        if total>limit:
                            raise ValueError("SOURCE_STOP Antarctic raster exceeds byte cap")
                        digest.update(chunk);sha.update(chunk);out.write(chunk)
            if digest.hexdigest()!=original_md5:
                raise ValueError("SOURCE_STOP official published Zenodo file MD5 mismatch")
            return {"sha256":sha.hexdigest(),"md5":digest.hexdigest(),"bytes":total,
                    "published_file":name, "original_record_doi":"10.5281/zenodo.11629115"}
        except (requests.RequestException,ValueError) as exc:
            errors.append(type(exc).__name__+": "+str(exc)[:80])
            path.unlink(missing_ok=True)
    raise ValueError("SOURCE_STOP cannot retrieve original hash-verified Antarctic inventory: "+" / ".join(errors))


def tier1_lookup(dbf):
    reader=shapefile.Reader(dbf=str(dbf))
    names=[f[0] for f in reader.fields[1:]]
    if "Value" not in names or "ID_Tier1" not in names:
        raise ValueError("SCHEMA_STOP source vat lacks raster value/Tier1 mapping")
    out={}
    for item in reader.iterRecords():
        r=dict(zip(names,item))
        key=int(r["Value"])
        cat=str(r["ID_Tier1"]).strip()
        # The publisher's Nine Tier1 environment units ALSO include
        # geophysical active/dormant volcanoes and lakes (G1,G2,L);
        # it is incorrect to require codes to start with "E".
        #
        # CRITICAL RESPONSE-LEAKAGE GATE: the source Tier2 includes
        # an explicit "Penguin colonies" unit E1B8 constructed from
        # MAPPPD records. Its underlying pixels must NEVER be used
        # to predict the very same MAPPPD/APBP penguin observations.
        tier2=str(r.get("ID_Tier2","")).strip()
        tier2name=str(r.get("Name_Tier2","")).strip()
        tier3name=str(r.get("Name_Tier3","")).strip()
        is_penguin_source_derived=(
            "E1B8" in tier2
            or "penguin" in tier2name.casefold()
            or "penguin" in tier3name.casefold()
        )
        if is_penguin_source_derived:
            continue
        if not cat:
            raise ValueError("SCHEMA_STOP non-penguin source unit without Tier1 code")
        if key in out and out[key]!=cat:
            raise ValueError("SCHEMA_STOP value maps ambiguously to multiple Tier1 classes")
        out[key]=cat
    if len(set(out.values()))!=9 or len(out)<150:
        raise ValueError("SCHEMA_STOP source Tier1 classes unexpected count")
    return out


def verified_csv(path,expected):
    blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=expected:
        raise ValueError("SOURCE_STOP joined APBP/high-res source SHA256 mismatch")
    return pd.read_csv(path,low_memory=False)


def source_pairs(source,geo):
    df=source.loc[
        source["eligibility"].eq("ELIGIBLE_NEST_RECORD_ONLY")
        & source["scientificName_accepted"].isin(TAXA)
    ].copy()
    numeric=pd.to_numeric(df.nest_numeric_candidate,errors="coerce")
    if numeric.isna().any() or (numeric<0).any() or (numeric!=np.floor(numeric)).any():
        raise ValueError("OBS_STOP original measured nest count cannot be treated as integer")
    df["nests"]=numeric.astype("int64")
    df["accuracy"]=pd.to_numeric(df.measurementAccuracy_original,errors="coerce")
    if not df.accuracy.between(1,5).all():
        raise ValueError("OBS_STOP original measurement accuracy missing/outside source 1–5")
    # One independent Event core containing two or three genuine quantified
    # nest species; never infer absence of taxa not listed in an Event.
    events=[]
    excluded_duplicate_taxon_events=0
    ignored_zero_zero_pairs=0
    for event_id,frame in df.groupby("original_event_core_id",sort=True):
        if frame.scientificName_accepted.duplicated().any():
            excluded_duplicate_taxon_events+=1
            continue
        if frame.scientificName_accepted.nunique()<2:
            continue
        site_ids=frame.site_id_original.dropna().unique()
        if len(site_ids)!=1:
            raise ValueError("OBS_STOP one original event has multiple incompatible source site IDs")
        for ia,ib in combinations(list(frame.index),2):
            a,b=frame.loc[ia],frame.loc[ib]
            denom=int(a.nests+b.nests)
            if denom<=0:
                ignored_zero_zero_pairs+=1
                continue
            pair="|".join(sorted([a.scientificName_accepted,b.scientificName_accepted]))
            events.append({
                "site_id":site_ids[0],
                "original_EventCore":str(event_id),
                "pair":pair,
                "balance":2*min(int(a.nests),int(b.nests))/denom,
                "log_nests":math.log1p(denom),
                "accuracy":float(np.mean([a.accuracy,b.accuracy])),
                "latitude":float(a.decimalLatitude),
                "longitude":float(a.decimalLongitude),
            })
    if not events:
        raise ValueError("OBS_STOP original public events contain no co-census pairs")
    event_df=pd.DataFrame(events)
    if not event_df.pair.isin(PAIRS).all():
        raise ValueError("OBS_STOP unexpected Pygoscelis pair category")
    # Repeated original Events remain evidence within site but not separate
    # independent island-replicate units.
    agg=event_df.groupby(["site_id","pair"],as_index=False).agg(
        response_balance=("balance","median"),
        source_median_log_nests=("log_nests","median"),
        source_median_accuracy=("accuracy","median"),
        source_n_events=("original_EventCore","nunique"),
        source_latitude=("latitude","median"),
        source_longitude=("longitude","median"),
        original_pair_events=("original_EventCore","size"),
    )
    if geo.source_locationID.duplicated().any():
        raise ValueError("SOURCE_STOP duplicate site IDs in original high-res land audit")
    geo_fields=[
        "source_locationID","high_class","original_APBP_max_uncertainty_m",
        "high_location_confidence","within_site_max_drift_m",
    ]
    agg=agg.merge(geo[geo_fields],left_on="site_id",right_on="source_locationID",
                  how="left",validate="many_to_one")
    source_summary={
        "original_simultaneous_multispecies_Events":int(event_df.original_EventCore.nunique()),
        "original_taxa_pair_event_rows":len(event_df),
        "original_site_pair_independent_rows":len(agg),
        "original_locationIDs_at_multispecies_Events":int(agg.site_id.nunique()),
        "n_discarded_ambiguous_multispecies_event_IDs":excluded_duplicate_taxon_events,
        "original_both_species_measured_zero_pairs_excluded":ignored_zero_zero_pairs,
        "site_land_categories_original":agg.groupby("site_id").first().high_class.value_counts(dropna=False).to_dict(),
    }
    return agg,source_summary


def pixel_ecology(arr,trans,cx,cy,tier,radii=BANDS_M):
    # Values are original TIFF raster 'Value' IDs; no-data/water/ice outside
    # the mapped terrestrial ecosystem is not a scored 0-type habitat.
    rr,cc=np.indices(arr.shape)
    xx=trans.c+(cc+0.5)*trans.a+(rr+0.5)*trans.b
    yy=trans.f+(cc+0.5)*trans.d+(rr+0.5)*trans.e
    distance_sq=(xx-cx)**2+(yy-cy)**2
    original=np.ma.getdata(arr).astype(int)
    valid=(~np.ma.getmaskarray(arr)) & np.isin(original,np.fromiter(tier.keys(),dtype=int))
    answer={}
    for rad in radii:
        inside=distance_sq<=rad*rad
        present=valid&inside
        n=int(present.sum())
        count=int(inside.sum())
        labels=Counter(tier[x] for x in original[present])
        entropy=-sum((v/n)*math.log(v/n) for v in labels.values())/math.log(9) if n else None
        answer[rad]={
            "valid_icefree_100m_pixels":n,
            "sampled_100m_pixel_centers":count,
            "fraction_mapped_icefree":n/count if count else None,
            "tier1_shannon_diversity_normlog9":entropy,
            "tier1_distinct_env_types":len(labels),
            "original_tier1_pixel_counts":dict(labels),
        }
    return answer


def extract_habitats(path,sites,tier):
    out={}
    with rasterio.open(path) as raster:
        if raster.count!=1 or raster.res[0]<90 or raster.res[0]>115 or raster.res[1]<90 or raster.res[1]>115:
            raise ValueError("RASTER_STOP published raster not single-band 100m mapping")
        if raster.crs is None:
            raise ValueError("RASTER_STOP no source CRS for 100m Antarctica")
        if not raster.crs.is_projected:
            raise ValueError("RASTER_STOP source 100m map not projected")
        tr=Transformer.from_crs(4326,raster.crs,always_xy=True)
        for site,latlon in sorted(sites.items()):
            lat,lon=latlon
            if not (-90<lat<-57 and -180<=lon<=180):
                raise ValueError("RASTER_STOP APBP source site beyond mapped Antarctic envelope")
            x,y=tr.transform(lon,lat)
            radius=max(BANDS_M)
            window=from_bounds(x-radius-150,y-radius-150,x+radius+150,y+radius+150,
                               raster.transform).round_offsets().round_lengths()
            arr=raster.read(1,window=window,boundless=True,masked=True)
            transform=raster.window_transform(window)
            out[site]=pixel_ecology(arr,transform,x,y,tier)
        qa={
            "raster_original_crs":str(raster.crs),
            "raster_original_pixel_size_m":list(map(float,raster.res)),
            "raster_original_shape":[raster.height,raster.width],
            "raster_nodata":str(raster.nodata),
            "source_Tier1_labels":sorted(set(tier.values())),
            "response_leakage_guard":"All original Tier2 E1B8 penguin colonies and Tier3 penguin class pixels excluded from environmental raster sampling",
            "icefree_fraction_caveat":"Fraction of retained non-penguin-classified mapped Tier1 cells, NOT historical ice-free nest capacity",
        }
    return out,qa


def attach_habitats(sitepairs,habitats):
    result=sitepairs.copy()
    for radius in BANDS_M:
        for sourcekey,name in [
            ("valid_icefree_100m_pixels","valid_pixels"),
            ("fraction_mapped_icefree","icefree_fraction"),
            ("tier1_shannon_diversity_normlog9","tier1_entropy"),
            ("tier1_distinct_env_types","tier1_types"),
        ]:
            result[f"{name}_{radius//1000}km"]=result.site_id.map(
                lambda x:habitats[x][radius][sourcekey])
    return result


def model_columns(data,use_2km=False):
    d=data
    lon=np.deg2rad(d.source_longitude.to_numpy(dtype=float))
    pair=d.pair
    cols={
        "latitude":d.source_latitude.to_numpy(dtype=float),
        "longitude_sin":np.sin(lon),
        "longitude_cos":np.cos(lon),
        "log_pair_nests":d.source_median_log_nests.to_numpy(dtype=float),
        "median_accuracy":d.source_median_accuracy.to_numpy(dtype=float),
        "log_event_count":np.log1p(d.source_n_events.to_numpy(dtype=float)),
        "pair_AG":pair.eq("Pygoscelis adeliae|Pygoscelis papua").to_numpy(dtype=float),
        "pair_CG":pair.eq("Pygoscelis antarcticus|Pygoscelis papua").to_numpy(dtype=float),
        "tier1_entropy_5km":d[f"tier1_entropy_{2 if use_2km else 5}km"].to_numpy(dtype=float),
        "icefree_fraction_5km":d[f"icefree_fraction_{2 if use_2km else 5}km"].to_numpy(dtype=float),
    }
    return cols


def ridge_predict(y,columns,names,training):
    raw=np.column_stack([columns[name] for name in names])
    means=raw[training].mean(axis=0)
    scales=raw[training].std(axis=0)
    scales[scales<1e-12]=1
    matrix=(raw-means)/scales
    design=np.column_stack([np.ones(len(y)),matrix])
    fit=design[training]
    penalty=np.diag([0]+[RIDGE_ALPHA]*len(names))
    beta=np.linalg.solve(fit.T@fit+penalty,fit.T@y[training])
    coef={key:float(beta[k+1]/scales[k]) for k,key in enumerate(names)}
    return design@beta,coef


def cv_results(frame,variant=False):
    if frame.empty:raise ValueError("MODEL_STOP no source usable covariates")
    y=frame.response_balance.to_numpy(dtype=float)
    columns=model_columns(frame,use_2km=variant)
    if not np.isfinite(y).all() or not all(np.isfinite(v).all() for v in columns.values()):
        raise ValueError("MODEL_STOP original public habitat/response contains NaN")
    labels=sorted(frame.block250k.unique())
    if len(labels)<MIN_CV_BLOCKS:
        raise ValueError("MODEL_STOP too few independent Antarctic site clusters")
    groups=frame.block250k.to_numpy(dtype=str)
    summary={}
    for model,features in (("B0",BASE),("B1",PLUS)):
        block_error={}
        pred=np.empty(len(y))
        for label in labels:
            train=groups!=label
            withheld=~train
            yhat,_=ridge_predict(y,columns,features,train)
            pred[withheld]=yhat[withheld]
            block_error[label]=float(np.mean((y[withheld]-yhat[withheld])**2))
        summary[model]={
            "equal_block_MSE":float(np.mean(list(block_error.values()))),
            "row_weighted_MSE":float(np.mean((y-pred)**2)),
            "per_block_MSE":block_error,
        }
    gain=summary["B0"]["equal_block_MSE"]-summary["B1"]["equal_block_MSE"]
    improvements={
        label:summary["B0"]["per_block_MSE"][label]-
              summary["B1"]["per_block_MSE"][label] for label in labels
    }
    big=max(labels,key=lambda l:frame.loc[frame.block250k==l,"site_id"].nunique())
    _,full=ridge_predict(y,columns,PLUS,np.ones(len(y),dtype=bool))
    _,no_big=ridge_predict(y,columns,PLUS,groups!=big)
    ent_full=full["tier1_entropy_5km"]
    ent_nobig=no_big["tier1_entropy_5km"]
    return {
        "model_full_sample_n_site_pair_rows":len(frame),
        "n_distinct_sites":int(frame.site_id.nunique()),
        "n_eligible_geographical_blocks":len(labels),
        "largest_block":big,
        "block_site_counts":frame.groupby("block250k").site_id.nunique().to_dict(),
        "models":summary,
        "incremental_habitat_prediction_gain_equal_block_MSE":gain,
        "n_geographic_blocks_improved":sum(v>0 for v in improvements.values()),
        "improvements_by_block":improvements,
        "full_fit_abiotic_Tier1_entropy_coefficient":ent_full,
        "omit_largest_block_Tier1_entropy_coefficient":ent_nobig,
        "entropy_coef_sign_stable_no_largest":ent_full*ent_nobig>0,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--population",type=Path,required=True)
    parser.add_argument("--high-land",type=Path,required=True)
    parser.add_argument("--out-json",type=Path,required=True)
    parser.add_argument("--out-csv",type=Path,required=True)
    args=parser.parse_args()
    result={"status":"HOLD_SOURCE_OR_ENVIRONMENT","novel_island_mechanism_demonstrated":False}
    try:
        pop=verified_csv(args.population,APBP_INPUT_SHA)
        geo=verified_csv(args.high_land,GEO_INPUT_SHA)
        pairs,sourceqa=source_pairs(pop,geo)
        coords=pairs.groupby("site_id")[["source_latitude","source_longitude"]].median()
        site_coords={k:(float(z.source_latitude),float(z.source_longitude))
                     for k,z in coords.iterrows()}
        with tempfile.TemporaryDirectory(prefix="antarctica-aei-v8-") as tmp:
            folder=Path(tmp)
            raster_path=folder/TIF
            vat_path=folder/DBF
            rastdata=download_zenodo(TIF,raster_path,TIF_MD5,80_000_000)
            vatdata=download_zenodo(DBF,vat_path,DBF_MD5,250_000)
            tier=tier1_lookup(vat_path)
            habitat,habitatqa=extract_habitats(raster_path,site_coords,tier)
        data=attach_habitats(pairs,habitat)
        eligibility=data.valid_pixels_5km>=MIN_VALID_5KM_PIXELS
        # No invented zero source habitat for sites outside ice-free inventory.
        data=data.loc[eligibility].copy()
        tr=Transformer.from_crs(4326,3031,always_xy=True)
        xx,yy=tr.transform(data.source_longitude.to_numpy(dtype=float),
                           data.source_latitude.to_numpy(dtype=float))
        data["block250k"]=[
            f"{math.floor(x/BLOCK_M)}_{math.floor(y/BLOCK_M)}"
            for x,y in zip(xx,yy)]
        counts=data.groupby("block250k").site_id.nunique()
        accepted=counts[counts>=MIN_CV_BLOCK_SITES].index
        data=data.loc[data.block250k.isin(accepted)].copy()
        result={
            "status":"V8_SOURCE_AND_HABITAT_ONLY_INSUFFICIENT_SPATIAL_SUPPORT",
            "source_APBP_pub_sha256":APBP_INPUT_SHA,
            "source_ADD_v4_pub_sha256":GEO_INPUT_SHA,
            "source_Zenodo_raster":rastdata,
            "source_Zenodo_Tier1_VAT":vatdata,
            "original_abiotic_ecosystem_raster":habitatqa,
            "original_corecording_QA":sourceqa,
            "raster_supported_site_pair_rows":int(eligibility.sum()),
            "raster_valid_source_locationIDs":int(pairs.loc[eligibility,"site_id"].nunique()),
            "excluded_site_pairs_without_30_icefree_pixels":int((~eligibility).sum()),
            "CV_eligible_site_pair_rows":len(data),
            "CV_eligible_unique_source_sites":int(data.site_id.nunique()),
            "CV_eligible_spatial_blocks":int(data.block250k.nunique()),
            "novel_island_mechanism_demonstrated":False,
        }
        if len(data)>=MIN_OBSERVATIONS and data.block250k.nunique()>=MIN_CV_BLOCKS:
            # Uncertainty is original source positional precision, not a
            # preferred sample-size/impact filter.
            primary=cv_results(data)
            precise=data.loc[
                data.original_APBP_max_uncertainty_m.le(1000)
                & data.original_APBP_max_uncertainty_m.notna()].copy()
            if precise.site_id.nunique()>=10 and len(precise)>=20:
                _,co_primary=ridge_predict(
                    precise.response_balance.to_numpy(dtype=float),
                    model_columns(precise),PLUS,
                    np.ones(len(precise),dtype=bool))
                precision_coef=co_primary["tier1_entropy_5km"]
            else:
                precision_coef=None
            secondary_data=data.loc[data.valid_pixels_2km>=MIN_VALID_5KM_PIXELS]
            secondary=(cv_results(secondary_data,variant=True)
                       if secondary_data.block250k.nunique()>=MIN_CV_BLOCKS
                       and len(secondary_data)>=MIN_OBSERVATIONS else None)
            improvements=primary["n_geographic_blocks_improved"]
            nblock=primary["n_eligible_geographical_blocks"]
            full_coef=primary["full_fit_abiotic_Tier1_entropy_coefficient"]
            robust=(
                primary["incremental_habitat_prediction_gain_equal_block_MSE"]>0
                and improvements>=math.ceil(2*nblock/3)
                and primary["entropy_coef_sign_stable_no_largest"]
                and precision_coef is not None
                and full_coef*precision_coef>0
            )
            result.update({
                "status":"V8_ANTARCTIC_ABIOTIC_HABITAT_COEXISTENCE_EXPLORATORY",
                "main_model_comparison":primary,
                "precise_original_coordinate_subset_n_sites":int(precise.site_id.nunique()),
                "precision_subset_entropy_coef":precision_coef,
                "predeclared_2km_habitat_sensitivity":secondary,
                "passed_full_descriptive_macro_support_gates":bool(robust),
                "scientific_decision":(
                    "TENTATIVE_NONCAUSAL_ICEFREE_HABITAT_MOSAIC_ASSOCIATION"
                    if robust else "NOT_SUPPORTED_OR_UNIDENTIFIABLE"
                ),
            })
        args.out_csv.parent.mkdir(parents=True,exist_ok=True)
        data.to_csv(args.out_csv,index=False)
        result["derived_site_pair_cohabitat_SHA256"]=hashlib.sha256(
            args.out_csv.read_bytes()).hexdigest()
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:650]
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
