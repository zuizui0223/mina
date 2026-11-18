from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Geod
out=Path('outputs/cape_diet_replication'); root=Path('work/mina-sync/research/climate-penguin/outputs/cmip6_projection_v1')
fits=pd.read_csv(out/'slope_checks.csv').set_index('site');rows=[]
for name,loc,y,x in [('Cape_Shirreff','loc080',-62.4575,-60.7874),('Stranger_Point','loc064',-62-16/60,-58-37/60)]:
 fit=fits.loc[name]
 for path in root.glob('support_*_siconc.csv'):
  a=pd.read_csv(path).query('location_id==@loc').iloc[0];pre='monthly_'+a.source_id+'_'+a.member_id+'_siconc_'
  def mean(exp,lo,hi):
   t=pd.read_csv(root/(pre+exp+'.csv.gz')).query('location_id==@loc and @lo<=year<=@hi and 8<=month<=11'); assert len(t)==80 and not t.duplicated(['year','month']).any() and t.value.notna().all()
   return t.value.mean()
  hist=mean('historical',1995,2014)
  for exp in ['ssp245','ssp585']:
   for lo,hi in [(2041,2060),(2081,2100)]:
    delta=mean(exp,lo,hi)-hist;adj=fit.hist_ref+delta;ok=fit.sic_min<=adj<=fit.sic_max
    rows.append(dict(site=name,proxy=a.site_id,grid=a.grid_cell_id,cell_km=Geod(ellps='WGS84').inv(x,y,a.grid_lon,a.grid_lat)[2]/1000,model=a.source_id,member=a.member_id,experiment=exp,period=f'{lo}-{hi}',hist_model=hist,obs_ref=fit.hist_ref,delta_sic=delta,adjusted_sic=adj,in_domain=ok,exploratory_gap_change_pp=delta*fit.gap_slope/10 if ok else np.nan))
t=pd.DataFrame(rows);t.to_csv(out/'cmip6_regional_scenarios.csv',index=False);print(t.groupby(['site','experiment','period']).agg(delta_min=('delta_sic','min'),delta_max=('delta_sic','max'),inside=('in_domain','sum')).round(2))
