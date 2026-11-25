#!/usr/bin/env python3
"""Independently derive ice-free breeding-habitat option traits for 7,785 AADC sites.

Inputs: exact 2021/2025 AADC original geographic workbooks + source-hashed
Antarctic Ecosystem Inventory raster/VAT. NO animal P/A/NR/count workbook.
This is not prospective ecological confirmation of already viewed AADC biology.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

from dbfread import DBF
import numpy as np
from pyproj import Transformer
import rasterio
from rasterio.windows import from_bounds

from audit_aadc_geography_editions_v1 import source_geography_only, parse_geo

AEI_TIF_MD5="cde880d73f7f18b44aecf5690aa2dc92"
AEI_VAT_MD5="fa5363b1c0d882b4343e239d03dc2ba4"
RADIUS_M=2000
EXPECTED_VAT_ROWS=269
SOURCE_CLASS=("island","continent")
ANIMAL_DERIVED_TERMS=(
    "penguin","seabird","bird","colony","rookery","guano","ornithogenic"
)


def file_md5(path:Path)->str:
    h=hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def vat_dictionary(path:Path):
    rows=[dict(x) for x in DBF(str(path),load=True,
        ignore_missing_memofile=True,char_decode_errors="ignore")]
    if len(rows)!=EXPECTED_VAT_ROWS:
        raise ValueError("SOURCE_STOP Antarctic original VAT row count drift")
    mapping={}
    for row in rows:
        val=int(round(float(row["Value"])))
        if val in mapping:
            raise ValueError("SOURCE_STOP original VAT key duplicate")
        t1=str(row["Name_Tier1"]).strip()
        t2=str(row["Name_Tier2"]).strip()
        t3=str(row["Name_Tier3"]).strip()
        if not t1 or not t2 or not t3:
            raise ValueError("SOURCE_STOP original VAT class label empty")
        biological=any(k in (t1+" "+t2+" "+t3).casefold()
                       for k in ANIMAL_DERIVED_TERMS)
        mapping[val]={"tier1":t1,"tier2":t2,"tier3":t3,
                      "animal_label_linked":biological}
    if len({v["tier1"] for v in mapping.values()})!=9:
        raise ValueError("SOURCE_STOP original VAT Tier1 class count drift")
    if len({v["tier2"] for v in mapping.values()})!=33:
        raise ValueError("SOURCE_STOP original VAT Tier2 class count drift")
    return mapping


def source_circle_values(src,x:float,y:float,radius:float=RADIUS_M):
    window=from_bounds(x-radius,y-radius,x+radius,y+radius,
                       transform=src.transform)
    window=window.round_offsets().round_lengths()
    arr=src.read(1,window=window,masked=True,boundless=True)
    affine=src.window_transform(window)
    rows,cols=np.indices(arr.shape)
    xs=affine.c+(cols+.5)*affine.a+(rows+.5)*affine.b
    ys=affine.f+(cols+.5)*affine.d+(rows+.5)*affine.e
    disk=(xs-x)**2+(ys-y)**2<=radius**2
    total=int(disk.sum())
    good=disk & (~np.ma.getmaskarray(arr))
    data=np.asarray(arr.data[good],dtype=float)
    data=data[np.isfinite(data)]
    if any(abs(x-round(x))>1e-8 for x in data):
        raise ValueError("SOURCE_STOP original AEI raster has nonintegral VAT class")
    return total,data.astype(int)


def summarize_habitat(values:np.ndarray,total:int,
                      mapping:dict,pixel_area_m2:float):
    unknown=sorted({int(v) for v in values if int(v) not in mapping})
    if unknown:
        raise ValueError("SOURCE_STOP unmapped AEI VAT raster classes "+str(unknown[:10]))
    all_valid_n=int(len(values))
    allowed=np.asarray([int(v) for v in values
                        if not mapping[int(v)]["animal_label_linked"]],dtype=int)
    independent_n=int(len(allowed))
    if independent_n:
        cls=[mapping[int(v)]["tier2"] for v in allowed]
        types,counts=np.unique(cls,return_counts=True)
        fractions=counts/counts.sum()
        richness=int(len(types))
        shannon=float(-(fractions*np.log(fractions)).sum())
        independent_area=independent_n*pixel_area_m2/1e4
    else:
        richness=shannon=independent_area=None
    return {
        "expected_circle_100m_pixel_centres":int(total),
        "all_classified_icefree_pixel_count":all_valid_n,
        "all_classified_mapped_icefree_area_projected_ha":
            all_valid_n*pixel_area_m2/1e4,
        "all_classified_mapped_icefree_fraction":
            all_valid_n/total if total else None,
        "outcome_label_linked_pixels_excluded":all_valid_n-independent_n,
        "independent_nonanimal_mapped_pixel_count":independent_n,
        "nonanimal_mapped_icefree_area_projected_ha":independent_area,
        "nonanimal_tier2_habitat_richness":richness,
        "nonanimal_tier2_habitat_shannon":shannon,
        "independently_mapped_habitat_coverage":independent_n>0,
    }


def distribution(vals):
    a=np.array([float(x) for x in vals if x is not None and math.isfinite(x)])
    return {
        "available":int(len(a)),
        "median":float(np.median(a)) if len(a) else None,
        "p10":float(np.percentile(a,10)) if len(a) else None,
        "p90":float(np.percentile(a,90)) if len(a) else None,
        "maximum":float(np.max(a)) if len(a) else None,
    }


def geographic_summary(rows):
    subsets={
        "all_2025":lambda r:True,
        "source_class_island":lambda r:r["source_geographic_class"]=="island",
        "source_class_continent":lambda r:r["source_geographic_class"]=="continent",
        "shared_with_2021_source_ids":lambda r:r["original_geographic_site_id_in_2021"],
        "new_only_in_2025_source_ids":lambda r:not r["original_geographic_site_id_in_2021"],
    }
    out={}
    for name,selector in subsets.items():
        subset=[r for r in rows if selector(r)]
        out[name]={
            "original_geographic_sites":len(subset),
            "sites_with_any_original_mapped_icefree_pixels":sum(
                r["all_classified_icefree_pixel_count"]>0 for r in subset),
            "sites_with_nonanimal_mapped_habitat_pixels":sum(
                r["independently_mapped_habitat_coverage"] for r in subset),
            "nonanimal_icefree_projected_area_ha":distribution([
                r["nonanimal_mapped_icefree_area_projected_ha"] for r in subset]),
            "nonanimal_tier2_richness":distribution([
                r["nonanimal_tier2_habitat_richness"] for r in subset]),
            "nonanimal_tier2_shannon":distribution([
                r["nonanimal_tier2_habitat_shannon"] for r in subset]),
            "all_icefree_fraction":distribution([
                r["all_classified_mapped_icefree_fraction"] for r in subset]),
        }
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raster",required=True,type=Path)
    p.add_argument("--vat",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--features",required=True,type=Path)
    a=p.parse_args()
    if file_md5(a.raster)!=AEI_TIF_MD5 or file_md5(a.vat)!=AEI_VAT_MD5:
        raise ValueError("SOURCE_STOP actual AEI raster or VAT original MD5 changed")
    mapping=vat_dictionary(a.vat)
    sources,original_receipts,manifest_sha=source_geography_only()
    old,_=parse_geo(sources["potential_geography_2021"],old=True)
    new,qa=parse_geo(sources["potential_geography_2025"],old=False)
    if len(old)!=4884 or len(new)!=7785:
        raise ValueError("SOURCE_STOP original AADC geography source frame changed")
    records=[]
    with rasterio.open(a.raster) as src:
        if src.count!=1 or str(src.crs)!="EPSG:3031":
            raise ValueError("SOURCE_STOP original AEI TIFF band/CRS mismatch")
        area=abs(float(src.transform.a*src.transform.e-
                       src.transform.b*src.transform.d))
        resolution=(abs(float(src.transform.a)),
                    abs(float(src.transform.e)))
        if not all(abs(x-100)<1e-6 for x in resolution):
            raise ValueError("SOURCE_STOP AEI spatial resolution unexpectedly changed")
        transform=Transformer.from_crs(4326,3031,always_xy=True)
        for ident,r in sorted(new.items()):
            if r["lat"] is None or r["lon"] is None:
                raise ValueError("SOURCE_STOP original AADC potential site location missing")
            x,y=transform.transform(r["lon"],r["lat"])
            total,values=source_circle_values(src,x,y)
            record={
                "original_geographic_site_id":ident,
                "source_geographic_class":r["feature"],
                "original_geographic_site_id_in_2021":ident in old,
                **summarize_habitat(values,total,mapping,area)
            }
            records.append(record)
    result={
        "status":"AADC_7785_INDEPENDENT_AEI_HABITAT_ATLAS_V3",
        "frozen_primary_radius_m":RADIUS_M,
        "source_original_AADC_2025_geographic_site_count":len(new),
        "original_AADC_source_2021_geographic_site_count":len(old),
        "original_AADC_source_manifest_SHA256":manifest_sha,
        "AADC_publisher_workbook_SHA256":original_receipts,
        "original_AEI_raster_MD5":AEI_TIF_MD5,
        "original_AEI_VAT_MD5":AEI_VAT_MD5,
        "original_AEI_raster_resolution_m":list(resolution),
        "original_AEI_VAT_269_unique_classes":len(mapping),
        "animal_outcome_label_exclusion_terms":list(ANIMAL_DERIVED_TERMS),
        "source_original_animal_label_linked_VAT_classes":[
            {"value":int(k),"tier2":v["tier2"],"tier3":v["tier3"]}
            for k,v in sorted(mapping.items()) if v["animal_label_linked"]
        ],
        "independent_breeding_habitat_summary":geographic_summary(records),
        "original_animal_P_A_NR_or_counts_downloaded":0,
        "no_penguin_or_seabird_outcome_fitted":True,
        "original_mapping_animal_labelled_categories_used_as_predictors":False,
        "publisher_geographic_site_is_nest_GPS":False,
        "ecological_fate_of_unmapped_cells_is_absence":False,
        "V14_or_V1_species_outcome_confirmatory_inference_authorized":False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.features.parent.mkdir(parents=True,exist_ok=True)
    with a.features.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    result["derived_7785_site_habitat_feature_CSV_SHA256"]=hashlib.sha256(
        a.features.read_bytes()).hexdigest()
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
