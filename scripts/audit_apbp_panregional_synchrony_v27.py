#!/usr/bin/env python3
"""V27: original APBP database matched-season spatial-sign feasibility and guarded effect."""
from __future__ import annotations
import argparse,csv,hashlib,io,itertools,json,math,re
from pathlib import Path
from collections import Counter,defaultdict
from pyproj import Transformer
SHA="75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59"
SPECIES={"Pygoscelis adeliae","Pygoscelis antarcticus","Pygoscelis papua"}
FIELDS={"eligibility","scientificName_accepted","site_id_original","event_date",
        "decimalLatitude","decimalLongitude","samplingProtocol","source_associatedReferences",
        "nest_numeric_candidate"}
MIN_STRATA=10;MIN_YEARS=6;MIN_SPECIES=2;MIN_BLOCKS=5;MIN_SITES=20;MIN_PAIRS=3

def read_original(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("SOURCE_STOP original V2 SHA256 differs")
    records=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not records or not FIELDS.issubset(records[0]):
        raise ValueError("SCHEMA_STOP original APBP V2 fields incomplete")
    if len(records)!=4750:
        raise ValueError("SOURCE_STOP original measurement row count changed")
    return records

def season_month(v):
    m=re.fullmatch(r"(19\d{2}|20\d{2})-(\d{2})(?:-\d{2})?",str(v or "").strip())
    if m is None:return None
    y=int(m.group(1));month=int(m.group(2))
    if month not in (12,1,2):return None
    season=y if month==12 else y-1
    return (season,month) if 1979<=season<=2022 else None

def normalized(value):
    return " ".join(str(value or "").lower().split())

def metadata(rows):
    """Do not inspect source nest_numeric_candidate values here."""
    pre=defaultdict(list);skipped=Counter()
    for r in rows:
        if r["eligibility"]!="ELIGIBLE_NEST_RECORD_ONLY" or r["scientificName_accepted"] not in SPECIES:
            continue
        sm=season_month(r["event_date"]);site=str(r["site_id_original"]).strip()
        if sm is None or not site:
            skipped["no_exact_source_season_or_site"]+=1;continue
        try:
            lat=float(r["decimalLatitude"]);lon=float(r["decimalLongitude"])
            if not(math.isfinite(lat) and math.isfinite(lon)
                   and -90<=lat<=-50 and -180<=lon<=180):
                raise ValueError("invalid latitude/longitude")
        except (TypeError,ValueError):
            skipped["invalid_source_coordinates"]+=1;continue
        year,month=sm
        pre[(site,r["scientificName_accepted"],year)].append({
            "row":r,"month":month,"lat":lat,"lon":lon,
            "method":normalized(r["samplingProtocol"]),
            "ref":normalized(r["source_associatedReferences"])})
    duplicates={k:len(v) for k,v in pre.items() if len(v)>1}
    unique={k:v[0] for k,v in pre.items() if len(v)==1}
    project=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    site_blocks=defaultdict(set)
    for (site,sp,year),record in unique.items():
        x,y=project.transform(record["lon"],record["lat"])
        if not(math.isfinite(x) and math.isfinite(y)):
            raise ValueError("GEOGRAPHY_STOP source projection failed")
        block=f"{math.floor(x/250000)}_{math.floor(y/250000)}"
        record["block"]=block
        site_blocks[site].add(block)
    conflict={site for site,bs in site_blocks.items() if len(bs)>1}
    valid={k:v for k,v in unique.items() if k[0] not in conflict}
    paired=[];excluded=Counter();reference=Counter()
    for (site,sp,y),prev in valid.items():
        curr=valid.get((site,sp,y+1))
        if curr is None:continue
        if curr["month"]!=prev["month"]:
            excluded["month_changed"]+=1;continue
        if not prev["method"] or prev["method"]!=curr["method"]:
            excluded["protocol_changed_or_unreported"]+=1;continue
        paired.append({"site":site,"species":sp,"year":y,
                       "block":prev["block"],"prev":prev["row"],"curr":curr["row"]})
        reference["same_nonempty_reference" if prev["ref"] and prev["ref"]==curr["ref"]
                  else "different_or_unknown_reference"]+=1
    strata=defaultdict(list)
    for p in paired:strata[(p["species"],p["year"])].append(p)
    qualified={};geocount={}
    for (sp,y),obs in strata.items():
        byblock=Counter(row["block"] for row in obs)
        close=sum(n*(n-1)//2 for n in byblock.values())
        distant=len(obs)*(len(obs)-1)//2-close
        if close>=MIN_PAIRS and distant>=MIN_PAIRS:
            qualified[(sp,y)]=obs
        geocount[f"{sp}|{y}"]={"site_year_changes":len(obs),"geographic_blocks":len(byblock),
                              "same_block_site_pairs":close,"between_block_site_pairs":distant,
                              "eligible":(sp,y) in qualified}
    blocks={p["block"] for rows in qualified.values() for p in rows}
    sites={p["site"] for rows in qualified.values() for p in rows}
    years={key[1] for key in qualified}
    species={key[0] for key in qualified}
    okay=(len(qualified)>=MIN_STRATA and len(years)>=MIN_YEARS
          and len(species)>=MIN_SPECIES and len(blocks)>=MIN_BLOCKS
          and len(sites)>=MIN_SITES)
    report={
       "source_original_total_measurements":len(rows),
       "original_eligible_unique_site_species_seasons":len(valid),
       "duplicate_source_groups_excluded":len(duplicates),
       "source_rows_in_duplicate_groups":sum(duplicates.values()),
       "source_sites_with_multiblock_coordinates_removed":len(conflict),
       "source_quality_exclusions":dict(skipped),
       "strict_same_month_same_protocol_adjacent_site_changes":len(paired),
       "transition_metadata_exclusions":dict(excluded),
       "source_reference_continuity":dict(reference),
       "growth_change_records_by_species":dict(Counter(p["species"] for p in paired)),
       "species_start_year_geographic_support":geocount,
       "qualified_species_year_strata":len(qualified),
       "qualified_unique_start_years":len(years),
       "qualified_species":len(species),
       "qualified_geographic_blocks":len(blocks),
       "qualified_original_site_IDs":len(sites),
       "frozen_macro_gate_pass":bool(okay),
       "original_biological_count_values_accessed":0
    }
    return qualified,report

def source_count(row):
    v=str(row["nest_numeric_candidate"]).strip()
    if not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.0+)?",v):return None
    return int(float(v))

def effect(eligible):
    summaries=[];drops=Counter()
    for (sp,year),items in sorted(eligible.items()):
        obs=[]
        for p in items:
            a=source_count(p["prev"]);b=source_count(p["curr"])
            if a is None or b is None:
                drops["invalid_original_count"]+=1;continue
            obs.append((p["site"],p["block"],(1 if b>a else -1 if b<a else 0)))
        within=[];far=[]
        for a,b in itertools.combinations(obs,2):
            if a[2]==0 or b[2]==0:continue
            (within if a[1]==b[1] else far).append(int(a[2]==b[2]))
        if len(within)<MIN_PAIRS or len(far)<MIN_PAIRS:
            drops["insufficient_nonzero_comparisons"]+=1;continue
        nw=sum(within)/len(within);nf=sum(far)/len(far)
        summaries.append({"species":sp,"year":year,
                          "site_changes":len(obs),"within_site_pairs":len(within),
                          "across_site_pairs":len(far),
                          "near_same_sign":nw,"far_same_sign":nf,"difference":nw-nf})
    ys=sorted({r["year"] for r in summaries})
    if len(summaries)<MIN_STRATA or len(ys)<MIN_YEARS:
        return {"status":"STOP_NUMERIC_PAIR_SUPPORT","effects_computed":False,
                "numeric_strata":len(summaries),"numeric_years":len(ys),
                "numeric_exclusions":dict(drops)}
    d=sum(x["difference"] for x in summaries)/len(summaries)
    pos=sum(x["difference"]>0 for x in summaries)
    omitted=[]
    for year in ys:
        sub=[x["difference"] for x in summaries if x["year"]!=year]
        if sub:omitted.append(sum(sub)/len(sub))
    return {
      "status":"V27_EXPLORATORY_SPATIAL_SYNCHRONY_BY_SOURCE_YEAR",
      "effects_computed":True,"original_species_year_strata":summaries,
      "n_species_year_strata":len(summaries),
      "n_original_start_years":len(ys),
      "mean_within_minus_between_same_direction_concordance":d,
      "n_strata_positive_difference":pos,
      "fraction_strata_positive":pos/len(summaries),
      "leave_one_year_out_delta_range":[min(omitted),max(omitted)],
      "frozen_directional_support":(d>0 and pos>=math.ceil(2*len(summaries)/3)),
      "spatial_block_is_not_original_island":True,
      "source_overlap_prior_V6":True,
      "climate_or_island_causal_mechanism_identified":False,
      "scientific_decision":("DESCRIPTIVE_WITHIN_REGION_MORE_CONCORDANT" if
          d>0 and pos>=math.ceil(2*len(summaries)/3) else
          "NO_SUPPORTED_PANREGIONAL_SPATIAL_CONCORDANCE_DIRECTION")
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    receipt={"status":"HOLD_ORIGINAL_SOURCE","biological_effect_computed":False}
    try:
        strata,qa=metadata(read_original(args.source))
        receipt={"status":"V27_ORIGINAL_APBP_SPATIAL_SOURCE_AUDIT",
                 "original_publisher_DOI":"10.48361/zftxkr",
                 "original_V2_join_SHA256":SHA,
                 "contract":"contracts/APBP_SPATIAL_SYNCHRONY_V27.md",
                 "structural_support":qa,
                 "biological_effect_computed":False,
                 "scientific_decision":("STOP_INSUFFICIENT_SPATIAL_COTEMPORAL_SUPPORT"
                                        if not qa["frozen_macro_gate_pass"] else "PENDING_NUMERIC_GATE")}
        if qa["frozen_macro_gate_pass"]:
            value=effect(strata)
            receipt["biological_effect_computed"]=value["effects_computed"]
            receipt["original_growth_sign_results"]=value
            receipt["scientific_decision"]=value.get("scientific_decision",value["status"])
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:750]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_SOURCE":raise SystemExit(2)
if __name__=="__main__":main()
