"""Public source inventory for an independent historic-colony comparison.
No spatial outcomes, no requests for restricted file bytes, no form submissions.
"""
import concurrent.futures as cf
import hashlib,json,pathlib,re,sys,urllib.request,urllib.parse
from html.parser import HTMLParser
OUT=pathlib.Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
HOST="https://data.aad.gov.au"
PARENT="AAS_4088_Adelie_breeding_colony_boundaries"
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"mina-public-source-inventory/1.0","Accept":"application/json,text/html,*/*"})
    with urllib.request.urlopen(req,timeout=25) as r:
        b=r.read(5000001)
        if len(b)>5000000:raise ValueError("size cap")
        return b
class Parse(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.text=[];self.skip=0
    def handle_starttag(self,t,attrs):
        if t in ("script","style"):self.skip+=1
        if t=="a":
            h=dict(attrs).get("href")
            if h:self.links.append(h)
    def handle_endtag(self,t):
        if t in ("script","style"):self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip and d.strip():self.text.append(d.strip())
def parse(b):
    p=Parse();p.feed(b.decode("utf-8","replace"));return p
def metadata(entry):
    result={"entry":entry}
    try:
        b=fetch(HOST+"/metadata/records/"+entry);p=parse(b);t=" ".join(p.text)
        ids=sorted(set(int(x) for a in p.links for x in re.findall(r"/eds/(\d+)/download",a)))
        result.update(status="ok",sha256=hashlib.sha256(b).hexdigest(),eds=ids)
        for h,end in [("Description","Quality"),("Quality","Access"),("Temporal Coverages","Spatial Coverages")]:
            # choose heading after metadata text, not nav
            txt=t.split(h,1)[-1].split(end,1)[0]
            result[h.lower()]=txt[:3500]
        (OUT/(entry+".html")).write_bytes(b)
    except Exception as e:result.update(status="failed",error=repr(e)[:250])
    return result
def objects(i):
    result={"eds":i}
    try:
        b=fetch(HOST+f"/eds/api/dataset/{i}/objects?recursive=true&removeBasePath=true")
        rows=json.loads(b);assert isinstance(rows,list)
        result.update(status="ok",count=len(rows),sha256=hashlib.sha256(b).hexdigest(),objects=[{k:x.get(k) for k in ("name","size") if k in x} for x in rows])
        (OUT/f"eds_{i}.json").write_bytes(b)
    except Exception as e:result.update(status="failed",error=repr(e)[:250])
    return result
def main():
    b=fetch(HOST+"/metadata/records/"+PARENT)
    children=sorted(set(re.findall(r"AAS_4088_Adelie_occupancy_[A-Za-z0-9_-]+"," ".join(parse(b).links))))
    search={}
    # Catalogues only; identify exact Whitney entry from authoritative catalogue, not a guessed dataset id.
    for key,query in [("eds","Whitney Point"),("datacite","Whitney Point Adelie Penguin Colonies")]:
        try:
            u=(HOST+"/eds/api/dataset?"+urllib.parse.urlencode({"search":query,"size":50})) if key=="eds" else ("https://api.datacite.org/dois?"+urllib.parse.urlencode({"query":'titles.title:"Whitney Point Adelie Penguin Colonies"',"page[size]":20}))
            raw=fetch(u);j=json.loads(raw);(OUT/(key+"_search.json")).write_bytes(raw)
            if key=="datacite":
                search[key]=[{"doi":x["id"],"titles":x["attributes"].get("titles"),"url":x["attributes"].get("url")} for x in j.get("data",[])]
            else:
                if isinstance(j,list):rows=j
                else:rows=next((v for k,v in j.items() if k in ["content","items","data","results","datasets"] and isinstance(v,list)),[])
                search[key]=[{"eds":x.get("eds_id"),"name":x.get("dataset_name"),"entry":x.get("metadata_entry_id"),"status":x.get("dataset_visibility_status")} for x in rows if isinstance(x,dict)]
        except Exception as e:search[key]={"error":repr(e)[:250]}
    extra=[]
    for x in search.get("datacite",[]) if isinstance(search.get("datacite"),list) else []:
        if "Whitney Point Adelie Penguin Colonies" in str(x.get("titles")):
            extra+=re.findall(r"ASAC_[A-Za-z0-9_]+",x.get("url") or "")
    for x in search.get("eds",[]) if isinstance(search.get("eds"),list) else []:
        if "Whitney" in str(x.get("name")) and x.get("entry"):extra.append(x["entry"])
    with cf.ThreadPoolExecutor(max_workers=5) as p: rows=list(p.map(metadata,sorted(set(children+extra))))
    ids=sorted(set(i for r in rows for i in r.get("eds",[])))
    with cf.ThreadPoolExecutor(max_workers=5) as p: objs=list(p.map(objects,ids))
    rec={"scope":"public catalogue, not acquired geometries or fitted ecological effects","children_count":len(children),"whitney_discovery":search,"records":rows,"objects":objs}
    (OUT/"receipt.json").write_text(json.dumps(rec,indent=2))
    print("WHITNEY",json.dumps(search),flush=True)
    for r in rows:print("RECORD",json.dumps(r,ensure_ascii=False)[:5000],flush=True)
    for r in objs:print("OBJECTS",json.dumps(r,ensure_ascii=False)[:10000],flush=True)
    print("SUMMARY",json.dumps({"children":len(children),"records_ok":sum(r["status"]=="ok" for r in rows),"eds_ids":len(ids),"object_lists_ok":sum(r["status"]=="ok" for r in objs)}))
if __name__=="__main__":main()
