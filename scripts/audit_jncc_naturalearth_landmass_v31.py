#!/usr/bin/env python3
"""Natural Earth native-land connectivity JNCC physical site matching V31.

Never opens JNCC biological count magnitudes; source external physical geography
measured separately from V30 ecological outcomes.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse
import requests
import shapefile
from shapely.geometry import Point,box,shape
from shapely.ops import unary_union,transform
from shapely.strtree import STRtree
from pyproj import Transformer
import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29
import model_jncc_component_concentration_v30 as v30

URLS={
    "major_land":"https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip",
    "minor_islands":"https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_minor_islands.zip"
}
LAND_ENVELOPE=(-13.5,48.0,3.5,63.5)
MIN_KM2=.01
SMALL_MAX_KM2=1000
LARGE_MIN_KM2=50000
NEAREST_M=250
SECOND_NEAREST_M=750
MAX_ZIP=15*1024*1024
MAX_UNZIPPED=100*1024*1024
MIN_SMALL_PANELS=20
MIN_LARGE_PANELS=20
MIN_SMALL_PHYSICAL_ISLANDS=5
MIN_LARGE_PHYSICAL_LANDMASSES=2
MIN_BALANCED_SPECIES=5
MIN_EACH_CLASS_PER_BALANCED_SPECIES=3

def land_type(area):
    if not math.isfinite(area) or area<MIN_KM2:
        return "UNRESOLVED_OR_MICRO"
    if area<=SMALL_MAX_KM2:return "SMALL_OFFSHORE_LANDMASS"
    if area>=LARGE_MIN_KM2:return "LARGE_LANDMASS"
    return "INTERMEDIATE_LANDMASS"

def download_ne():
    out={}
    for key,url in URLS.items():
        r=requests.get(url,timeout=45,stream=True,
                       headers={"User-Agent":"mina-naturalearth-jncc-geom-source-v31/1.0"})
        try:
            p=urlparse(r.url)
            if p.scheme!="https" or p.hostname!="naturalearth.s3.amazonaws.com":
                raise ValueError("SOURCE_STOP unexpected Natural Earth redirected host")
            r.raise_for_status()
            buffers=[];total=0
            for chunk in r.iter_content(chunk_size=65536):
                total+=len(chunk)
                if total>MAX_ZIP:raise ValueError("SOURCE_STOP original NE ZIP too large")
                buffers.append(chunk)
            raw=b"".join(buffers)
            if not raw.startswith(b"PK"):
                raise ValueError("SOURCE_STOP original NE response not shapefile ZIP")
            out[key]=(raw,{"url":r.url,"original_bytes":len(raw),
                            "original_sha256":hashlib.sha256(raw).hexdigest(),
                            "publisher_dataset":key})
        finally:
            r.close()
    return out

def polygons_from_zip(raw,base):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        if len(names)>30 or z.testzip() is not None:
            raise ValueError("SOURCE_STOP invalid publisher Natural Earth archive")
        length=0
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("SOURCE_STOP unsafe archive member")
            length+=info.file_size
        if length>MAX_UNZIPPED:raise ValueError("SOURCE_STOP uncompressed geodata oversized")
        parts={}
        for extension in (".shp",".shx",".dbf"):
            candidates=[x for x in names if x.endswith(base+extension)]
            if len(candidates)!=1:
                raise ValueError("SCHEMA_STOP missing or ambiguous shapefile "+base+extension)
            parts[extension]=z.read(candidates[0])
        rr=shapefile.Reader(shp=io.BytesIO(parts[".shp"]),
                            shx=io.BytesIO(parts[".shx"]),dbf=io.BytesIO(parts[".dbf"]))
        roi=box(*LAND_ENVELOPE)
        polygons=[]
        shape_count=0
        for item in rr.iterShapes():
            shape_count+=1
            bbox=item.bbox
            if bbox[2]<LAND_ENVELOPE[0] or bbox[0]>LAND_ENVELOPE[2] or bbox[3]<LAND_ENVELOPE[1] or bbox[1]>LAND_ENVELOPE[3]:
                continue
            geom=shape(item.__geo_interface__)
            if not geom.is_valid:
                geom=geom.buffer(0)
            if geom.is_empty or not geom.intersects(roi):
                continue
            polygons.append(geom)
        if shape_count<10 or not polygons:
            raise ValueError("SCHEMA_STOP official Natural Earth polygons inaccessible")
        return polygons,{"source_shapes":shape_count,
                         "source_envelope_intersecting_shapes":len(polygons),
                         "uncompressed_original_bytes":length}

def geometric_components(source_polygons):
    combined=unary_union(source_polygons)
    if combined.is_empty:raise ValueError("SOURCE_STOP unioned land is empty")
    if combined.geom_type=="Polygon":
        geoms=[combined]
    elif combined.geom_type=="MultiPolygon":
        geoms=list(combined.geoms)
    else:
        geoms=[g for g in combined.geoms if g.geom_type=="Polygon"]
    transform_fn=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True).transform
    shapes=[transform(transform_fn,g) for g in geoms]
    kms=[s.area/1e6 for s in shapes]
    good=[(g,a) for g,a in zip(shapes,kms) if a>=0 and math.isfinite(a)]
    if len(good)<10:raise ValueError("SOURCE_STOP not enough independent island geom")
    shapes=[pair[0] for pair in good];kms=[pair[1] for pair in good]
    return shapes,kms,{
        "original_source_fragment_count":len(source_polygons),
        "merged_connected_physical_landmasses_in_regional_envelope":len(shapes),
        "landmass_area_rule":"equal-area EPSG3035 on globally connected Natural Earth 10m polygons",
        "landmass_class_counts":dict(Counter(land_type(km) for km in kms))
    }

def attach_points(components,areas,geolocations):
    tree=STRtree(components)
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    labels={};state=Counter();cache={}
    for key,(lat,lon) in geolocations.items():
        coordinate=(lat,lon)
        if coordinate in cache:
            labels[key]=cache[coordinate]
            state["cached_same_original_coordinate"]+=1
            continue
        px,py=tr.transform(lon,lat)
        if not(math.isfinite(px) and math.isfinite(py)):
            labels[key]={"status":"UNRESOLVED","reason":"NONFINITE_SOURCE_POINT"}
            continue
        p=Point(px,py)
        possibilities=list(map(int,tree.query(p.buffer(SECOND_NEAREST_M))))
        inside=[i for i in possibilities if components[i].covers(p)]
        if len(inside)==1:
            i=inside[0]
            detail={"status":"INTERIOR","physical_id":i,"area_km2":areas[i],"class":land_type(areas[i]),"snap_distance_m":0.0}
        elif len(inside)>1:
            detail={"status":"AMBIGUOUS","reason":"MULTIPLE_PHYSICAL_LAND_POLYGONS"}
        else:
            nearest=sorted((components[i].distance(p),i) for i in possibilities)
            if not nearest or nearest[0][0]>NEAREST_M:
                detail={"status":"UNRESOLVED","reason":"COASTAL_POINT_TOO_FAR_FROM_PUBLISHER_LAND"}
            elif len(nearest)>1 and nearest[1][0]<=SECOND_NEAREST_M:
                detail={"status":"AMBIGUOUS","reason":"MULTIPLE_CLOSE_PHYSICAL_LANDMASSES"}
            else:
                distance,i=nearest[0]
                detail={"status":"COAST_SNAPPED","physical_id":i,"area_km2":areas[i],"class":land_type(areas[i]),"snap_distance_m":float(distance)}
        cache[coordinate]=detail
        labels[key]=detail
        state[detail["status"]]+=1
    return labels,state

def source_only_panels(original_rows,components,areas):
    raw_safe,source_qa=v30.extract_structural(original_rows)
    if not source_qa["pre_count_structural_gate_pass"] or len(raw_safe)!=1483:
        raise ValueError("SOURCE_STOP source V30 structural support changed")
    sites={}
    for k,rows in raw_safe.items():
        for original,_ in rows:
            point=(original["lat"],original["lon"])
            sitekey=(original["species"],original["country"],original["master"],original["unit"],original["site_id"])
            if sitekey in sites and sites[sitekey]!=point:
                raise ValueError("SOURCE_STOP original site ID coordinate changes")
            sites[sitekey]=point
    labels,point_states=attach_points(components,areas,sites)
    panel_classes=Counter()
    species_groups=defaultdict(Counter)
    matched_sites=Counter()
    physical_ids=defaultdict(set)
    labels_by_class=Counter()
    valid_panels=[]
    for parent,children in sorted(raw_safe.items()):
        matched=[]
        for original,_ in children:
            k=(original["species"],original["country"],original["master"],original["unit"],original["site_id"])
            r=labels[k]
            matched.append(r)
            matched_sites[r["status"]]+=1
        if len(matched)!=len(children):
            raise ValueError("SOURCE_STOP lost original child sites")
        ids={r.get("physical_id") for r in matched}
        if None in ids:
            panel="UNRESOLVED_OR_AMBIGUOUS_CHILD"
        elif len(ids)!=1:
            panel="MIXED_PHYSICAL_LANDMASSES"
        else:
            panel=land_type(matched[0]["area_km2"])
            physical_ids[panel].add(matched[0]["physical_id"])
            species_groups[parent[0]][panel]+=1
            valid_panels.append((parent,panel,matched[0]["physical_id"]))
        panel_classes[panel]+=1
    small={x for x in valid_panels if x[1]=="SMALL_OFFSHORE_LANDMASS"}
    large={x for x in valid_panels if x[1]=="LARGE_LANDMASS"}
    balanced=[species for species,p in species_groups.items()
              if p["SMALL_OFFSHORE_LANDMASS"]>=MIN_EACH_CLASS_PER_BALANCED_SPECIES
              and p["LARGE_LANDMASS"]>=MIN_EACH_CLASS_PER_BALANCED_SPECIES]
    support=(
      len(small)>=MIN_SMALL_PANELS and len(large)>=MIN_LARGE_PANELS
      and len(physical_ids["SMALL_OFFSHORE_LANDMASS"])>=MIN_SMALL_PHYSICAL_ISLANDS
      and len(physical_ids["LARGE_LANDMASS"])>=MIN_LARGE_PHYSICAL_LANDMASSES
      and len(balanced)>=MIN_BALANCED_SPECIES
    )
    return {
      "original_V30_eligible_site_metadata_panels":len(raw_safe),
      "original_source_child_records_covered":len(sites),
      "unique_source_coordinates":len(set(sites.values())),
      "original_coordinate_states_unique_query_counts":dict(point_states),
      "original_child_site_match_states":dict(matched_sites),
      "original_parent_panel_physical_geometry_type":dict(panel_classes),
      "physical_small_island_landmass_count_in_classified_panels":len(physical_ids["SMALL_OFFSHORE_LANDMASS"]),
      "physical_large_landmass_count_in_classified_panels":len(physical_ids["LARGE_LANDMASS"]),
      "geographical_panels_by_species":{sp:dict(z) for sp,z in sorted(species_groups.items())},
      "balanced_species_with_three_or_more_each_small_and_large_panels":sorted(balanced),
      "predeclared_physical_island_generalization_support_pass":bool(support),
      "count_magnitude_cells_opened":0,
      "original_master_sites_not_independent_geographic_islands":True,
      "Britain_and_Ireland_are_both_large_islands_not_continental_controls":True,
      "no_physical_island_effect_fit":True,
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    receipt={"status":"HOLD_JNCC_OR_NATURAL_EARTH_SOURCE","ecological_effect_fitted":False}
    try:
        raw,jncc=v28.download_original()
        if jncc["original_sha256"]!=v29.ORIGINAL_SHA:
            raise ValueError("SOURCE_STOP JNCC original revised file mutated")
        ne=download_ne()
        result=source_only_geometry(ne)
        physical,areas,join_meta=geometric_components(result["land"])
        q=source_only_panels(list(v29.original_rows(raw)),physical,areas)
        receipt={
          "status":"JNCC_V31_INDEPENDENT_NATURAL_EARTH_LANDMASS_SOURCE_SUPPORT",
          "JNCC_original_SHA256":v29.ORIGINAL_SHA,
          "JNCC_source_rows_previous_V29_qualifying":14112,
          "natural_earth_publishers":result["receipts"],
          "natural_earth_schema_source":result["geography"],
          "natural_earth_connected_landmass":join_meta,
          "site_and_source_parent_geography":q,
          "ecological_effect_fitted":False,
          "scientific_decision":("READY_FOR_PREDECLARED_PHYSICAL_GEOGRAPHY_COMPARATIVE_CONTRACT"
                                  if q["predeclared_physical_island_generalization_support_pass"]
                                  else "STOP_GEOGRAPHICALLY_INCOMPLETE_OR_UNBALANCED_SMALL_LARGE_SOURCE")
        }
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:900]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_JNCC_OR_NATURAL_EARTH_SOURCE":
        raise SystemExit(2)

def source_only_geometry(original):
    all_polygons=[];receipts={};geography={}
    for key,base in (("major_land","ne_10m_land"),("minor_islands","ne_10m_minor_islands")):
        raw,meta=original[key]
        parts,schema=polygons_from_zip(raw,base)
        all_polygons.extend(parts)
        receipts[key]=meta
        geography[key]=schema
    return {"land":all_polygons,"receipts":receipts,"geography":geography}

if __name__=="__main__":main()
