#!/usr/bin/env python3
"""V42 first-party public GBIF independent positive mammal-island witness audit.

Original Mammal Mapper (CC BY) + Mammal Atlas (CC BY-NC) 2022–2026;
source-only GBIF records (not verified absences) and RSPB geography/GSHHG.
NEVER reads Stanbury source label positives or V40 probabilities/JNCC counts.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlparse

import requests
from shapely.geometry import Point
from pyproj import Transformer

import audit_jncc_predator_island_source_v33 as uk
import audit_jncc_naturalearth_landmass_v31 as geo
import audit_jncc_predator_ne_land_v35 as v35
import audit_jncc_predator_gshhg_f_land_v36 as gshhg

GBIF_ROOT="https://api.gbif.org/v1"
DATASETS={
    "Mammal Mapper":("8898e990-9d39-4871-9e6e-d1031c19e24b","CC_BY_4_0","10.15468/mjw32e"),
    "National Mammal Atlas":("67e2335c-4303-4ee3-9bfe-ecfe65662629","CC_BY_NC_4_0","10.15468/i2eosa"),
}
TAXA={
    "American mink":("Neogale vison","Neovison vison","Mustela vison"),
    "Brown rat":("Rattus norvegicus",),
    "House mouse":("Mus musculus",),
    "Cat_sighting_NOT_verified_feral":("Felis catus",),
}
MAX_PER_DATASET_TAXON=5000
PAGE_SIZE=250
MAX_UNCERTAINTY_M=250.
INLAND_MIN_M=250.
MIN_GBIF_EVENTS=10
MIN_GBIF_ISLANDS=5
MIN_ARCHIPELAGOS=2
ORIGINAL_PERIOD=(2022,2026)
AS_OF="2026-10-27"
EXPECTED_RSPB_SOURCE_ISLANDS=9688
EXPECTED_V40_GT10HA=506
GBIF_LICENSES={d[0]:d[1] for d in DATASETS.values()}

def safe_gbif_json(session,path,params=None):
    url=GBIF_ROOT+path
    if urlparse(url).hostname!="api.gbif.org":
        raise ValueError("GBIF_PUBLIC_HOST_GATE")
    r=session.get(url,params=params,timeout=(15,55),headers={
        "User-Agent":"mina-v42-public-GBIF-mammal-source-audit/1.0 (source-only research)"
    })
    r.raise_for_status()
    final=urlparse(r.url)
    if final.scheme!="https" or final.hostname!="api.gbif.org":
        raise ValueError("GBIF_PUBLIC_REDIRECT_GATE")
    if len(r.content)>3_000_000:
        raise ValueError("GBIF_PUBLIC_RESPONSE_SIZE_GATE")
    value=r.json()
    if not isinstance(value,dict):
        raise ValueError("GBIF_UNEXPECTED_JSON")
    return value


def matching_taxon(session,names):
    results=[]
    for name in names:
        obj=safe_gbif_json(session,"/species/match",{"name":name,"strict":"true"})
        usage=obj.get("acceptedUsageKey",obj.get("usageKey"))
        rank=str(obj.get("rank",""))
        match=str(obj.get("matchType",""))
        if not (isinstance(usage,int) and usage>0 and rank in ("SPECIES","SUBSPECIES")
                and match in ("EXACT","HIGHERRANK")):
            results.append({"request":name,"state":"UNRESOLVED","matchType":match,"rank":rank})
            continue
        results.append({"request":name,"state":"RESOLVED","taxonKey":usage,
                        "matchType":match,"rank":rank,
                        "canonicalName":str(obj.get("canonicalName",""))[:120]})
    keys=sorted({x["taxonKey"] for x in results if x["state"]=="RESOLVED"})
    return keys,results


def normalized_gbif_license(value):
    """GBIF Registry may return the canonical CC licence URL rather than enum."""
    if value in ("CC_BY_4_0","CC_BY_NC_4_0"):
        return value
    parsed=urlparse(str(value))
    if parsed.scheme not in ("https","http") or parsed.hostname!="creativecommons.org":
        return None
    path=parsed.path.rstrip("/")
    if path in ("/licenses/by/4.0","/licenses/by/4.0/legalcode"):
        return "CC_BY_4_0"
    if path in ("/licenses/by-nc/4.0","/licenses/by-nc/4.0/legalcode"):
        return "CC_BY_NC_4_0"
    return None


def source_registration(session):
    report={}
    for label,(key,license_name,doi) in DATASETS.items():
        obj=safe_gbif_json(session,"/dataset/"+key)
        if obj.get("key")!=key:
            raise ValueError("GBIF_DATASET_KEY_MISMATCH "+label)
        lic=obj.get("license")
        if normalized_gbif_license(lic)!=license_name:
            raise ValueError("GBIF_DATASET_LICENSE_CHANGED "+label+":"+str(lic))
        report[label]={
            "datasetKey":key,"expected_DOI":doi,
            "returned_title":obj.get("title"),
            "returned_license":lic,
            "normalized_license":normalized_gbif_license(lic),
            "returned_publishingOrganizationKey":obj.get("publishingOrganizationKey"),
            "source_last_pub":obj.get("pubDate"),
            "same_source_recording_network_may_overlap":True,
        }
    return report


def request_parameters(dataset_key,taxon_key):
    return {
        "datasetKey":dataset_key,
        "taxonKey":str(taxon_key),
        "hasCoordinate":"true",
        "hasGeospatialIssue":"false",
        "occurrenceStatus":"PRESENT",
        "year":f"{ORIGINAL_PERIOD[0]},{ORIGINAL_PERIOD[1]}",
    }


def page_public_records(session,dataset_key,taxon_key):
    params=request_parameters(dataset_key,taxon_key)
    info=safe_gbif_json(session,"/occurrence/search",{**params,"limit":1,"offset":0})
    count=info.get("count")
    if not isinstance(count,int) or count<0:
        raise ValueError("GBIF_OCCURRENCE_TOTAL_NOT_INTEGER")
    if count>MAX_PER_DATASET_TAXON:
        return [],{"api_count":count,"retrieved":0,"status":"TOO_MANY_PUBLIC_SEARCH_ROWS_STOP",
                   "source_not_safely_exhaustive":True}
    records=[]
    for offset in range(0,count,PAGE_SIZE):
        response=safe_gbif_json(session,"/occurrence/search",{
            **params,"limit":min(PAGE_SIZE,count-offset),"offset":offset,
        })
        rows=response.get("results")
        if not isinstance(rows,list) or len(rows)!=min(PAGE_SIZE,count-offset):
            raise ValueError("GBIF_PAGINATED_SOURCE_DRIFT")
        records.extend(rows)
    if len(records)!=count:
        raise ValueError("GBIF_RETRIEVAL_COUNT_MISMATCH")
    return records,{"api_count":count,"retrieved":len(records),"status":"COMPLETE_PUBLIC_SEARCH",
                    "source_not_safely_exhaustive":False}


def record_quality(row,taxon):
    """Only public IDs and georeference retained; no verbatim recorder identity."""
    if not isinstance(row,dict):
        return None,"SOURCE_RECORD_NOT_OBJECT"
    species=(str(row.get("species","") or row.get("scientificName",""))).casefold()
    known={
        "American mink":("vison",),
        "Brown rat":("rattus norvegicus",),
        "House mouse":("mus musculus",),
        "Cat_sighting_NOT_verified_feral":("felis catus","felis silvestris catus"),
    }
    if not any(x in species for x in known[taxon]):
        return None,"GBIF_TAXON_LINEAGE_MISMATCH"
    year=row.get("year")
    if not isinstance(year,int) or not ORIGINAL_PERIOD[0]<=year<=ORIGINAL_PERIOD[1]:
        return None,"SOURCE_YEAR_OUT_OF_RANGE"
    date=str(row.get("eventDate",""))
    if date and date[:10]>AS_OF:
        return None,"FUTURE_EVENT_DATE"
    lon=uk.to_integral_key(None)  # intentional no-op; avoid parsing rounded identifiers as coordinates
    try:
        lon=float(row.get("decimalLongitude"))
        lat=float(row.get("decimalLatitude"))
    except (TypeError,ValueError):
        return None,"NO_NUMERIC_COORDINATES"
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return None,"NONFINITE_COORDINATES"
    if not (48<=lat<=63.5 and -13.5<=lon<=3.5):
        return None,"OUTSIDE_FROZEN_UK_STUDY_ENVELOPE"
    uncertainty=row.get("coordinateUncertaintyInMeters")
    try:
        u=float(uncertainty)
    except (TypeError,ValueError):
        u=None
    precision_valid=bool(u is not None and math.isfinite(u) and 0<u<=MAX_UNCERTAINTY_M)
    return {
        "lat":lat,"lon":lon,"u":u if u is not None and math.isfinite(u) else None,
        "precision_gate":precision_valid,
        "gbifID":str(row.get("gbifID",row.get("key",""))),
        "occurrenceID":str(row.get("occurrenceID","") or ""),
        "taxon":taxon,"year":year,
        "eventDate":date[:10],
    }, ("COORDINATE_UNCERTAINTY_ELIGIBLE" if precision_valid
        else "COORDINATE_UNCERTAINTY_NOT_KNOWN_LE250")


def collect_public_source():
    with requests.Session() as session:
        registration=source_registration(session)
        resolved={}
        resolved_summaries={}
        for taxon,names in TAXA.items():
            keys,report=matching_taxon(session,names)
            resolved[taxon]=keys
            resolved_summaries[taxon]=report
        rows=[]
        raw_metadata={}
        pair_count=0
        for label,(dskey,_lic,_doi) in DATASETS.items():
            for taxon in TAXA:
                keys=resolved[taxon]
                if not keys:
                    raw_metadata[label+":"+taxon]={
                        "status":"SOURCE_TAXON_KEY_NOT_RESOLVED","keys":[]}
                    continue
                counter=Counter();dedup={}
                inputs=[]
                for key in keys:
                    pair_count+=1
                    page,info=page_public_records(session,dskey,key)
                    inputs.append({"taxonKey":key,**info})
                    if info["status"]!="COMPLETE_PUBLIC_SEARCH":
                        continue
                    for r in page:
                        item,why=record_quality(r,taxon)
                        counter[why]+=1
                        if item is None:continue
                        occurrence=item["gbifID"]
                        if not occurrence:
                            counter["MISSING_GBIF_ID"]+=1
                            continue
                        if occurrence in dedup:
                            counter["DUPLICATE_GBIF_ID"]+=1
                            continue
                        dedup[occurrence]=item
                complete=all(i["status"]=="COMPLETE_PUBLIC_SEARCH" for i in inputs)
                raw_metadata[label+":"+taxon]={
                    "status": "PUBLIC_SOURCE_RETRIEVAL_COMPLETE" if complete
                        else "PARTIAL_OR_UNRESOLVED_TAXON_SOURCE_HOLD",
                    "queries":inputs,
                    "source_screen_counts":dict(counter),
                    "within_dataset_unique_records_after_GBIF_ID_dedup":len(dedup) if complete else None,
                    "precision_eligible_geo_records":sum(x["precision_gate"] for x in dedup.values()) if complete else None,
                }
                if complete:
                    for occ in dedup.values():
                        occ["dataset"]=label
                        rows.append(occ)
    return rows,{
        "data_publishers":registration,
        "species_keys":resolved_summaries,
        "source_dataset_by_taxon":raw_metadata,
        "public_API_species_query_n":pair_count,
        "all_requested_source_pairs_complete":all(
            x["status"]=="PUBLIC_SOURCE_RETRIEVAL_COMPLETE"
            for x in raw_metadata.values()
        ),
        "GBIF_api_search_100k_limit_never_bypassed":True,
        "independent_observer_effort_or_survey_non_detections_unavailable":True,
    }


def source_taxon_completeness(source_report):
    """An incompletely paginated GBIF taxon cannot pass independent validation."""
    meta=source_report["source_dataset_by_taxon"]
    return {
        tax:all(
            meta.get(label+":"+tax,{}).get("status")=="PUBLIC_SOURCE_RETRIEVAL_COMPLETE"
            for label in DATASETS
        )
        for tax in TAXA
    }


def strict_original_island_witnesses(records, complete_taxa):
    ids,rspb,metadata=uk.fetch_rpsb_islands()
    if len(rspb)!=EXPECTED_RSPB_SOURCE_ISLANDS:
        raise ValueError("RSPB_original_2014_island_count_changed")
    large={id for id,r in rspb.items()
           if isinstance(r["low_tide_area_h"],(int,float))
           and r["low_tide_area_h"]>10}
    if len(large)!=EXPECTED_V40_GT10HA:
        raise ValueError("RSPB_V40_GT10HA_SOURCE_COHORT_CHANGED")

    original=gshhg.download_gshhg()
    geometry,area,qa=gshhg.precise_UK_geography(gshhg.shapefile_source(original))
    isp={
       id:(r["latitude"],r["longitude"]) for id,r in rspb.items()
       if r.get("latitude") is not None and r.get("longitude") is not None
    }
    island_labels,_=geo.attach_points(geometry,area,isp)
    strict,bridge=v35.strict_RSPB_landmass_bridge(island_labels,area)
    # GBIF coordinates may be redacted/coarsened; never nearby snap.
    locations={i:(r["lat"],r["lon"]) for i,r in enumerate(records)}
    assigned,_=geo.attach_points(geometry,area,locations)
    counts=Counter()
    tax_summary={}
    key_by_taxon=defaultdict(set)
    region_by_taxon=defaultdict(set)
    events_by_taxon=defaultdict(set)
    sources_per_taxon=defaultdict(Counter)
    same_external_record_ids=defaultdict(set)
    tx=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    for i,r in enumerate(records):
        tax=r["taxon"];ds=r["dataset"]
        state=assigned.get(i,{"status":"UNRESOLVED"})
        counts["all_GBIF_records_in_UK_envelope"]+=1
        counts["mapped_"+state["status"]]+=1
        if state["status"]!="INTERIOR":
            continue
        counts["GBIF_point_inside_unique_land_geometry"]+=1
        poly=state["physical_id"]
        if poly not in strict:
            counts["GBIF_inside_land_but_not_unique_RSPB_island_ID"]+=1
            continue
        lowid=strict[poly]
        if lowid not in large:
            counts["GBIF_inside_RSPB_island_below_V40_area_domain"]+=1
            continue
        counts["GBIF_inside_strict_unique_RSPB_V40_island"]+=1
        if not r["precision_gate"]:
            counts["GBIF_inside_original_island_but_uncertainty_not_le250m"]+=1
            continue
        lon,lat=r["lon"],r["lat"]
        point=Point(*tx.transform(lon,lat))
        margin=float(geometry[poly].boundary.distance(point))
        if not margin>INLAND_MIN_M:
            counts["GBIF_inside_island_but_uncertainty_radius_crosses_coast"]+=1
            continue
        # only anonymous group aggregates (never original GBIF occurrence coordinates in result)
        key_by_taxon[tax].add(lowid)
        meta=rspb[lowid]
        arch=str(meta.get("group") or "").strip().lower()
        if not arch:
            arch="region:"+str(meta.get("country") or "")+":"+str(meta.get("coast") or "")
        region_by_taxon[tax].add(arch)
        events_by_taxon[tax].add((ds,r["gbifID"]))
        sources_per_taxon[tax][ds]+=1
        if r["occurrenceID"]:
            same_external_record_ids[(tax,r["occurrenceID"])].add(ds)
    exact_duplicates_across_datasets=sum(len(v)>1 for v in same_external_record_ids.values())
    for tax in TAXA:
        n_events=len(events_by_taxon[tax])
        n_islands=len(key_by_taxon[tax])
        n_regions=len(region_by_taxon[tax])
        pass_gate=(
            tax!="Cat_sighting_NOT_verified_feral"
            and bool(complete_taxa.get(tax,False))
            and n_events>=MIN_GBIF_EVENTS and n_islands>=MIN_GBIF_ISLANDS
            and n_regions>=MIN_ARCHIPELAGOS
        )
        tax_summary[tax]={
            "independently_documented_recent_strict_island_events":n_events,
            "unique_physical_island_original_RSPB_lowids":n_islands,
            "distinct_original_RSPB_archipelago_groups":n_regions,
            "GBIF_source_recorder_networks":dict(sources_per_taxon[tax]),
            "both_independent_GBIF_dataset_species_queries_complete":bool(complete_taxa.get(tax,False)),
            "original_source_positive_only_comparison_gate_pass":bool(pass_gate),
            "focal_island_status":"ELIGIBLE_FOR_POSITIVE_ONLY_RANKING"
                if pass_gate else "STOP_INDEPENDENT_ISLAND_WITNESS_SUPPORT",
            "cat_sightings_are_not_field_verified_feral_cat":tax=="Cat_sighting_NOT_verified_feral",
        }
    return {
        "source_original_RSPB_9688":len(rspb),
        "V40_original_source_islands_mlws_gt10ha":len(large),
        "GSHHG_2_3_7_f_original_sha256":gshhg.SOURCE_SHA256,
        "GSHHG_geography_QA":qa,
        "strict_original_RSPB_small_island_geometry_crosswalk":bridge,
        "GBIF_GSHHG_full_coverage_status_counts":dict(counts),
        "potential_same_occurrence_ID_across_datasets_count":exact_duplicates_across_datasets,
        "strict_recent_documented_positive_witnesses_by_taxon":tax_summary,
        "individual_mammal_coordinates_in_report":False,
        "original_RSPB_island_identity_points_in_report":False,
        "no_Stanbury_label_or_V40_predicted_probability_opened":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    out={
       "status":"V42_INDEPENDENT_MAMMAL_OCCURRENCE_SOURCE_UNSTARTED",
       "contract":"contracts/JNCC_GBIF_INDEPENDENT_PREDATOR_ISLAND_WITNESS_V42.md",
       "GBIF_DOI":["10.15468/mjw32e","10.15468/i2eosa"],
       "GBIF_dated_2022_2026_not_contemporaneous_2014_Stanbury":True,
       "original_2014_Stanbury_predator_source_labels_read":False,
       "original_JNCC_seabird_abundance_or_V40_predicted_values_read":False,
       "independent_true_predator_occupancy_probability_estimated":False,
       "independent_field_surveyed_absences_obtained":False,
    }
    try:
        occ,info=collect_public_source()
        out["GBIF_public_source"]=info
        out["downloaded_public_eligible_GBIF_source_record_count"]=len(occ)
        complete=source_taxon_completeness(info)
        out["original_public_GBIF_complete_taxon_sources"]=complete
        if any(complete.values()) and occ:
            # Eligibility is only permitted for species with BOTH pinned
            # sources completely retrieved. Brown rat's 7073-record Atlas
            # query exceeds the frozen 5000 cap: it stays incomplete, not
            # retrospectively threshold-relaxed or treated as zero.
            out["strict_physical_island_source_qa"]=strict_original_island_witnesses(
                occ,complete
            )
            out["status"]=(
                "V42_PUBLIC_GBIF_INDEPENDENT_PREDATOR_ISLAND_WITNESS_AUDITED"
                if all(complete.values())
                else "V42_PARTIAL_PUBLIC_GBIF_STRICT_ISLAND_AUDITED_SOME_TAXA_HOLD"
            )
        else:
            out["status"]="V42_GBIF_PUBLIC_ACCESS_OR_EXHAUSTIVENESS_HOLD"
    except Exception as e:
        out["status"]="V42_PUBLIC_DATA_OR_SCHEMA_SOURCE_HOLD"
        out["error"]=type(e).__name__+": "+str(e)[:600]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))
    if out["status"] not in (
        "V42_PUBLIC_GBIF_INDEPENDENT_PREDATOR_ISLAND_WITNESS_AUDITED",
        "V42_PARTIAL_PUBLIC_GBIF_STRICT_ISLAND_AUDITED_SOME_TAXA_HOLD",
    ):
        raise SystemExit(2)


if __name__=="__main__":
    main()
