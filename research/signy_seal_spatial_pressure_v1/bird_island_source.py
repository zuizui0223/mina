"""Source-only Bird Island nest monitoring intake, no count outcomes in receipt."""
import csv,io,hashlib,json,math,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlparse
import requests
OUT=Path("build/bird_island_source")
ENTRY="8fedb5a0-b98c-4457-9d86-aae9c6d3ed8e"
URL=f"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={ENTRY}&output=zip.tree"
def sha(b):return hashlib.sha256(b).hexdigest()
def present(s):return bool(str(s).strip()) and str(s).strip().lower() not in {"na","nan","n/a","null","none"}
def norm(s):return re.sub(r"[^a-z0-9]+","",str(s).lower())
def acquire():
    with requests.get(URL,timeout=(20,90),stream=True,allow_redirects=False) as r:
        r.raise_for_status()
        if r.is_redirect:raise ValueError("unreviewed redirect "+r.headers.get("Location",""))
        if urlparse(r.url).hostname!="ramadda.data.bas.ac.uk":raise ValueError("unexpected source hostname")
        b=bytearray()
        for p in r.iter_content(65536):
            b.extend(p)
            if len(b)>20_000_000:raise ValueError("bounded original source")
    return bytes(b)
def inventory(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError("archive CRC")
        if sum(x.file_size for x in z.infolist())>50_000_000:raise ValueError("bounded expanded size")
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1:raise ValueError("original dataset expected exactly one CSV: "+str(names))
        raw=z.read(names[0]); files=[{"name":i.filename,"bytes":i.file_size} for i in z.infolist()]
    for enc in ["utf-8-sig","latin-1"]:
        try:t=raw.decode(enc);break
        except UnicodeDecodeError:continue
    rr=list(csv.reader(io.StringIO(t,newline="")))
    # Select actual header by names, never numerical outcomes.
    headers=[i for i,row in enumerate(rr[:20]) if any("season" in norm(x) or norm(x)=="year" for x in row) and any("nest" in norm(x) or "pair" in norm(x) for x in row)]
    if len(headers)!=1:
        return {"status":"HEADER_REVIEW_REQUIRED","members":files,"csv_member":names[0],"csv_sha256":sha(raw),
                "header_candidates":[[x[:100] if not re.search(r"\d",x) else "[contains digits]" for x in row] for row in rr[:3]]},raw
    h=[x.strip() for x in rr[headers[0]]]
    if len(set(h))!=len(h):raise ValueError("duplicate headers")
    rows=[];width=Counter();repairs=0
    for row in rr[headers[0]+1:]:
        if not any(x.strip() for x in row):continue
        width[len(row)]+=1
        if len(row)>len(h):
            if "comment" not in norm(h[-1]):continue
            row=row[:len(h)-1]+[",".join(row[len(h)-1:])];repairs+=1
        if len(row)<len(h):continue
        rows.append(dict(zip(h,[v.strip() for v in row])))
    season=[x for x in h if "season" in norm(x) or norm(x)=="year"]
    colony=[x for x in h if norm(x) in {"colony","colonyname","site","sitename","location","colonyid"}]
    nest=[x for x in h if ("nest" in norm(x) or "pair" in norm(x)) and not any(k in norm(x) for k in ["date","day","success","ratio","per","percent"])]
    summary={"status":"SOURCE_ACQUIRED_SCHEMA_REVIEW_REQUIRED","members":files,"csv_member":names[0],"csv_sha256":sha(raw),"csv_bytes":len(raw),"encoding":enc,
             "header_line":headers[0]+1,"headers":h,"valid_width_rows":len(rows),"source_width_counts":dict(width),"repaired_comment_rows":repairs,
             "season_field_candidates":season,"colony_field_candidates":colony,"nest_field_candidates":nest,
             "missing_by_field":{k:sum(not present(row[k]) for row in rows) for k in h},"count_magnitudes_exposed":False}
    def valid_nonnegative(v):
        try:n=float(v.replace(",",""));return math.isfinite(n) and n>=0 and n.is_integer()
        except (ValueError,TypeError):return False
    if len(season)==1:
        summary["literal_seasons"]=dict(sorted(Counter(row[season[0]] for row in rows).items()))
    if len(colony)==1:
        summary["literal_colonies"]=dict(sorted(Counter(row[colony[0]] for row in rows).items()))
    if len(colony)==1 and len(season)==1:
        keys=[(row[colony[0]],row[season[0]]) for row in rows]
        summary["duplicate_colony_season_keys"]=[list(k) for k,n in Counter(keys).items() if n>1]
        summary["presence_by_nest_field"]={}
        for n in nest:
            p=defaultdict(set)
            for row in rows:
                if present(row[colony[0]]) and present(row[season[0]]) and valid_nonnegative(row[n]):p[row[colony[0]]].add(row[season[0]])
            summary["presence_by_nest_field"][n]={k:sorted(v) for k,v in sorted(p.items())}
    elif len(season)==1:
        summary["presence_by_possible_wide_nest_field"]={n:sorted({r[season[0]] for r in rows if valid_nonnegative(r[n])}) for n in nest}
    return summary,raw
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result={"status":"BLOCKED_SOURCE","doi":"10.5285/"+ENTRY,"source_url":URL,"license":"Open Government Licence v3 (provider metadata)","ecological_fit":False,"climate_test":False}
    try:
        b=acquire();result["archive_sha256"]=sha(b);result["archive_bytes"]=len(b)
        s,raw=inventory(b);result.update(s)
        # Archive original open-data bytes separately from the receipt, never git.
        (OUT/"original_source.zip").write_bytes(b)
    except Exception as e:result["error"]=f"{type(e).__name__}: {e}"
    (OUT/"receipt.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
