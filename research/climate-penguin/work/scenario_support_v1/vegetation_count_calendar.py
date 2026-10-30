"""Reconcile candidate image years with original dated count records."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_annual_support_v1'
p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);args=p.parse_args()
raw=pd.read_csv(args.raw);known=raw[raw.month.notna()]
assert known.season.eq(known.year-np.where(known.month<=6,1,0)).all()
c=pd.read_csv(OUT/'count_image_year_candidates.csv').drop_duplicates(['site_id','species_id','season','count'])
keys=['site_id','species_id','season','count']
source=raw[raw.type.eq('nests')].merge(c[keys],on=keys,how='inner',validate='many_to_one')
assert not source.duplicated(keys).any()
j=c[keys].merge(source,on=keys,how='left',validate='one_to_one',indicator=True)
assert j._merge.eq('both').all();j=j.drop(columns='_merge')
j['same_breeding_season_january_year']=j.season+1
j['prior_january_year']=j.season
j['month_known']=j.month.notna()
j['same_season_january_relative_to_count']=np.select([j.month.isin([7,8,9,10,11,12]),j.month.eq(1),j.month.isin([2,3,4,5,6])],['after_count_month','same_month_day_order_needed','before_count_month'],default='unknown_count_month')
j.to_csv(OUT/'dated_count_alignment.csv',index=False)
receipt=dict(raw_sha256=hashlib.sha256(args.raw.read_bytes()).hexdigest(),global_known_month_rule_checks=len(known),matched_counts=len(j),known_month_counts=int(j.month_known.sum()),january_after_count_month=int(j.same_season_january_relative_to_count.eq('after_count_month').sum()),january_same_month=int(j.month.eq(1).sum()),unknown_month=int(j.month.isna().sum()),note='Season+1 January follows the observed dataset convention; unknown-month rows remain unverified for chronological ordering')
(OUT/'calendar_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt)
