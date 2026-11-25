"""Obtain a version-verified public export from actual advertised publisher links."""
import csv,hashlib,io,json,re,zipfile
from pathlib import Path
from collections import Counter
from urllib.parse import urljoin,urlparse
from html.parser import HTMLParser
import requests

OUT=Path("build/mapppd_v5_source")
PAGE="https://www.penguinmap.com/mapppd/"
def sha(b):return hashlib.sha256(b).hexdigest()
def allowed(u):
    p=urlparse(u)
    return p.scheme=="https" and (p.hostname=="penguinmap.com" or (p.hostname or "").endswith(".penguinmap.com")) and not p.username and not p.password
def fetch(u,limit):
    if not allowed(u):raise ValueError("not an official HTTPS URL")
    with requests.get(u,timeout=(15,60),stream=True,allow_redirects=False,headers={"User-Agent":"mina-research-source-audit/1.0","Accept":"*/*"}) as r:
        if r.is_redirect:
            target=urljoin(u,r.headers.get("Location",""))
            if not allowed(target):raise ValueError("unreviewed redirect target "+target)
            return None,{"status":r.status_code,"redirect":target}
        r.raise_for_status()
        b=bytearray()
        for part in r.iter_content(65536):
            b.extend(part)
            if len(b)>limit:raise ValueError("bounded download size exceeded")
        return bytes(b),{"url":u,"status":r.status_code,"bytes":len(b),"sha256":sha(b),"content_type":r.headers.get("Content-Type"),"content_disposition":r.headers.get("Content-Disposition")}
def get(u,limit):
    hops=[]
    for _ in range(4):
        b,m=fetch(u,limit);hops.append(m)
        if b is not None:return b,dict(m,redirect_chain=hops)
        u=m["redirect"]
    raise ValueError("redirect limit")
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.anchors=[];self.words=[];self.a=None;self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style"):self.skip+=1
        if tag=="a":self.a={"href":dict(attrs).get("href",""),"title":dict(attrs).get("title",""),"label":""}
    def handle_data(self,d):
        if self.skip:return
        self.words.append(d)
        if self.a is not None:self.a["label"]+=d
    def handle_endtag(self,tag):
        if tag in ("script","style") and self.skip:self.skip-=1
        if tag=="a" and self.a is not None:
            self.a["label"]=" ".join(self.a["label"].split());self.anchors.append(self.a);self.a=None
def parse_csv(b):
    try:t=b.decode("utf-8-sig")
    except UnicodeDecodeError:raise ValueError("non-UTF8 source requires reviewed encoding")
    if t.lstrip().startswith("<"):raise ValueError("HTML response, not CSV")
    try:dialect=csv.Sniffer().sniff(t[:20000],delimiters=",;\t")
    except csv.Error:raise ValueError("could not detect tabular source delimiter")
    rows=list(csv.reader(io.StringIO(t),dialect))
    if len(rows)<2:raise ValueError("empty CSV")
    h=[x.strip() for x in rows[0]]
    if not all(h) or len(set(h))!=len(h):raise ValueError("blank/duplicate source headers")
    body=[r for r in rows[1:] if any(v.strip() for v in r)]
    if any(len(r)!=len(h) for r in body):raise ValueError("ragged CSV rows")
    if not 1000<=len(body)<=100000:raise ValueError("unexpected full-export size")
    n=lambda x:re.sub(r"[^a-z0-9]","",x.casefold())
    fields={x:n(x) for x in h}
    roles={
      "site":{"site","siteid","sitecode","colonyid","colonycode","locationid"},
      "species":{"species","speciesid","speciescode","scientificname","commonname"},
      "season":{"season","breedingseason","year","censusyear","surveyyear","yearstart","seasonstart"},
      "count_type":{"type","counttype","unit","countunit","counted","countof","countcategory","observationtype"},
      "method":{"method","countmethod","surveymethod","observationmethod","protocol"},
      "source":{"source","sourceid","citation","citationid","reference","referenceid","bibliography","doi","sourcecitation","sourcename","references"},
      "date":{"date","eventdate","countdate","surveydate","observationdate","datecount","dateofcount"},
      "count":{"count","countvalue","observedcount","individualcount","number","abundance","nests","numberofnests","observednestcount"},
      "record_id":{"id","countid","observationid","recordid","occurrenceid","eventid"},
    }
    candidates={k:[x for x,v in fields.items() if v in a] for k,a in roles.items()}
    result={"headers":h,"n_rows":len(body),"n_columns":len(h),"exact_duplicate_rows":len(body)-len(set(tuple(r) for r in body)),"field_candidates":candidates,
            "missing_by_field":{x:sum(not r[i].strip() for r in body) for i,x in enumerate(h)},"categorical_support":{}}
    for role in ("species","count_type","method","season"):
        for col in candidates[role]:
            i=h.index(col);v=Counter(r[i].strip() for r in body)
            if len(v)<=300:result["categorical_support"][col]=dict(sorted(v.items()))
    for role in ("site","source","record_id"):
        for col in candidates[role]:
            i=h.index(col);result.setdefault("distinct_nonblank_values",{})[col]=len({r[i].strip() for r in body if r[i].strip()})
    return result
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r={"status":"BLOCKED_SOURCE","ecological_fit":False,"independence_established":False}
    try:
        html,m=get(PAGE,8_000_000);r["page_receipt"]=m
        p=Page();p.feed(html.decode("utf-8",errors="replace"));words=" ".join(" ".join(p.words).split())
        r["version_indicators"]=re.findall(r"\bv(?:ersion\s*)?\d+\.\d+\b",words,re.I)[:20]
        r["latest_season_indicator_2025_26"]=bool(re.search(r"2025\s*[/–-]\s*(?:2026|26)",words))
        r["license_indicator_cc_by_4"]=bool(re.search(r"CC\s*BY\s*4\.0",words,re.I))
        r["relevant_publisher_anchors"]=[a for a in p.anchors if re.search(r"count|csv|darwin|api|release|source|download",a["label"]+" "+a["href"]+" "+a["title"],re.I)][:100]
        if not re.search(r"\bv(?:ersion\s*)?5\.0\b",words,re.I) or not r["latest_season_indicator_2025_26"]:
            raise ValueError("official live page not verified v5.0/2025-26")
        choices=[]
        for a in p.anchors:
            label=" ".join((a["label"]+" "+a["title"]).split())
            if re.search(r"\ball counts\b|\bdownload all counts\b",label,re.I):
                u=urljoin(m["url"],a["href"])
                if a["href"] and not a["href"].startswith("#") and allowed(u):choices.append(u)
        choices=list(dict.fromkeys(choices));r["full_export_candidates"]=choices
        if len(choices)!=1:raise ValueError("no unique official all-counts href")
        b,meta=get(choices[0],30_000_000);r["export_receipt"]=meta
        if b.startswith(b"PK\x03\x04"):
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                if z.testzip() is not None:raise ValueError("archive CRC")
                members=[i for i in z.infolist() if i.filename.lower().endswith(".csv")]
                if len(members)!=1 or members[0].file_size>60_000_000:raise ValueError("ambiguous or oversized CSV member")
                r["csv_member"]=members[0].filename;data=z.read(members[0])
        else:data=b
        r["csv_sha256"]=sha(data);r["schema"]=parse_csv(data)
        r["status"]="V5_EXPORT_ACQUIRED_SCHEMA_REVIEW_REQUIRED"
        # Public export stays in a temporary workflow artifact, never Git.
        if r["license_indicator_cc_by_4"]:
            (OUT/"public_source.csv").write_bytes(data)
            r["public_source_artifact_included"]=True
        else:r["public_source_artifact_included"]=False
    except Exception as e:r["error"]=f"{type(e).__name__}: {e}"
    (OUT/"receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(r,ensure_ascii=False))
if __name__=="__main__":main()
