#!/usr/bin/env python3
"""Exact source Table 4 Syowa 8-colony 2004/05–2010/11 estimates from Southwell 2015 S1 DOC.
Source only, no satellite extraction, no demographic model, no invented unobserved years.
"""
from __future__ import annotations
import argparse,subprocess,re,hashlib,json
from pathlib import Path
import pandas as pd
ORIGINAL_DOC_SHA256="c063b1d77e67a83bb945a1b8db276061b452130e7389e79dbdfd3f4675fb8ddb"
EXPECTED={
  2004:(3325,3181,3491),
  2005:(2634,2486,2801),
  2006:(3047,2931,3170),
  2007:(2864,2720,3013),
  2008:(2255,2136,2371),
  2009:(2557,2454,2669),
  2010:(2047,1981,2117)
}
def gate(cond,msg):
    if not cond:raise ValueError("SYOWA ORIGINAL-SOURCE STOP "+msg)
def main(args):
    raw=Path(args.source);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(raw.read_bytes()).hexdigest()
    gate(h==ORIGINAL_DOC_SHA256,"original Southwell S1 document hash drift")
    content=subprocess.run(["antiword","-w","120",str(raw)],capture_output=True,check=True).stdout.decode("latin1","replace")
    sect=content.split("Table 4. Population estimates for sites surveyed",1)
    gate(len(sect)==2,"Original Table 4 not located")
    rows=[];regional=None
    for l in sect[1].splitlines():
        if not l.startswith("|"):continue
        if l.strip().startswith("|Syowa"):
            regional="Syowa"
        elif re.match(r"\|Mawson",l):
            break
        m=re.search(r"\|\s*(20\d\d)/(20\d\d|\d\d)\s*\|\s*([\d,]+)\s*\|\s*\(([\d,]+)-([\d,]+)\)",l)
        if m and regional=="Syowa":
            year=int(m[1]);val=tuple(int(m[k].replace(",","")) for k in (3,4,5))
            if year in EXPECTED:
                gate(year not in {x["season"] for x in rows},"duplicate original season")
                gate(val==EXPECTED[year],"published original Table 4 value drift "+str(year))
                rows.append(dict(region="Syowa",season=year,breeding_pairs_median=val[0],
                     CI_95_lower=val[1],CI_95_upper=val[2],n_original_stable_region_sites=8,
                     source="Southwell et al 2015 PLOS ONE Table S1 Table 4"))
    rows=sorted(rows,key=lambda x:x["season"])
    gate([x["season"] for x in rows]==list(EXPECTED),"missing 7 original years")
    # Table 1: starred original eight fixed regional breeding sites.
    coords=[]
    for line in content.split("Table 2. Sources of historical",1)[0].splitlines():
        match=re.search(r"\|S,\s*(-\d+\.\d+),\s*(\d+\.\d+)\*",line)
        if match:
            coords.append((float(match.group(1)),float(match.group(2))))
    gate(len(coords)==8,"Expected eight original source Syowa sites; got "+str(len(coords)))
    coords_df=pd.DataFrame({"site":range(1,9),
        "latitude":[c[0] for c in coords],
        "longitude":[c[1] for c in coords]})
    gate(coords_df.drop_duplicates(["latitude","longitude"]).shape[0]==7,
        "Source original S1 duplicate rounded coordinate unexpectedly changed")
    count_df=pd.DataFrame(rows)
    count_df.to_csv(out/"SYO_Southwell2015_original_8site_7_seasons_2004_2010.csv",index=False)
    coords_df.to_csv(out/"SYO_Southwell2015_original_8site_coords.csv",index=False)
    audit={
       "status":"SOUTHWELL_S1_SOURCE_VERIFIED_7_SEASONS_UNDER_8YEAR_SPAN_GATE",
       "source_doi":"https://doi.org/10.1371/journal.pone.0139877.s001",
       "original_S1_DOC_SHA256":ORIGINAL_DOC_SHA256,
       "n_original_source_region_sites":8,"n_distinct_rounded_coordinates":7,
       "n_observed_seasons":7,"min_season":2004,"max_season":2010,"span_years":6,
       "original_estimates_are_Southwell_adjusted_regional_breeding_pair_estimates":True,
       "not_directly_comparable_to_RAW_MAPPPD_SITE_NESTS":True,
       "passes_predeclared_min_years_4":True,
       "passes_predeclared_min_time_span_8_years":False,
       "adopt_as_eighth_qualified_independent_block":False,
       "source_quality_caveat":"Regional total of same 8 sites; some lat/lon rounded identical in publisher S1 table.",
       "existing_7_geographic_blocks_unchanged":True}
    (out/"SYO_SOUTHWELL_ORIGINAL_SEVEN_YEAR_SOURCE_GATE.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",required=True)
    main(p.parse_args())
