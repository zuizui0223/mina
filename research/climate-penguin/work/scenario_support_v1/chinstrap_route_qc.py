"""Prespecified quality/timing screen for three return-season track candidates.

One original point per source-clock day; no interpolated route or arrival label.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/chinstrap_winter_v1'
source=OUT/'tracks_normalized.csv.gz'
d=pd.read_csv(source,dtype={'PTT':str,'LOC_CLASS':str})
d['time']=pd.to_datetime(d.time)
targets=sorted(d[d.month.isin([9,10])&d.STAGE.eq('adult')].PTT.unique())
assert len(targets)==3
geo=Geod(ellps='WGS84');daily=[];summaries=[];segments=[];conflicts=[]
for tag in targets:
    raw=d[d.PTT.eq(tag)].sort_values('time').copy()
    good=raw[raw.LOC_CLASS.isin(['1','2','3'])].copy()
    kept=[]
    for time,g in good.groupby('time'):
        best=g[g.LOC_CLASS.astype(int).eq(g.LOC_CLASS.astype(int).max())]
        coords=best[['LATITUDE','LONGITUDE']].drop_duplicates()
        conflict=len(coords)>1
        if len(g)>1:
            conflicts.append(dict(PTT=tag,time=time,rows=len(g),best_class=best.LOC_CLASS.iloc[0],best_coordinates=len(coords),excluded_conflict=conflict))
        if not conflict:kept.append(best.iloc[0])
    clean=pd.DataFrame(kept).sort_values('time')
    initial=clean[clean.time<=raw.time.min()+pd.Timedelta(days=1)]
    assert len(initial)>0
    ref_lat=float(initial.LATITUDE.median());ref_lon=float(initial.LONGITUDE.median())
    period=clean[clean.time.dt.month.isin([9,10])].copy()
    period['day']=period.time.dt.floor('D')
    period['noon_gap_hours']=abs((period.time-period.day-pd.Timedelta(hours=12)).dt.total_seconds()/3600)
    period['quality']=period.LOC_CLASS.astype(int)
    # Quality first, source-clock noon proximity second, earliest time last.
    selected=period.sort_values(['day','quality','noon_gap_hours','time'],ascending=[True,False,True,True]).drop_duplicates('day').sort_values('time').copy()
    _,_,dist=geo.inv(np.full(len(selected),ref_lon),np.full(len(selected),ref_lat),selected.LONGITUDE.to_numpy(),selected.LATITUDE.to_numpy())
    selected['distance_to_initial_proxy_km']=dist/1000
    selected['initial_proxy_lat']=ref_lat;selected['initial_proxy_lon']=ref_lon
    daily.append(selected)
    records=selected.to_dict('records')
    for a,b in zip(records,records[1:]):
        hours=(b['time']-a['time']).total_seconds()/3600
        az,_,metres=geo.inv(a['LONGITUDE'],a['LATITUDE'],b['LONGITUDE'],b['LATITUDE'])
        segments.append(dict(PTT=tag,COLONY=a['COLONY'],start=a['time'],end=b['time'],hours=hours,
            start_lat=a['LATITUDE'],start_lon=a['LONGITUDE'],end_lat=b['LATITUDE'],end_lon=b['LONGITUDE'],
            displacement_km=metres/1000,bearing_degrees=az,
            distance_to_proxy_change_km=b['distance_to_initial_proxy_km']-a['distance_to_initial_proxy_km'],
            within_12_36_hours=bool(12<=hours<=36)))
    summaries.append(dict(PTT=tag,COLONY=raw.COLONY.iloc[0],raw_sep_oct_rows=int(raw.month.isin([9,10]).sum()),
        quality_sep_oct_rows=len(period),selected_days=len(selected),first_selected=str(selected.time.min()),last_selected=str(selected.time.max()),
        first_proxy_distance_km=float(selected.distance_to_initial_proxy_km.iloc[0]),last_proxy_distance_km=float(selected.distance_to_initial_proxy_km.iloc[-1]),
        min_proxy_distance_km=float(selected.distance_to_initial_proxy_km.min()),max_proxy_distance_km=float(selected.distance_to_initial_proxy_km.max()),
        days_beyond_500km=int((selected.distance_to_initial_proxy_km>500).sum()),initial_reference_rows=len(initial)))
daily=pd.concat(daily,ignore_index=True);segments=pd.DataFrame(segments);summary=pd.DataFrame(summaries)
assert not daily.duplicated(['PTT','day']).any()
assert daily.LOC_CLASS.isin(['1','2','3']).all()
assert set(daily.PTT)==set(targets)
daily.to_csv(OUT/'route_daily_points.csv',index=False)
segments.to_csv(OUT/'route_segments.csv',index=False)
summary.to_csv(OUT/'route_support.csv',index=False)
pd.DataFrame(conflicts,columns=['PTT','time','rows','best_class','best_coordinates','excluded_conflict']).to_csv(OUT/'timestamp_conflicts.csv',index=False)
receipt={'passed':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tags':3,'daily_points':len(daily),
 'candidate_segments':len(segments),'segments_12_36_hours':int(segments.within_12_36_hours.sum()),
 'same_best_quality_conflicts_excluded':sum(c['excluded_conflict'] for c in conflicts),
 'limitations':['initial 24h high-quality coordinate median is a proxy, not verified colony coordinates','timestamps remain naive source clock; no UTC assumption',
 'daily net displacement not travelled path or swimming speed','12-36h is an exposure alignment screen, not proof of good biological trajectory',
 'no confirmed return, no ice transport attribution, no sea-ice values joined yet']}
(OUT/'route_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(summary.to_string(index=False));print(json.dumps(receipt,indent=2))
