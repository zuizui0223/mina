#!/usr/bin/env python3
import argparse,csv,json
from pathlib import Path
from collections import defaultdict,Counter

def main():
 p=argparse.ArgumentParser();p.add_argument("--census",required=True,type=Path);p.add_argument("--out",required=True,type=Path);a=p.parse_args()
 rows=[]
 with a.census.open("r",encoding="utf-8-sig",newline="") as h:
  for r in csv.DictReader(h):
   time=str(r.get("time",""))
   if not time.startswith("1993"): continue
   try:n=float(r.get("num_breeding_pairs",""))
   except:continue
   rows.append({
    "study_name":str(r.get("study_name","")).strip(),
    "island_name":str(r.get("island_name","")).strip(),
    "colony_code":str(r.get("colony_code","")).strip(),
    "count":n
   })
 sums=defaultdict(float); counts=Counter()
 for r in rows:
  k=(r["study_name"],r["island_name"]);sums[k]+=r["count"];counts[k]+=1
 out={"year":1993,"rows":rows,"summaries":[
  {"study_name":k[0],"island_name":k[1],"rows":counts[k],"sum_pairs":v}
  for k,v in sorted(sums.items(), key=lambda kv:(kv[0][0],kv[0][1]))
 ],"grand_total":sum(r["count"] for r in rows)}
 a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
