"""Only complete Aug-Nov seasons get environmental summaries; no bird outcome fit."""
from pathlib import Path
import numpy as np,pandas as pd,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
manifest=json.loads((OUT/'daily_concentration_manifest.json').read_text())
files=[ROOT/'work/climate_penguin/osi_concentration/extracted'/(r['date']+'.csv') for r in manifest if r['ok']]
d=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
d['date']=pd.to_datetime(d.date);d['year']=d.date.dt.year
assert not d.duplicated(['location_id','date','inner_km']).any()
rows=[]
for (loc,year,inner),g in d.groupby(['location_id','year','inner_km']):
    dates=pd.date_range(f'{year}-08-01',f'{year}-11-30')
    g=g.set_index('date').reindex(dates)
    observed=g.sic_percent_mean.notna()
    # Coverage is required daily; thresholds are diagnostics, not a chosen best fit.
    enough=(g.n_valid/g.n_ocean.replace(0,np.nan)>=.8)&observed
    complete=bool(enough.all())
    r={'location_id':loc,'year':year,'inner_km':inner,'n_days_present':int(g.n_grid.notna().sum()),'n_days_quality':int(enough.sum()),'complete_122_days':complete}
    if complete:
        for month in [8,9,10,11]:
            z=g[g.index.month==month]
            r[f'sic_mean_month{month}']=z.sic_percent_mean.mean()
        # These are first sustained low-concentration dates in a fixed window,
        # not necessarily final retreat or local physical melt.
        for threshold in [15,30]:
            low=(g.sic_percent_mean<threshold).to_numpy()
            starts=[i for i in range(len(low)-6) if low[i:i+7].all()]
            name=f'low{threshold}_7day'
            if starts and starts[0]==0:
                r[name+'_status']='already_low_at_window_start'
            elif starts:
                i=starts[0];r[name+'_status']='observed_transition';r[name+'_date']=str(dates[i].date());r[name+'_doy']=dates[i].dayofyear
                r[name+'_later_reversal']=bool((~low[i+7:]).any())
            else:r[name+'_status']='no_transition_by_window_end'
        r['mean_interpolated_fraction']=(g.n_interpolated/g.n_valid).mean()
        r['mean_spill_corrected_fraction']=(g.n_land_spill_corrected/g.n_valid).mean()
    rows.append(r)
s=pd.DataFrame(rows);s.to_csv(OUT/'daily_ice_complete_season_features.csv',index=False)
support=s.groupby(['year','inner_km']).agg(location_windows=('location_id','size'),complete_windows=('complete_122_days','sum'),min_days=('n_days_present','min'),max_days=('n_days_present','max')).reset_index()
support.to_csv(OUT/'daily_ice_season_support.csv',index=False)
locations=pd.read_csv(OUT/'daily_ice_locations.csv')
# Exact-coordinate duplicates are removed from separability diagnostics only.
unique=locations.drop_duplicates(['latitude','longitude']).location_id
good=s[s.complete_122_days & s.location_id.isin(unique)]
checks=[]
for month in [9,10]:
    v=f'sic_mean_month{month}'
    if v not in good:continue
    w=good.pivot(index=['location_id','year'],columns='inner_km',values=v).dropna()
    if 0 not in w or 100 not in w:continue
    residual=w-w.groupby(level=0).transform('mean')
    checks.append({'month':month,'location_years':len(w),'locations':w.index.get_level_values(0).nunique(),'spatial_temporal_pearson':w[0].corr(w[100]),'within_location_pearson':residual[0].corr(residual[100]),'note':'Descriptive only; overlapping windows and shared years are dependent. No flow variable included.'})
pd.DataFrame(checks).to_csv(OUT/'daily_ice_near_far_separability.csv',index=False)
print(support.to_string(index=False));print('Complete windows:',s.complete_122_days.sum(),flush=True)
