#!/usr/bin/env python3
import csv, json, argparse
from pathlib import Path
from collections import defaultdict

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    rows=[]
    with a.census.open("r",encoding="utf-8-sig",newline="") as h:
        for r in csv.DictReader(h):
            if str(r.get("island_name","")).strip()!="TOR": continue
            time=str(r.get("time",""))
            if not time[:4].isdigit(): continue
            y=int(time[:4])
            if y not in {1991,1992,1993,2021,2022}: continue
            try: n=float(r.get("num_breeding_pairs",""))
            except: continue
            rows.append({
              "year":y,
              "study_name":str(r.get("study_name","")).strip(),
              "colony_code":str(r.get("colony_code","")).strip(),
              "count":n
            })
    sums=defaultdict(float); counts=defaultdict(int)
    for r in rows:
        k=(r["year"],r["study_name"])
        sums[k]+=r["count"]; counts[k]+=1
    out={
      "rows":rows,
      "study_year_summaries":[
        {"year":y,"study_name":s,"row_count":counts[(y,s)],"sum_pairs":sums[(y,s)]}
        for y,s in sorted(sums)
      ],
      "year_total_all_studies":{
        str(y):sum(r["count"] for r in rows if r["year"]==y)
        for y in sorted({r["year"] for r in rows})
      }
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
