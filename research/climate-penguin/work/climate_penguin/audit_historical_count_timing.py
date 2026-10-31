"""Calendar support for historical counts before environmental fitting."""
from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
rawpath=ROOT/'work/data_audit/mapppdr/penguin_obs.csv';raw=pd.read_csv(rawpath)
known=raw[raw.month.notna()];assert known.season.eq(known.year-np.where(known.month<=6,1,0)).all()
loc=pd.read_csv(OUT/'daily_ice_locations.csv');loc=loc[loc.cohort.eq('macro_40')]
c=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv')
c=c[c.site_id.isin(loc.site_id)&c.species_id.eq('ADPE')&c.season.between(1991,2020)]
e=raw[raw.type.eq('nests')][['site_id','species_id','season','count','month','day','date','year','citekey']]
j=c[['site_id','species_id','season','count']].merge(e,on=['site_id','species_id','season','count'],how='left',validate='one_to_many',indicator=True)
assert j._merge.eq('both').all()
j['month_known']=j.month.notna();j['after_september']=j.month.isin([10,11,12,1,2,3,4,5,6]);j['october_march']=j.month.isin([10,11,12,1,2,3]);j['after_november']=j.month.isin([12,1,2,3,4,5,6])
q=j.groupby(['site_id','species_id','season']).agg(source_records=('citekey','size'),all_months_known=('month_known','all'),all_after_september=('after_september','all'),all_october_march=('october_march','all'),all_after_november=('after_november','all'),months=('month',lambda x:';'.join(str(int(v)) for v in sorted(x.dropna().unique()))),citations=('citekey',lambda x:';'.join(sorted(set(x.dropna().astype(str)))))).reset_index()
c=c.merge(q,on=['site_id','species_id','season'],validate='one_to_one')
c.to_csv(OUT/'historical_count_season_timing.csv',index=False)
i=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_intervals.csv')
i=i[i.site_id.isin(loc.site_id)&i.species_id.eq('ADPE')&i.start.between(1991,2019)&i.end.between(1992,2020)&i.same_known_method&i.gap.eq(1)&i.n_start.gt(0)&i.n_end.gt(0)].copy()
flags=['all_months_known','all_after_september','all_october_march','all_after_november']
for phase in ['start','end']:
    i=i.merge(c[['site_id','species_id','season']+flags].rename(columns={'season':phase,**{v:phase+'_'+v for v in flags}}),on=['site_id','species_id',phase],validate='many_to_one')
for v in flags:i['both_'+v]=i['start_'+v]&i['end_'+v]
assert len(i)==301
i.to_csv(OUT/'historical_count_interval_timing.csv',index=False)
rows=[]
for scope,a in [('all',i),('without_victoria',i[i.region.ne('Victoria Land')]),('1991_2010',i[i.end.le(2010)]),('2011_2020',i[i.start.ge(2011)])]:
    for criterion in ['all_intervals']+['both_'+v for v in flags]:
        b=a if criterion=='all_intervals' else a[a[criterion]]
        rows.append(dict(scope=scope,criterion=criterion,intervals=len(b),sites=b.site_id.nunique(),regions=b.region.nunique()))
r=pd.DataFrame(rows);r.to_csv(OUT/'historical_count_timing_summary.csv',index=False)
checks=dict(source_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),known_month_season_rule_verified=True,matched_count_records=len(c),count_source_rows=len(j),eligible_intervals=len(i),environment_effect_fitted=False)
(OUT/'historical_count_timing_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(r.to_string(index=False))
