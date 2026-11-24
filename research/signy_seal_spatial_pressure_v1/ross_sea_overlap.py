"""Compare Ross Sea aerial census with both prior MAPPPD annual archives.
No raw new counts are exported. No ecological trends or independent-event claim.
"""
import base64,csv,hashlib,io,json,math,re,sys,unicodedata,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from openpyxl import load_workbook
from ross_sea_source_audit import BASE,DATASET,SOURCES,fetch,sha,LEGACY_PIN

OUT=Path("build/ross_sea_overlap")
PINS={"counts":"23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6",
      "locations":"d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6"}
OLD_BLOB="fc134e364cf38699fa7611d7dee5fbbbcb370c0a"
GEO_MAX_KM=5.0

def norm(s):
    return "".join(c for c in unicodedata.normalize("NFKC",str(s)).casefold() if c.isalnum())

def present(x):
    return x is not None and (not isinstance(x,str) or bool(x.strip()))

def number(x):
    if isinstance(x,bool):raise ValueError("boolean count")
    v=float(x)
    if not math.isfinite(v) or v<0 or not v.is_integer():raise ValueError("not a nonnegative integer count")
    return int(v)

def dms(v):
    s=unicodedata.normalize("NFKC",str(v)).strip().upper()
    sign=-1 if s[-1:] in ("S","W") else 1
    if s[-1:] not in ("N","S","E","W"):return None
    parts=re.findall(r"\d+(?:\.\d+)?",s[:-1])
    if not 1<=len(parts)<=3:return None
    d,m,ss=([float(x) for x in parts]+[0,0])[:3]
    if m>=60 or ss>=60 or d>180:return None
    x=sign*(d+m/60+ss/3600)
    return x

def distance(a,b):
    lat1,lon1,lat2,lon2=map(math.radians,(*a,*b))
    t=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(min(1,max(0,t))))

def acquire(role):
    uid,name=SOURCES[role]
    u=f"{BASE}/dataset/{DATASET}/resource/{uid}/download/{name}"
    b,ru=fetch(u)
    if sha(b)!=PINS[role]:raise ValueError(role+" original file drift")
    if role=="counts" and hashlib.md5(b).hexdigest()!="195a9027a0d18012812b09fb345ac60e":
        raise ValueError("publisher MD5 mismatch")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError("workbook CRC")
    return b,{"url":ru,"bytes":len(b),"sha256":sha(b)}

def read_new(count_bytes,location_bytes):
    w=load_workbook(io.BytesIO(count_bytes),read_only=True,data_only=True)
    if w.sheetnames!=["All data"]:raise ValueError("new census sheet")
    it=iter(w["All data"].values);h=next(it)
    if h[0]!="Colony" or tuple(int(v) for v in h[1:45])!=tuple(range(1981,2025)) or any(present(v) for v in h[45:]):
        raise ValueError("new census header")
    # The verified year header defines the table A:AS (45 columns).
    # Inventory auxiliary nonblank cells, but do not interpret them as census events.
    # Candidate overlap only: ancillary annotations require later semantic review.
    out={}; blanks=0; zeros=0; auxiliary=[]; quarantined=[]; table_rows=0
    for rownum,row in enumerate(it,2):
        for j,v in enumerate(row[45:],46):
            if present(v):
                aux={"row":rownum,"column":j,"type":type(v).__name__}
                if isinstance(v,str) and not re.fullmatch(r"[+\-]?\d+(?:[.,]\d+)?",v.strip()):
                    aux["text_annotation_candidate"]=v[:250]
                auxiliary.append(aux)
        if not any(present(v) for v in row[:45]):continue
        table_rows+=1
        name=row[0].strip() if isinstance(row[0],str) and row[0].strip() else None
        vals={}
        for y,v in zip(range(1981,2025),row[1:45]):
            if not present(v):blanks+=1;continue
            if not isinstance(v,(int,float)):raise ValueError("non-numeric observed cell")
            n=number(v);vals[y]=n;zeros+=n==0
        if name is None:
            quarantined.append({"row":rownum,"label_type":type(row[0]).__name__,"years":vals})
            continue
        key=norm(name)
        if key in out:raise ValueError("duplicate normalized colony name")
        out[key]={"name":name,"years":vals}
    w.close()
    labelled=sum(len(v["years"]) for v in out.values())
    unlabeled=sum(len(v["years"]) for v in quarantined)
    if table_rows!=40 or labelled+unlabeled!=525 or blanks!=1235:
        raise ValueError("count schema/coverage drift")
    # Diagnose every unlabeled row, never count it as a colony or export its raw values.
    quarantine_receipts=[]
    for qr in quarantined:
        diag=[]
        for y,n in qr["years"].items():
            v=[g["years"][y] for g in out.values() if y in g["years"]]
            diag.append({"year":y,"n_labelled_numeric_cells":len(v),
                         "equals_labelled_sum":bool(v) and n==sum(v),
                         "equals_labelled_cell_count":n==len(v),
                         "equals_labelled_max":bool(v) and n==max(v)})
        quarantine_receipts.append({"row":qr["row"],"label_type":qr["label_type"],
                                    "n_numeric_cells":len(qr["years"]),"zero_cells":sum(v==0 for v in qr["years"].values()),"aggregate_diagnostic":diag})
    w=load_workbook(io.BytesIO(location_bytes),read_only=True,data_only=True)
    if w.sheetnames!=["Sheet1"]:raise ValueError("location sheet")
    loc={}
    for row in w["Sheet1"].values:
        if not any(present(v) for v in row):continue
        name,area,lat,lon=row
        if not isinstance(name,str) or not name.strip():raise ValueError("location key")
        k=norm(name)
        if k in loc:raise ValueError("duplicate location name")
        a,b=dms(lat),dms(lon)
        coords=[a,b] if a is not None and b is not None and -90<=a<=-55 and -180<=b<=180 else None
        loc[k]={"area":area,"coords":coords,"name":name}
    w.close()
    return out,loc,{"n_labels":len(out),"table_rows":table_rows,"numeric_cells":525,
                    "labelled_numeric_cells":labelled,"quarantined_numeric_cells":unlabeled,
                    "quarantined_unlabelled_rows":quarantine_receipts,
                    "blank_cells":blanks,"explicit_zero_cells_all_rows":zeros,
                    "table_range":"A1:AS41","auxiliary_nonblank_cells":auxiliary,
                    "auxiliary_semantics_review_required":bool(auxiliary),
                    "location_rows":len(loc),"location_label_overlap":len(set(out)&set(loc)),
                    "count_labels_without_location":[v["name"] for k,v in out.items() if k not in loc],
                    "location_labels_without_count":[v["name"] for k,v in loc.items() if k not in out],
                    "coordinate_parse_failed":[v["name"] for v in loc.values() if v["coords"] is None]}

def read_old(selected_path,blob_path):
    b=Path(selected_path).read_bytes()
    if sha(b)!=LEGACY_PIN:raise ValueError("selected archive drift")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError("selected CRC")
        s=list(csv.DictReader(io.StringIO(z.read("source_observed_2456.csv").decode("utf-8-sig"))))
    if len(s)!=2456 or len({(x["site_id"],x["species"],x["season"]) for x in s})!=2456:
        raise ValueError("selected keys")
    j=json.loads(Path(blob_path).read_text())
    if j["sha"]!=OLD_BLOB or j["encoding"]!="base64":raise ValueError("old blob identity")
    raw=base64.b64decode(j["content"])
    if hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()!=OLD_BLOB:raise ValueError("old blob bytes")
    a=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(a)!=2999 or len({(x["site_id"],x["species_id"],x["season"]) for x in a})!=2999:
        raise ValueError("annual archive keys")
    sel={(r["site_id"],int(r["season"])):r for r in s if r["species"]=="ADPE"}
    allr={(r["site_id"],int(r["season"])):r for r in a if r["species_id"]=="ADPE"}
    if not set(sel)<=set(allr):raise ValueError("selected not subset of annual archive")
    for key,r in sel.items():
        if float(r["observed_nest_count"])!=float(allr[key]["count"]):raise ValueError("old archive count mismatch")
    sites={}
    for (site,y),r in allr.items():
        d={"site_id":site,"name":r["site_name"],"region":r["region"],"coords":[float(r["latitude"]),float(r["longitude"])]}
        if site in sites and sites[site]!=d:raise ValueError("old site metadata conflict")
        sites[site]=d
    return sel,allr,sites

def classify(old,count,field,method):
    if old is None:return "NO_KEY_IN_ARCHIVE"
    if not old.get(field):return "KEY_PRESENT_COUNT_UNKNOWN"
    same=float(old[field])==count
    aerial=str(old[method]).strip().casefold() in ("aerial","aerial photo")
    return ("EQUAL" if same else "DIFFERENT")+"_COUNT_"+("AERIAL_FAMILY" if aerial else "OTHER_METHOD")

def run(new,loc,sel,allr,sites):
    byname=defaultdict(list)
    for d in sites.values():byname[norm(d["name"])].append(d)
    rows=[];summary=Counter();selected=Counter();annual=Counter()
    recent={str(y):{"new_numeric_cells":0,"selected":Counter(),"annual":Counter()} for y in range(1981,2025)}
    for key,g in new.items():
        rec={"name":g["name"],"n_numeric_cells":len(g["years"]),"first_observed":min(g["years"]) if g["years"] else None,
             "last_observed":max(g["years"]) if g["years"] else None}
        coords=loc.get(key,{}).get("coords")
        match=byname.get(key,[])
        rec["exact_name_candidate_ids"]=[d["site_id"] for d in match]
        status="UNRESOLVED_NAME_OR_GEOMETRY"
        if len(match)==1 and coords is not None:
            d=match[0];gap=distance(coords,d["coords"])
            rec.update(candidate_old_id=d["site_id"],candidate_old_region=d["region"],distance_km=gap)
            if gap<=GEO_MAX_KM:status="EXACT_NAME_WITHIN_5KM_CANDIDATE"
        if status!="EXACT_NAME_WITHIN_5KM_CANDIDATE" and coords is not None:
            rec["nearby_candidates_for_manual_review_only"]=[
                {"site_id":d["site_id"],"name":d["name"],"distance_km":dist}
                for d in sites.values() if (dist:=distance(coords,d["coords"]))<=10]
        rec["mapping_status"]=status
        summary[status]+=1
        sc=Counter();ac=Counter()
        for year,count in g["years"].items():
            if status=="EXACT_NAME_WITHIN_5KM_CANDIDATE":
                k=(rec["candidate_old_id"],year)
                c1=classify(sel.get(k),count,"observed_nest_count","original_survey_method")
                c2=classify(allr.get(k),count,"count","method")
            else:c1=c2="UNRESOLVED_SITE_MAPPING"
            sc[c1]+=1;ac[c2]+=1
            recent[str(year)]["new_numeric_cells"]+=1
            recent[str(year)]["selected"][c1]+=1;recent[str(year)]["annual"][c2]+=1
        rec["selected_archive_classes"]=dict(sc);rec["annual_archive_classes"]=dict(ac)
        selected.update(sc);annual.update(ac);rows.append(rec)
    expected=sum(len(v["years"]) for v in new.values())
    if sum(selected.values())!=expected or sum(annual.values())!=expected:raise ValueError("labelled classification denominator")
    # Exact names are only candidates. Check noninjective candidate mapping.
    ids=[r["candidate_old_id"] for r in rows if r["mapping_status"]=="EXACT_NAME_WITHIN_5KM_CANDIDATE"]
    if len(ids)!=len(set(ids)):raise ValueError("noninjective candidate mapping")
    return {"site_mapping":dict(summary),"selected_archive_classes":dict(selected),"annual_archive_classes":dict(annual),
            "year_classification":recent,"colony_summaries":rows,
            "old_selected_ADPE_rows":len(sel),"old_annual_ADPE_rows":len(allr),
            "old_selected_Victoria_ADPE_rows":sum(r["source_region"]=="Victoria Land" for r in sel.values()),
            "old_annual_Victoria_ADPE_rows":sum(r["region"]=="Victoria Land" for r in allr.values())}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result={"status":"BLOCKED","doi":"10.7931/kf06-x745","source_pins":PINS,
            "old_annual_git_blob":OLD_BLOB,"distance_gate_km":GEO_MAX_KM,
            "independence_established":False,"ecological_fit":False,"new_raw_count_values_exported":False,
            "notes":["Exact name and distance are a candidate site crosswalk, not verified event lineage.",
                     "Equal counts and aerial-family methods strongly flag potential reuse; no independent events certified.",
                     "NO_KEY means not in selected or previously consolidated annual archive, not absent from full publisher observations.",
                     "Parent/subcolony footprint and survey dates remain unresolved; no nearby match is accepted automatically."]}
    try:
        cb,cm=acquire("counts");lb,lm=acquire("locations");result["source_receipts"]={"counts":cm,"locations":lm}
        new,loc,shape=read_new(cb,lb);result["new_structure"]=shape
        sel,allr,sites=read_old(sys.argv[1],sys.argv[2])
        result.update(run(new,loc,sel,allr,sites))
        # Account for every numeric cell, including the explicitly quarantined unlabeled row.
        for key in ("selected_archive_classes","annual_archive_classes"):
            if shape["quarantined_numeric_cells"]:
                result[key]["UNLABELLED_ROW_QUARANTINED"]=shape["quarantined_numeric_cells"]
            if sum(result[key].values())!=525:raise ValueError("total classification denominator")
        for row in shape["quarantined_unlabelled_rows"]:
            for event in row["aggregate_diagnostic"]:
                yr=result["year_classification"][str(event["year"])]
                yr["new_numeric_cells"]+=1
                for key in ("selected","annual"):yr[key]["UNLABELLED_ROW_QUARANTINED"]+=1
        result["status"]="CANDIDATE_OVERLAP_AUDIT_COMPLETE_WITH_QUARANTINE"
    except Exception as e:result["error"]=str(e)
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("year_classification","colony_summaries")},ensure_ascii=False))
if __name__=="__main__":main()
