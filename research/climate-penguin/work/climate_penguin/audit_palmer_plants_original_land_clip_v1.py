"""Clip published Plantarctica 2024 composite vegetation to five exact SCAR island polygons.

Measures independently published mapped spatial extent, NOT annually observed
vegetation change or a causal result of penguin abandonment or warming.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,sys,tempfile,zipfile
from collections import defaultdict
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse

import requests,shapefile
from pyproj import CRS,Transformer
from shapely.geometry import Point,shape
from shapely.ops import unary_union

sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_palmer_original_island_rock_v1 as island

ROOT=Path(__file__).resolve().parents[2]
SITE_CSV=ROOT/"outputs/comparison_audit/palmer_site_coordinates.csv"
FIGSHARE_ID=24745956
FIGSHARE_API=f"https://api.figshare.com/v2/articles/{FIGSHARE_ID}/files"
VEG_ZIP_SHA="7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236"
EXPECTED_CLASSES={"Vegetation","Lichen","Snow Algae"}
EXPECTED_FEATURES=87391
MAX_ZIP_BYTES=15_000_000
MAX_UNZIP_BYTES=180_000_000

def sha(b):return hashlib.sha256(b).hexdigest()

def official_vegetation_zip():
    response=requests.get(FIGSHARE_API,timeout=(20,45))
    response.raise_for_status()
    entries=response.json()
    if not isinstance(entries,list):raise ValueError("SOURCE_STOP non-list figshare files")
    candidates=[x for x in entries if x.get("name")=="PlantarcticaVegetationMap.zip"]
    if len(candidates)!=1:raise ValueError("SOURCE_STOP target Vegetation ZIP not listed by authoritative figshare article")
    original=candidates[0]
    if not 0<int(original.get("size",0))<=MAX_ZIP_BYTES:
        raise ValueError("SOURCE_STOP figshare source file size invalid")
    url=original.get("download_url") or f"https://figshare.com/ndownloader/files/{original['id']}"
    u=urlparse(url)
    if u.scheme!="https" or (u.hostname or "").lower() not in {
        "figshare.com","ndownloader.figshare.com","api.figshare.com","ndownloader.figshare.com"
    }:
        raise ValueError("SOURCE_STOP unexpected original figshare file domain")
    with requests.get(url,timeout=(25,95),stream=True) as response:
        response.raise_for_status()
        data=bytearray()
        for part in response.iter_content(chunk_size=65536):
            data.extend(part)
            if len(data)>MAX_ZIP_BYTES:raise ValueError("SOURCE_STOP source ZIP too large")
    raw=bytes(data)
    if not raw.startswith(b"PK") or sha(raw)!=VEG_ZIP_SHA:
        raise ValueError("SOURCE_STOP original Plantarctica ZIP SHA drift")
    return raw,{"doi":"10.6084/m9.figshare.24745956","figshare_file_id":original["id"],
                "figshare_advertised_size":original["size"],
                "download_original_sha256":sha(raw)}

def unpack(blob,target):
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        members=z.infolist()
        if len(members)>50 or sum(f.file_size for f in members)>MAX_UNZIP_BYTES or z.testzip() is not None:
            raise ValueError("SOURCE_STOP invalid figshare vegetation ZIP archive")
        for f in members:
            rel=PurePosixPath(f.filename)
            if rel.is_absolute() or ".." in rel.parts or len(rel.parts)>6:
                raise ValueError("SOURCE_STOP unsafe original vegetation file path")
            if f.is_dir():continue
            dst=target.joinpath(*rel.parts)
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(z.read(f))
    files=list(target.rglob("*.shp"))
    if len(files)!=1:raise ValueError("SOURCE_STOP original map must have one polygon shapefile")
    prj=files[0].with_suffix(".prj")
    if not prj.exists() or not CRS.from_wkt(prj.read_text(errors="replace")).equals(CRS.from_epsg(3031)):
        raise ValueError("SOURCE_STOP original vegetation CRS is not EPSG:3031")
    return files[0]

def geom_class_clips(land,source_features):
    """Union exact clipped geom within each source land/class; never use point buffers."""
    by_land=defaultdict(list)
    for fid,cls,geom in source_features:
        if cls not in EXPECTED_CLASSES:continue
        if not geom.is_valid or geom.is_empty:
            raise ValueError("SOURCE_STOP invalid original vegetation feature intersects a focal island")
        for island_id,poly in land.items():
            if not geom.intersects(poly):continue
            part=geom.intersection(poly)
            if not part.is_empty and part.area>0:
                by_land[island_id,cls].append((fid,part))
    rows=[]
    for island_id,polygon in sorted(land.items()):
        entry={"site_id":island_id,"original_scar_land_area_epsg3031_m2":float(polygon.area)}
        class_areas=[]
        for cls in ("Vegetation","Lichen","Snow Algae"):
            hits=by_land[island_id,cls]
            geom=unary_union([g for _,g in hits]) if hits else None
            area=float(geom.area) if geom is not None else 0.
            assert 0<=area<=float(polygon.area)+1e-6
            entry[cls.replace(" ","_")+"_source_features_intersecting_island"]=len({fid for fid,_ in hits})
            entry[cls.replace(" ","_")+"_mapped_union_m2"]=area
            class_areas.append(geom)
        grouped=[v for v in class_areas if v is not None]
        joint=unary_union(grouped) if grouped else None
        entry["all_classes_mapped_union_m2"]=float(joint.area) if joint else 0.
        entry["map_nonzero_means_island_occupied_by_penguins"]=False
        entry["zero_map_does_not_prove_true_vegetation_absence"]=True
        assert entry["all_classes_mapped_union_m2"]<=float(polygon.area)+1e-6
        rows.append(entry)
    return rows

def audit():
    raw,receipt=official_vegetation_zip()
    sites=island.csvrows(SITE_CSV)
    assert len(sites)==5
    convert=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    pts={s["site_id"]:Point(*convert.transform(float(s["longitude"]),float(s["latitude"]))) for s in sites}
    coast_blob=island.original_publisher_zip()
    with tempfile.TemporaryDirectory(prefix="palmer-pland-scar-") as td:
        root=Path(td)
        sc= island.unpack(coast_blob,root/"coast")
        near_land,_=island.geometry_source_candidates(sc,pts)
        classification={sid:island.classify(pt,near_land) for sid,pt in pts.items()}
        if any(x["category"]!="EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON" for x in classification.values()):
            raise ValueError("SOURCE_STOP at least one of five site points lacks exact original land")
        fid_to_geom={fid:geom for fid,geom in near_land}
        selected={sid:fid_to_geom[x["original_land_fid"]] for sid,x in classification.items()}
        if len({x["original_land_fid"] for x in classification.values()})!=5:
            raise ValueError("GEOGRAPHY_STOP five nominal islands not five unique mapped land features")
        vfile=unpack(raw,root/"vegetation")
        reader=shapefile.Reader(str(vfile))
        fields=[f[0] for f in reader.fields[1:]]
        classes=defaultdict(int)
        records=[]
        for fid,sr in enumerate(reader.iterShapeRecords()):
            vals=dict(zip(fields,sr.record))
            cls=vals.get("Vegetation")
            classes[str(cls)]+=1
            bbox=sr.shape.bbox
            if not any(not (bbox[2]<g.bounds[0] or bbox[0]>g.bounds[2] or
                bbox[3]<g.bounds[1] or bbox[1]>g.bounds[3]) for g in selected.values()):
                continue
            geom=shape(sr.shape.__geo_interface__)
            records.append((fid,str(cls),geom))
    if sum(classes.values())!=EXPECTED_FEATURES or set(classes)!=EXPECTED_CLASSES:
        raise ValueError("SOURCE_STOP original 87391-feature vegetation map changed")
    clip=geom_class_clips(selected,records)
    for x in clip:
        src=classification[x["site_id"]]
        x["original_scar_land_fid"]=src["original_land_fid"]
        x["mapped_vegetation_is_2024_static_composite_not_time_series"]=True
    return {"schema":1,
            "status":"original_2024_plantarctica_composite_clipped_to_2026_published_land_not_temporal_greening",
            "vegetation_publisher_source":receipt,
            "coast_source":{"sha256":sha(coast_blob),
                 "doi":"10.5285/13c4d2f1-8903-4d7f-8977-592121975554"},
            "original_vegetation_feature_count":sum(classes.values()),
            "original_source_classes":dict(classes),
            "five_islands":clip,
            "n_islands":len(clip),
            "count_data_used":False,
            "physical_island_rock_access_measured":False,
            "annual_vegetation_change_measured":False,
            "temporal_penguin_effect_measured":False,
            "zero_vegetation_map_is_true_absence":False,
            "unobserved_seal_trampling_or_nutrient_process_resolved":False,
            "source_shape_crs":"EPSG:3031",
            "area": "Projected union of clipped mapped feature footprints, metres squared; not true vegetation biomass or nesting substrate",
            "caution": "2024 published composite and 2026 cartographic boundary do not reconstruct land cover in the 2007 loss year"
           }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    result=audit()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    print("PALMER_ISLAND_PLANTARCTICA_CLIPPED_RECEIPT="+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)

if __name__=="__main__":main()
