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
import statistics
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
    observed_CHIC_site_year_events=defaultdict(list)  # raw animal IDs remain only in memory
    off_natal_resighted=defaultdict(set)
    post_age2_CHIC_seen=defaultdict(set)
    # Original record-availability denominators are observations, NOT survey effort.
    verified_event_rows_by_site_year=Counter()
    strict_nest_event_rows_by_site_year=Counter()
    verified_bands_by_site_year=defaultdict(set)
    strict_nest_bands_by_site_year=defaultdict(set)
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
        if kind=="CHIC" and birthyear>=1994 and yr>=birthyear+2:
            post_age2_CHIC_seen[birthsite].add(tag)
            if observed!=birthsite:
                off_natal_resighted[birthsite,observed].add(tag)
        siteyear=(observed,yr)
        verified_event_rows_by_site_year[siteyear]+=1
        verified_bands_by_site_year[siteyear].add(tag)
        nest=primary_nest(r)
        if kind=="CHIC" and birthyear>=1994 and yr>=birthyear+2:
            observed_CHIC_site_year_events[tag].append((observed,yr,stamp,nest,
                r["status"].strip().upper(),r["nuegg"].strip(),r["nuch"].strip()))
        if nest:
            quality["strict_active_nest_rows"]+=1
            strict_nest_event_rows_by_site_year[siteyear]+=1
            strict_nest_bands_by_site_year[siteyear].add(tag)
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
    n_offsite_seen=unique(off_natal_resighted)
    n_CHIC_post_age2=unique(post_age2_CHIC_seen)
    offsite_visit_nesting_rows=[{
        "original_chick_banding_colony":a,
        "observed_other_colony":b,
        "n_unique_bands_observed_at_other_colony_age2_plus":len(ids),
        "n_unique_bands_with_strict_active_nest_at_other_colony":len(strict_recruit.get((a,b),set()))
      } for (a,b),ids in sorted(off_natal_resighted.items())]
    # A different-colony nest is only documented at the *first observed* breeding
    # season; undetected nesting at a natal colony in an earlier year is possible.
    natal_off_first=0
    natal_off_ever_home=0
    natal_off_same_firstseason_multisite=0
    for tag,at_colonies in active_nests.items():
        born=assignments[tag]
        birthsite,birthyear,kind=born
        if kind!="CHIC" or birthyear<1994:continue
        eligible={s:{y for y in ys if y>=birthyear+2}
                  for s,ys in at_colonies.items()}
        eligible={s:ys for s,ys in eligible.items() if ys}
        if not eligible or not any(s!=birthsite for s in eligible):continue
        earliest=min(y for years in eligible.values() for y in years)
        firstsites={s for s,ys in eligible.items() if earliest in ys}
        if birthsite not in firstsites:natal_off_first+=1
        if birthsite in eligible:natal_off_ever_home+=1
        if len(firstsites)>1:natal_off_same_firstseason_multisite+=1
    years=sorted(verified_event_rows_by_site_year)
    site_year_rows=[{
       "colony":site,"season_start_year":yr,
       "verified_resight_event_rows":verified_event_rows_by_site_year[site,yr],
       "unique_bands_with_verified_resight":len(verified_bands_by_site_year[site,yr]),
       "strict_active_nest_event_rows":strict_nest_event_rows_by_site_year[site,yr],
       "unique_bands_with_strict_active_nest":len(strict_nest_bands_by_site_year[site,yr])
      } for site,yr in years]
    site_observability=[]
    for site0 in sorted(SITES):
        rows0=[r for r in site_year_rows if r["colony"]==site0]
        if not rows0:continue
        site_observability.append({
           "colony":site0,"n_years_with_verified_observations":len(rows0),
           "first_year":rows0[0]["season_start_year"],
           "last_year":rows0[-1]["season_start_year"],
           "verified_resight_events":sum(r["verified_resight_event_rows"] for r in rows0),
           "strict_active_nest_events":sum(r["strict_active_nest_event_rows"] for r in rows0),
           "band_years_with_verified_resighting":sum(r["unique_bands_with_verified_resight"] for r in rows0),
           "band_years_with_strict_nesting":sum(r["unique_bands_with_strict_active_nest"] for r in rows0)})
    if (quality["eligible_verified_rows"],quality["strict_active_nest_rows"],
         natal_off_first,natal_off_ever_home,natal_off_same_firstseason_multisite,
         n_CHIC_post_age2,n_offsite_seen,len(offsite_visit_nesting_rows))!=(
         94678,15157,64,2,0,7132,506,11):
        raise ValueError("Source-locked effort/first-breeding chronology failed")
    # New post-result chronology: original individual-site-year observations, NOT
    # first biological prospecting/natal recruitment dates or movement rates.
    first_away_nesters=set().union(*strict_recruit.values())
    if len(first_away_nesters)!=64 or len(observed_CHIC_site_year_events)!=7132:
        raise ValueError("Offsite stage support changed from pinned original cohort")
    from_colony=defaultdict(Counter)
    observed_gap=Counter()
    first_nest_age=Counter()
    stage_q=Counter()
    for tag in first_away_nesters:
        natal,bandyear,kind=assignments[tag]
        if kind!="CHIC":raise ValueError("Non-chick band in offsite nest cohort")
        ev=observed_CHIC_site_year_events[tag]
        foreign_nests=[(year,site0) for site0,year,dt,is_nest,st,eg,ch in ev
                       if site0!=natal and is_nest]
        if not foreign_nests:raise ValueError("Missing strict foreign nest for eligible band")
        first_nest_year=min(year for year,site0 in foreign_nests)
        first_nest_sites={site0 for year,site0 in foreign_nests if year==first_nest_year}
        if len(first_nest_sites)!=1:
            stage_q["first_nest_year_tied_destination"]+=1
            continue
        destination=next(iter(first_nest_sites))
        from_colony[destination]["nesting_birds"]+=1
        visits=[(year,dt,is_nest,st,eg,ch)
                for site0,year,dt,is_nest,st,eg,ch in ev if site0==destination]
        earliest_visit_year=min(row[0] for row in visits)
        lag=first_nest_year-earliest_visit_year
        if lag<0:raise ValueError("Observed first visit occurs after strict nest year")
        observed_gap[lag]+=1
        first_nest_age[first_nest_year-bandyear]+=1
        if lag>0:
            stage_q["different_year_prior_observed_site_visit"]+=1
            from_colony[destination]["different_year_prior_site_visit"]+=1
            earlier=[v for v in visits if v[0]<first_nest_year]
            if any(eg in ("0","") and ch in ("0","") for year,dt,is_nest,st,eg,ch in earlier):
                stage_q["prior_year_explicit_zero_egg_chick_event"]+=1
            if any(st.startswith("P/") or eg in ("1","2") or ch in ("1","2")
                   for year,dt,is_nest,st,eg,ch in earlier):
                stage_q["prior_year_possible_nest_non_strict_status"]+=1
            else:
                stage_q["prior_year_no_ambiguous_nest_status"]+=1
        else:
            stage_q["first_observed_site_season_already_strict_nesting"]+=1
            from_colony[destination]["first_observed_year_already_nesting"]+=1
        first_nest_date=min(dt for year,dt,is_nest,st,eg,ch in visits
                            if year==first_nest_year and is_nest)
        earlier_this_year=[v for v in visits if v[0]==first_nest_year and
                           v[1]<first_nest_date and not v[2]]
        if earlier_this_year:
            stage_q["same_year_earlier_non_strict_observation"]+=1
            if any(v[4] in ("0","") and v[5] in ("0","") for v in earlier_this_year):
                stage_q["same_year_earlier_zero_egg_chick_event"]+=1
            if any(v[3].startswith("P/") or v[4] in ("1","2") or v[5] in ("1","2")
                   for v in earlier_this_year):
                stage_q["same_year_earlier_possible_nest_non_strict_status"]+=1
        if any(site0!=natal and site0!=destination and year<first_nest_year
               for site0,year,dt,is_nest,st,eg,ch in ev):
            stage_q["earlier_other_foreign_colony_visit"]+=1
        natal_nesting_years=active_nests.get(tag,{}).get(natal,set())
        if natal_nesting_years:
            stage_q["also_documented_natal_strict_nesting"]+=1
            if any(year<first_nest_year for year in natal_nesting_years):
                stage_q["natal_nest_before_foreign_first_nest"]+=1
            if first_nest_year in natal_nesting_years:
                stage_q["natal_nest_same_year_as_foreign_first_nest"]+=1
            if any(year>first_nest_year for year in natal_nesting_years):
                stage_q["natal_nest_after_foreign_first_nest"]+=1
    if (len(first_away_nesters),sum(observed_gap.values()),observed_gap[0],
        sum(n for gap,n in observed_gap.items() if gap>0),
        stage_q["same_year_earlier_non_strict_observation"],
        stage_q["prior_year_possible_nest_non_strict_status"],
        stage_q["also_documented_natal_strict_nesting"],
        stage_q["natal_nest_after_foreign_first_nest"])!=(64,64,41,23,35,14,2,2):
        raise ValueError("Published original stage chronology does not rederive")
    new_stage_summary={
      "source":"USAP-DC 601443/601444 original publisher MD5-verified observations",
      "status":"POST_RESULT_OBSERVED_STAGE_CHRONOLOGY_ONLY",
      "source_all_193638_events_rechecked":quality["original_rows"],
      "original_eligible_resights":quality["eligible_verified_rows"],
      "original_strict_active_nest_events":quality["strict_active_nest_rows"],
      "n_chick_banded_age2_plus_seen":len(observed_CHIC_site_year_events),
      "n_chick_banded_age2_plus_seen_offsite":n_offsite_seen,
      "n_chick_banded_offsite_strict_nest":64,
      "n_prior_year_observed_site_before_offsite_nest":23,
      "n_first_observed_offsite_year_already_strict_nesting":41,
      "observed_site_visit_to_first_nest_year_gap_distribution":dict(sorted(observed_gap.items())),
      "first_documented_foreign_nest_age_distribution_years":dict(sorted(first_nest_age.items())),
      "median_age_at_first_documented_offsite_nest":statistics.median(
          [age for age,n in first_nest_age.items() for _ in range(n)]),
      "operational_stage_qa":dict(stage_q),
      "destination_stage_observation_coverage":{
           k:dict(v) for k,v in sorted(from_colony.items())},
      "limitations":[
           "These are selected detected individuals, NOT an immigration or establishment probability.",
           "Observed visit-to-nest gap is NOT actual biological settling latency.",
           "Earlier P/INC and other ambiguous nest-activity codes are not definitive nonbreeding states.",
           "First observed nesting at a foreign site does not exclude prior undetected nesting elsewhere.",
           "Crozier dominates the destination histories and colony-year observation effort is highly unequal.",
           "Dugger et al 2026 DOI 10.3389/fevo.2026.1868960 already estimates demographic prospecting/recruitment with multistate mark-recapture."],
      "no_raw_individual_ids_or_human_observer_notes_exported":True}
    (outdir/"observed_stage_chronology_no_individual_ids.json").write_text(
        json.dumps(new_stage_summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    save_csv(outdir/"observed_foreign_visit_to_nest_gap_histogram.csv",
             [{"year_gap":year,"n_individuals":n} for year,n in sorted(observed_gap.items())],
             ["year_gap","n_individuals"])
    save_csv(outdir/"first_foreign_nest_observed_age_histogram.csv",
             [{"age_years":age,"n_individuals":n} for age,n in sorted(first_nest_age.items())],
             ["age_years","n_individuals"])
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
      "n_CHIC_post_age2_ever_verified_resighted_any_site":n_CHIC_post_age2,
      "n_CHIC_post_age2_ever_verified_resighted_off_natal":n_offsite_seen,
      "n_off_natal_original_to_other_site_observation_routes":len(offsite_visit_nesting_rows),
      "off_natal_observations_vs_documented_nesting_by_route":offsite_visit_nesting_rows,
      "n_CHIC_off_natal_first_documented_strict_nesting_year":natal_off_first,
      "n_CHIC_off_natal_ever_documented_strict_nesting_at_natal_site":natal_off_ever_home,
      "n_CHIC_off_natal_first_year_multisite_strict_nesting":natal_off_same_firstseason_multisite,
      "n_verified_colony_season_coverage_cells":len(site_year_rows),
      "original_observation_records_by_colony":site_observability,
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
    save_csv(outdir/"anonymous_off_natal_resight_vs_nest_by_route.csv",
             offsite_visit_nesting_rows,
             ["original_chick_banding_colony","observed_other_colony",
              "n_unique_bands_observed_at_other_colony_age2_plus",
              "n_unique_bands_with_strict_active_nest_at_other_colony"])
    save_csv(outdir/"anonymous_colony_season_record_availability.csv",site_year_rows,
             ["colony","season_start_year","verified_resight_event_rows",
              "unique_bands_with_verified_resight","strict_active_nest_event_rows",
              "unique_bands_with_strict_active_nest"])
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
        "verified_breeding_two_colonies_distinct_seasons":len(anonymous),
        "prior_year_observed_same_foreign_colony_before_nesting":23,
        "same_first_observed_foreign_colony_season_already_nesting":41,
        "first_documented_chick_off_natal_nesting":natal_off_first,
        "chick_banded_resighted_any_colony_age2_plus":n_CHIC_post_age2,
        "chick_banded_resighted_off_natal_age2_plus":n_offsite_seen,
        "source_verified_events":quality["eligible_verified_rows"],
        "source_verified_strict_nest_events":quality["strict_active_nest_rows"],
        "n_colony_season_availability_cells":len(site_year_rows)}))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--banding-zip",type=Path,required=True)
    ap.add_argument("--resighting-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    audit(args.banding_zip,args.resighting_zip,args.out)
