"""Audit usable days per trip before any directional transport regression."""
from pathlib import Path
import hashlib,json
import pandas as pd

root=Path(__file__).resolve().parents[2]/'outputs'
out=root/'ross_ice_temporal_support_v1';out.mkdir(exist_ok=True)
source=root/'ross_ensemble_ice_v1/interval_support.csv.gz'
metadata=root/'pointblue_full_positions_v1/trip_support.csv'
d=pd.read_csv(source);m=pd.read_csv(metadata)
d=d.merge(m[['bird_fn','season','br_col','data']],on=['bird_fn','season'],validate='many_to_one')
d['date']=pd.to_datetime(d.time1,utc=True).dt.strftime('%Y-%m-%d')
d['year']=pd.to_datetime(d.time1,utc=True).dt.year
assert len(d)==8469 and d.br_col.notna().all() and d.draws.eq(500).all()
records=[]
for (bird,season),g in d.groupby(['bird_fn','season']):
    for measure in ['drift_valid_fraction','drift_nominal_fraction','drift_overlap_half_fraction']:
        for threshold in [.5,1.]:
            for land in ['retain','exclude_flagged_intervals']:
                usable=g[measure].ge(threshold)
                if land!='retain':usable &= g.source_land_flag.eq(0)
                v=g[usable];days=sorted(v.date.unique())
                longest=run=0;prior=None
                for day in pd.to_datetime(days):
                    run=run+1 if prior is not None and (day-prior).days==1 else 1
                    longest=max(longest,run);prior=day
                records.append(dict(bird_fn=bird,season=season,year=int(g.year.iloc[0]),
                    colony=g.br_col.iloc[0],deployment_status=g.data.iloc[0],
                    measure=measure,threshold=threshold,land=land,
                    intervals=len(v),days=len(days),consecutive_days=longest,
                    first_day=min(days) if days else '',last_day=max(days) if days else '',
                    october_intervals=int(v.date.str[5:7].eq('10').sum())))
r=pd.DataFrame(records);r.to_csv(out/'trip_days.csv',index=False)
summary=[]
keys=['year','colony','measure','threshold','land']
for key,g in r.groupby(keys):
    summary.append(dict(zip(keys,key),trips=len(g),with_any=int(g.days.gt(0).sum()),
        with_3_days=int(g.days.ge(3).sum()),with_3_consecutive_days=int(g.consecutive_days.ge(3).sum()),
        median_days=float(g.days.median()),max_days=int(g.days.max()),
        october_intervals=int(g.october_intervals.sum())))
pd.DataFrame(summary).to_csv(out/'colony_year_summary.csv',index=False)
assert len(r)==188*3*2*2
assert (r.consecutive_days<=r.days).all()
assert r.groupby(['bird_fn','season','measure','land']).apply(lambda x: x.sort_values('threshold').days.is_monotonic_decreasing,include_groups=False).all()
result=dict(passed=True,trips=188,specifications=12,trip_specifications=len(r),
    input_hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,metadata]},
    claim='Distinct UTC start dates with accepted flow support, not complete daily tracks or independent replication')
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
print(r[(r.measure=='drift_valid_fraction')&(r.threshold==.5)&(r.land=='retain')].groupby('year').agg(trips=('bird_fn','size'),median_days=('days','median'),max_days=('days','max'),three_days=('days',lambda x:int(x.ge(3).sum()))).to_string())
