#!/usr/bin/env python3
"""Observed real-zero -> recorded-positive penguin nesting transition audit.

Original 2999 unambiguous MAPPPD nests site×species×season rows; reconstruct
fixed-method exact source counts and audit every one of 2456 rows against the
original publisher-derived source ZIP. A recorded zero is not unknown survey
effort nor proof of true species absence, founding, or population colonization.

Disclose all 35 consecutive-record status transitions. The "sustained-recorded"
classification is a follow-up QA descriptor: first source zero, first positive
observed later, >=4 post-event positive source censuses, zero subsequent
recorded zero; this is conditioned on unequal resurvey intensity and NOT a
colonization probability or survival estimator. Cluster geographic endpoints
at 2 and 10 km to avoid pseudo-independent nearby colonies.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,zipfile
from collections import defaultdict,Counter
from pathlib import Path

ORIGINAL_BLOB_SHA1="fc134e364cf38699fa7611d7dee5fbbbcb370c0a"
SP=("ADPE","CHPE","GEPE")
FOLLOWUP=4
DISTANCES=(2.0,10.0)

def blob(path):
    x=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\0"+x).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csvread(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
def zipread(path,member):
    with zipfile.ZipFile(path) as f:
        assert f.testzip() is None
        return list(csv.DictReader(io.StringIO(f.read(member).decode("utf-8-sig"))))
def write_csv(path,rows,cols):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader();w.writerows(rows)
def coordinate_km(x,y):
    a=math.radians(float(x["latitude"]));b=math.radians(float(y["latitude"]))
    da=b-a;dl=math.radians(float(y["longitude"])-float(x["longitude"]))
    v=math.sin(da/2)**2+math.cos(a)*math.cos(b)*math.sin(dl/2)**2
    return 6371.0088*2*math.atan2(math.sqrt(v),math.sqrt(max(0.,1-v)))
def clusters(points,distance):
    parent={x["site_id"]:x["site_id"] for x in points}
    def root(s):
        while parent[s]!=s:
            parent[s]=parent[parent[s]]
            s=parent[s]
        return s
    for i,p in enumerate(points):
        for q in points[i+1:]:
            if coordinate_km(p,q)<distance:
                ra,rb=root(p["site_id"]),root(q["site_id"])
                parent[max(ra,rb)]=min(ra,rb)
    comp=defaultdict(list)
    for p in points:comp[root(p["site_id"])].append(p["site_id"])
    return sorted([sorted(v) for v in comp.values()],key=lambda x:x[0])

def rebuild_and_validate(raw_file,countzip):
    if blob(raw_file)!=ORIGINAL_BLOB_SHA1:
        raise ValueError("STOP: original site-season source blob changed")
    raw=csvread(raw_file)
    assert len(raw)==2999
    methods=defaultdict(Counter);valid=[]
    for r in raw:
        if r["species_id"] not in SP:continue
        if r["n_methods"]!="1" or r["method"].strip() in ("","unknown"):continue
        if r["count"].strip()=="":continue
        n=float(r["count"])
        if not math.isfinite(n) or n<0 or not n.is_integer():
            raise ValueError("Noninteger or negative genuine original nests")
        valid.append(r)
        methods[(r["site_id"],r["species_id"])][r["method"]]+=1
    assert len(valid)==2724 and len(methods)==707
    most={k:sorted(v.items(),key=lambda x:(-x[1],x[0]))[0][0]
          for k,v in methods.items()}
    reconstructed={}
    for r in valid:
        site=r["site_id"];sp=r["species_id"];y=int(r["season"])
        if r["method"]!=most[(site,sp)]:continue
        key=(site,sp,y)
        if key in reconstructed:raise ValueError("Original site-species-season duplicate")
        reconstructed[key]=r
    assert len(reconstructed)==2456
    original=zipread(countzip,"source_observed_2456.csv")
    inventory=zipread(countzip,"panantarctic_595_site_inventory.csv")
    assert len(original)==2456 and len(inventory)==595
    seen=set();grouped=defaultdict(list)
    for r in original:
        site=r["site_id"];sp=r["species"];y=int(r["season"])
        key=(site,sp,y)
        if key not in reconstructed or key in seen:
            raise ValueError("Publisher source key differs from strict original")
        seen.add(key);q=reconstructed[key]
        assert r["original_survey_method"]==q["method"]
        assert r["source_region"]==q["region"]
        assert float(r["observed_nest_count"])==float(q["count"])
        assert float(r["latitude"])==float(q["latitude"])
        assert float(r["longitude"])==float(q["longitude"])
        assert str(r["site_name"])==q["site_name"]
        r["observed_nest_count"]=int(float(r["observed_nest_count"]))
        r["season"]=y
        grouped[(site,sp)].append(r)
    assert seen==set(reconstructed)
    assert len(grouped)==707
    return grouped,inventory

def audit(grouped):
    events=[];candidate=[]
    for (site,sp),grp in sorted(grouped.items()):
        g=sorted(grp,key=lambda r:r["season"])
        assert len({r["season"] for r in g})==len(g)
        status=lambda r:r["observed_nest_count"]>0
        first=g[0]
        for i in range(1,len(g)):
            before=g[i-1];after=g[i]
            if status(before)==status(after):continue
            post=g[i:]
            post_pos=[r for r in post if status(r)]
            post_zero=[r for r in post if not status(r)]
            previous_pos=[r for r in g[:i] if status(r)]
            first_zero_no_prior_positive=not status(first) and not previous_pos
            sustained=bool(
               not status(before) and status(after) and
               first_zero_no_prior_positive and len(post_pos)>=FOLLOWUP and
               len(post_zero)==0
            )
            d={
              "site_id":site,"site_name":after["site_name"],
              "species":sp,"source_region":after["source_region"],
              "original_survey_method":after["original_survey_method"],
              "latitude":float(after["latitude"]),
              "longitude":float(after["longitude"]),
              "transition":"observed_0_to_positive" if not status(before) else "observed_positive_to_0",
              "last_previous_census_season":before["season"],
              "first_changed_census_season":after["season"],
              "inter_census_gap_years":after["season"]-before["season"],
              "previous_observed_nests":before["observed_nest_count"],
              "changed_observed_nests":after["observed_nest_count"],
              "n_counted_years_at_site_species":len(g),
              "n_followup_source_censuses_including_changed_season":len(post),
              "n_followup_positive_censuses":len(post_pos),
              "n_followup_zero_censuses":len(post_zero),
              "n_positive_censuses_before_transition":len(previous_pos),
              "first_ever_source_census_was_recorded_zero":bool(not status(first)),
              "four_positive_followups_without_recorded_zero_from_initial_recorded_zero":sustained,
              "last_positive_census_year":post_pos[-1]["season"] if post_pos else None,
              "max_post_transition_positive_observed_nests":max(
                     [r["observed_nest_count"] for r in post_pos],default=None),
              "no_unobserved_year_imputed_zero":True,
              "transition_does_not_prove_new_colony_founding":True
            }
            events.append(d)
            if sustained:candidate.append(d)
    return events,candidate

def metrics(grouped,events,consistent):
    allrecords=[r for v in grouped.values() for r in v]
    zero=[r for r in allrecords if r["observed_nest_count"]==0]
    assert len(allrecords)==2456 and len(zero)==98
    zero_series={k for k,v in grouped.items() if any(r["observed_nest_count"]==0 for r in v)}
    assert len(zero_series)==46
    assert len(events)==35
    assert Counter(r["transition"] for r in events)=={
      "observed_positive_to_0":20,"observed_0_to_positive":15}
    assert len(consistent)==5
    assert all(r["species"]=="GEPE" and r["source_region"]=="Central-west Antarctic Peninsula"
                for r in consistent)
    assert {r["site_id"] for r in consistent}=={"BISC","GALE","ORNE","TXRX","VERN"}
    assert [x["n_followup_positive_censuses"] for x in sorted(consistent,key=lambda x:x["site_id"]) ]==[16,6,10,6,6]
    b=sorted(consistent,key=lambda z:z["site_id"])
    return {
      "status":"PASS_REAL_ZERO_TO_POSITIVE_SOURCE_SURVEY_TRANSITION_AUDIT",
      "original_source_unambiguous_site_species_seasons":2999,
      "original_method_eligible_rows":2724,
      "original_method_selected_nest_counts":len(allrecords),
      "original_unique_site_species_series":len(grouped),
      "recorded_zero_nest_census_rows":len(zero),
      "site_species_series_with_recorded_zero":len(zero_series),
      "unique_site_species_with_observed_transition":
          len({(r["site_id"],r["species"]) for r in events}),
      "all_observed_adjacent_census_status_transitions":len(events),
      "zero_to_positive_transition_events":
          sum(r["transition"]=="observed_0_to_positive" for r in events),
      "positive_to_zero_transition_events":
          sum(r["transition"]=="observed_positive_to_0" for r in events),
      "predefined_sustained_observed_positive_with_first_recorded_zero_criteria":{
          "earliest_original_observation_zero":True,
          "positive_after_zero":True,
          "at_least_post_change_positive_censuses":FOLLOWUP,
          "no_observed_zero_after_first_positive":True,
          "never_infer_unsurveyed_years":True,
          "resurvey_followup_conditioning_not_probability":True
      },
      "sustained_positive_source_site_ids":[r["site_id"] for r in b],
      "sustained_source_site_count":len(b),
      "sustained_distinct_geographic_groups_under2km":clusters(b,2),
      "sustained_distinct_geographic_groups_under10km":clusters(b,10),
      "n_original_regions_with_sustained_cases":len({r["source_region"] for r in b}),
      "single_region_replicate_not_panantarctic_generalization":True,
      "not_source_census_same_colony_polygon_or_detection_effort_guarantee":True,
      "recorded_zero_not_assumed_species_absence_offsite":True,
      "not_true_foundation_or_discovery_date":True,
      "not_a_climate_causal_inference":True
    }

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--original-source",type=Path,required=True)
    pa.add_argument("--count-zip",type=Path,required=True)
    pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    grouped,inventory=rebuild_and_validate(a.original_source,a.count_zip)
    events,consistent=audit(grouped)
    report=metrics(grouped,events,consistent)
    report["original_2999_source_blob_sha1"]=blob(a.original_source)
    report["original_2456_archive_sha256"]=sha(a.count_zip)
    cols=list(events[0])
    write_csv(a.out/"all_35_original_nest_status_transitions.csv",events,cols)
    write_csv(a.out/"five_persistent_after_recorded_zero_gentoo_source_sites.csv",
              sorted(consistent,key=lambda r:r["site_id"]),cols)
    (a.out/"original_penguin_nest_zero_to_positive_transition_receipt.json").write_text(
      json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PENGUIN_SOURCE_ZERO_TO_POSITIVE_AUDIT="+json.dumps(report,ensure_ascii=False),flush=True)

def selftest():
    dummy=[{"site_id":"A","latitude":-65.,"longitude":-64.},
           {"site_id":"B","latitude":-65.0003,"longitude":-64.0004},
           {"site_id":"C","latitude":-62.,"longitude":-58.}]
    assert len(clusters(dummy,2))==2
    assert coordinate_km(dummy[0],dummy[1])<0.1
    print("PASS original-transition geography cluster and stable distance arithmetic")

if __name__=="__main__":
    import sys
    if len(sys.argv)==2 and sys.argv[1]=="--self-test":selftest()
    else:main()
