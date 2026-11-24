"""Count fingerprint diagnostic against all old Adélie annual site series."""
import json,sys
from pathlib import Path
from collections import Counter,defaultdict
from ross_sea_overlap import acquire,read_new,read_old,norm,distance
OUT=Path("build/ross_sea_fingerprint")
ALIASES={"Coulman Island South":"CSOU","Coulman Island Middle":"CMID","Coulman Island North":"CNOR","Duke of York":"DUKE","Sentry Rock":"SENT","Unger Rock":"UNGE","Chinstrap Island":"CHII"}
def compare(g,old):
    common=sorted(set(g)&set(old));positive=[];values=set();zero=0;diff=[];unknown=0;multi=0;method=Counter()
    for y in common:
        r=old[y]
        if r["count"] is None or r["count"]=="":unknown+=1;continue
        if float(r["count"])==g[y]:
            if g[y]>0:
                positive.append(y);values.add(g[y]);method[r["method"]]+=1
                multi+=int(int(r["n_rows"])>1)
            else:zero+=1
        else:diff.append(y)
    return {"common_years":len(common),"positive_equal":len(positive),"distinct_positive_equal_values":len(values),"equal_zero":zero,"different":len(diff),"unknown":unknown,"missing_old_years":len(set(g)-set(old)),"matching_positive_years":positive,"different_years":diff,"match_method_counts":dict(method),"matches_with_multiple_original_rows":multi}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r={"status":"BLOCKED","independence_established":False,"ecological_fit":False,"raw_counts_exported":False}
    try:
        cb,cm=acquire("counts");lb,lm=acquire("locations")
        new,loc,shape=read_new(cb,lb);sel,annual,sites=read_old(sys.argv[1],sys.argv[2])
        if (len(new),shape["labelled_numeric_cells"],len(sites))!=(39,524,267):raise ValueError("frozen source structure drift")
        olds=defaultdict(dict);names=defaultdict(list)
        for (sid,y),v in annual.items():olds[sid][y]=v
        for sid,v in sites.items():names[norm(v["name"])].append(sid)
        rows=[]
        for key,g in new.items():
            coords=loc.get(key,{}).get("coords")
            exact=names[key]
            geo=bool(len(exact)==1 and coords and distance(coords,sites[exact[0]]["coords"])<=5)
            comparisons=[]
            for sid,old in olds.items():
                a=compare(g["years"],old)
                a.update(site_id=sid,name=sites[sid]["name"],region=sites[sid]["region"],exact_normalized_name=sid in exact,predeclared_alias_candidate=ALIASES.get(g["name"])==sid,distance_km=distance(coords,sites[sid]["coords"]) if coords else None)
                comparisons.append(a)
            qual=[a for a in comparisons if a["positive_equal"]>=2 and a["distinct_positive_equal_values"]>=2]
            strong=[a for a in qual if a["positive_equal"]>=3 and a["distinct_positive_equal_values"]>=3 and a["different"]==0]
            qual.sort(key=lambda a:(-a["positive_equal"],a["different"],a["site_id"]))
            primary=strong[0] if len(strong)==1 else None
            named=[a for a in comparisons if a["exact_normalized_name"] or a["predeclared_alias_candidate"]]
            row={"name":g["name"],"n_records":len(g["years"]),"old_geographic_candidate":geo,"original_exact_name_ids":exact,
                 "predeclared_alias":ALIASES.get(g["name"]),"n_candidates_two_distinct_matches":len(qual),
                 "n_strong_candidates":len(strong),"unique_strong_fingerprint":primary,
                 "multi_year_candidates":qual,"name_or_alias_candidates":named,
                 "n_sites_with_at_least_one_positive_match":sum(a["positive_equal"]>=1 for a in comparisons),
                 "max_exact_positive_matches_any_site":max(a["positive_equal"] for a in comparisons)}
            rows.append(row)
        if sum(x["n_records"] for x in rows)!=524 or sum(x["old_geographic_candidate"] for x in rows)!=17:raise ValueError("prior denominator mismatch")
        groups={"all":rows,"previous_unresolved":[a for a in rows if not a["old_geographic_candidate"]],"previous_geographic_candidates":[a for a in rows if a["old_geographic_candidate"]]}
        counts={}
        for name,v in groups.items():
            strong=[x for x in v if x["unique_strong_fingerprint"]]
            counts[name]={"n_labels":len(v),"n_records":sum(x["n_records"] for x in v),"n_unique_strong":len(strong),
                          "records_in_strong_series":sum(x["n_records"] for x in strong),
                          "positive_matches_unique_strong":sum(x["unique_strong_fingerprint"]["positive_equal"] for x in strong),
                          "no_key_in_unique_strong_candidate":sum(x["unique_strong_fingerprint"]["missing_old_years"] for x in strong),
                          "n_weak_or_ambiguous":sum(x["n_candidates_two_distinct_matches"]>0 and not x["unique_strong_fingerprint"] for x in v),
                          "n_no_multiyear_fingerprint":sum(x["n_candidates_two_distinct_matches"]==0 for x in v)}
        reused=defaultdict(list)
        for a in rows:
            if a["unique_strong_fingerprint"]:reused[a["unique_strong_fingerprint"]["site_id"]].append(a["name"])
        r.update(status="COUNT_FINGERPRINT_DIAGNOSTIC_COMPLETE",source_receipts={"counts":cm,"locations":lm},shape=shape,
                 groups=counts,duplicate_old_site_candidates={k:v for k,v in reused.items() if len(v)>1},rows=rows,
                 n_old_adelie_sites=len(sites),n_old_adelie_annual_records=len(annual))
    except Exception as e:r["error"]=str(e)
    (OUT/"result.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in r.items() if k not in ("rows","shape")},ensure_ascii=False))
    for a in r.get("rows",[]):
        if not a["old_geographic_candidate"]:
            p=a["unique_strong_fingerprint"]
            print(json.dumps({"label":a["name"],"n":a["n_records"],"strong":p,"n_multi_year_candidates":a["n_candidates_two_distinct_matches"],"name_alias_candidates":a["name_or_alias_candidates"]},ensure_ascii=False))
if __name__=="__main__":main()
