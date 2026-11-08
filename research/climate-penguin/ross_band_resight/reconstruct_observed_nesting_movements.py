#!/usr/bin/env python3
"""Recompute source-verified Ross Adelie nesting-site observations from USAP-DC ZIPs.

Original DOI: 10.15784/601443 (band inventory), 10.15784/601444 (resights).
The publisher MD5 is checked on ORIGINAL UNCOMPRESSED CSV bytes.
No raw band numbers, full records, observers' initials or notes are exported.
This does NOT estimate dispersal rates, survival, recapture probabilities or
climate-causality. This is a post-hoc conservative original-source reconstruction.
"""
from __future__ import annotations
import argparse
import csv
import datetime
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

PUBLISHED={
    "inventory":("band_inv_1994-2021.csv","3da33defa4decc82b6e317c7fa9f9044","utf-8-sig","10.15784/601443"),
    "resights":("band_resighting_1997-2021.csv","aaae6ddad6d12081b5a68466794438a2","latin1","10.15784/601444")
}
BAND_COLS="low high colony season type notes season_yr".split()
RESIGHT_COLS="proofed bandnumb bandseen location status nuegg nuch bandgap subcolony flagged chick1size chick2size chick1age chick2age sex sexhow nestpos date initials notes lat lon datum orig_col colony season".split()
SITES={"ROYD","BIRD","CROZ","BEAU"}
def site(x):
    x=x.strip()
    return {"ROYDS":"ROYD","CR0Z":"CROZ"}.get(x,x)
def season_start(s):
    s=s.strip()
    if s=="2021":return 2020
    if len(s)!=4 or not s.isdigit():return None
    year=1900+int(s[:2]) if int(s[:2])>=90 else 2000+int(s[:2])
    return year if (year+1)%100==int(s[2:]) else None
def verified_zip(path,role):
    filename,md5,encoding,doi=PUBLISHED[role]
    with zipfile.ZipFile(path) as z:
        files=[f for f in z.infolist() if not f.is_dir()]
        if len(files)!=1 or Path(files[0].filename).name!=filename or files[0].file_size>40000000:
            raise ValueError("Unexpected original USAP-DC ZIP layout")
        raw=z.read(files[0])
    if hashlib.md5(raw).hexdigest()!=md5:
        raise ValueError("Original published MD5 mismatch for "+role)
    receipt={"doi":doi,"source_original_csv":filename,
             "csv_bytes":len(raw),"publisher_md5":md5,
             "source_sha256":hashlib.sha256(raw).hexdigest(),"hash_verified":True}
    return csv.reader(io.StringIO(raw.decode(encoding),newline="")),receipt
def primary_nest(r):
    status=r["status"].strip().upper()
    return (status=="INC" and r["nuegg"].strip() in {"1","2"}) or (
        status=="BR" and r["nuch"].strip() in {"1","2"})
def broad_nest(r):
    return (r["status"].strip().upper() in {"INC","BR","P/INC","P/BR"}
            and (r["nuegg"].strip() in {"1","2","3"} or
                 r["nuch"].strip() in {"1","2","3"}))
def save_csv(path,records,cols):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader();w.writerows(records)

def audit(banding_zip,resighting_zip,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    inventor,source_a=verified_zip(banding_zip,"inventory")
    if next(inventor)!=BAND_COLS:raise ValueError("Publisher band inventory headers changed")
    ranges=[]
    for row in inventor:
        if len(row)!=len(BAND_COLS):raise ValueError("Band inventory has malformed row")
        r=dict(zip(BAND_COLS,row))
        lo,hi=int(r["low"]),int(r["high"])
        if lo>hi:raise ValueError("Original band range reversed")
        ranges.append((lo,hi,site(r["colony"]),int(r["season_yr"]),r["type"].strip()))
    assignments={};ambiguous=set()
    for lo,hi,colony,year,kind in ranges:
        for key in range(lo,hi+1):
            if key in assignments:ambiguous.add(key)
            else:assignments[key]=(colony,year,kind)
    for key in ambiguous:assignments.pop(key,None)
    observations,source_b=verified_zip(resighting_zip,"resights")
    if next(observations)!=RESIGHT_COLS:raise ValueError("Publisher resight header changed")
    quality=Counter()
    distinct_numeric=set()
    strict_recruit=defaultdict(set);inc_only=defaultdict(set)
    broader_recruit=defaultdict(set);active_nests=defaultdict(lambda:defaultdict(set))
    band_kind={}
    for row in observations:
        quality["original_rows"]+=1
        if len(row)>26:
            quality["unquoted_notes_extra_comma_rows"]+=1
            # Original free-text column 19 contains an unescaped literal comma.
            # Preserve first 19 and final 6 original source columns exactly.
            row=row[:19]+[",".join(row[19:-6])]+row[-6:]
        if len(row)!=26:raise ValueError("Unexpected source CSV column count")
        r=dict(zip(RESIGHT_COLS,row))
        tag=r["bandnumb"].strip()
        if not tag.isdigit() or int(tag)<=0:
            quality["nonnumeric_or_zero_band_rows"]+=1;continue
        tag=int(tag);distinct_numeric.add(tag)
        if tag in ambiguous:
            quality["overlapping_inventory_id_rows_excluded"]+=1;continue
        origin=assignments.get(tag)
        if origin is None:
            quality["outside_original_band_ranges_rows"]+=1;continue
        birthsite,birthyear,kind=origin
        observed=site(r["colony"])
        if site(r["orig_col"])!=birthsite or birthsite not in SITES:
            quality["orig_col_disagrees_with_band_inventory_or_unrecognized_origin"]+=1
            continue
        if observed not in SITES:
            quality["unknown_observation_colony_rows"]+=1;continue
        if r["proofed"].strip()!="1" or r["bandseen"].strip().upper()!="Y":
            quality["unverified_original_flag_rows"]+=1;continue
        try:
            stamp=datetime.datetime.strptime(r["date"].strip(),"%m/%d/%Y").date()
        except ValueError:
            quality["bad_observation_dates"]+=1;continue
        yr=stamp.year if stamp.month>=7 else stamp.year-1
        if not (1994<=yr<=2020) or season_start(r["season"])!=yr:
            quality["inconsistent_season_and_observation_date"]+=1;continue
        quality["eligible_verified_rows"]+=1
        nest=primary_nest(r)
        if nest:
            quality["strict_active_nest_rows"]+=1
            active_nests[tag][observed].add(yr)
            band_kind[tag]=kind
        if kind=="CHIC" and birthyear>=1994 and yr>=birthyear+2 and observed!=birthsite:
            pair=(birthsite,observed)
            if nest:
                strict_recruit[pair].add(tag)
                if r["status"].strip().upper()=="INC" and r["nuegg"].strip() in {"1","2"}:
                    inc_only[pair].add(tag)
            if broad_nest(r):broader_recruit[pair].add(tag)
    if quality["original_rows"]!=193638 or quality["unquoted_notes_extra_comma_rows"]!=14:
        raise ValueError("Original source row count/CSV notes anomaly changed")
    unique=lambda d: len(set().union(*d.values())) if d else 0
    route_rows=[{"natal_chick_banding_colony":a,"observed_nest_colony":b,
                 "distinct_source_birds":len(ids)}
                for (a,b),ids in sorted(strict_recruit.items())]
    moves=Counter();case_types=Counter();anonymous=[]
    for bird,colonies in active_nests.items():
        if len(colonies)<2:continue
        # First documented active nest for each observed colony, *not* first movement date.
        listed=sorted((min(years),colony) for colony,years in colonies.items())
        across=[(y1,s1,y2,s2) for i,(y1,s1) in enumerate(listed)
                for y2,s2 in listed[i+1:] if y2>y1 and s2!=s1]
        if not across:continue
        year_a,site_a,year_b,site_b=min(across)
        moves[(site_a,site_b)]+=1
        case_types[band_kind[bird]]+=1
        anonymous.append({"first_documented_breeding_colony":site_a,
                          "later_documented_breeding_colony":site_b,
                          "years_between_documented_seasons":year_b-year_a,
                          "band_category":"CHIC" if band_kind[bird]=="CHIC" else "other"})
    summary={
      "status":"OFFICIAL_MD5_VERIFIED_CONSERVATIVE_OBSERVED_NEST_SITE_MOVEMENT",
      "doi_sources":{"banding":source_a,"resighting":source_b},
      "n_original_banding_inventory_ranges":len(ranges),
      "n_overlapping_original_band_labels":len(ambiguous),
      "n_distinct_numeric_resighted_band_labels":len(distinct_numeric),
      "n_inventory_lookup_labels_nonambiguous":len(assignments),
      "original_quality":dict(quality),
      "n_CHIC_band_origin_different_verified_nesting_birds":unique(strict_recruit),
      "n_CHIC_origin_different_INC_egg_only_birds":unique(inc_only),
      "n_CHIC_origin_different_broad_status_birds":unique(broader_recruit),
      "n_birds_with_active_nests_at_two_colonies_in_distinct_seasons":len(anonymous),
      "nest_colony_switch_case_band_category":dict(case_types),
      "natal_origin_to_nesting_site_aggregate":route_rows,
      "documented_breeding_site_moves_aggregate":[
          {"first_nesting_site":s,"later_nesting_site":t,"individuals":n}
          for (s,t),n in sorted(moves.items())],
      "anonymized_site_switch_season_gap_records":sorted(anonymous,key=lambda a:(
         a["first_documented_breeding_colony"],a["later_documented_breeding_colony"])),
      "inference_limits":[
         "Proofed=1, bandseen=Y and exact INC-with-egg or BR-with-chick are operational conservative filters; uploaded files contain no formal status-code dictionary.",
         "CHIC band ranges identify original chick-banding colony/year; inventory is ranges not individual deployment rows.",
         "Observed examples are not dispersal, recruitment, immigration or transition probabilities: site/time effort and detection are unequal.",
         "Detected nesting at two sites in separated years does not date the movement or prove continual nesting in intervening seasons.",
         "Study area is Ross/Beaufort, not Palmer or six west Antarctic Peninsula community-shift sites.",
         "The topic of multi-state breeding dispersal in this metapopulation was studied previously in 2010 and 2026; do not call this a first discovery.",
         "No human observer notes, individual bird bands or original raw ZIPs are included in the output files."]}
    if (len(ranges),len(ambiguous),unique(strict_recruit),unique(inc_only),
        unique(broader_recruit),len(anonymous))!=(229,4,64,59,69,3):
        raise ValueError("Pinned original source aggregation no longer reproduces")
    save_csv(outdir/"natal_chick_banded_nesting_other_colony.csv",route_rows,
             ["natal_chick_banding_colony","observed_nest_colony","distinct_source_birds"])
    save_csv(outdir/"breeding_colony_switch_observed.csv",summary["documented_breeding_site_moves_aggregate"],
             ["first_nesting_site","later_nesting_site","individuals"])
    (outdir/"verified_aggregate_no_individual_ids.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ROSS_RAW_MOVEMENT_AGGREGATE="+json.dumps({
        "source_md5_verified":True,"resight_rows":quality["original_rows"],
        "extra_notes_commas":quality["unquoted_notes_extra_comma_rows"],
        "natal_off_origin_strict":unique(strict_recruit),
        "natal_only_inc_eggs":unique(inc_only),
        "natal_broad_status":unique(broader_recruit),
        "verified_breeding_two_colonies_distinct_seasons":len(anonymous)}))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--banding-zip",type=Path,required=True)
    ap.add_argument("--resighting-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    audit(args.banding_zip,args.resighting_zip,args.out)
