from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
s=pd.read_csv(OUT/'daily_ice_locations.csv');s=s[s.cohort.eq('macro_40')]
c=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv')
c=c[c.site_id.isin(s.site_id)&c.species_id.eq('ADPE')&c.season.between(1991,2020)]
i=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_intervals.csv')
i=i[i.site_id.isin(s.site_id)&i.species_id.eq('ADPE')&i.start.between(1991,2019)&i.end.between(1992,2020)&i.same_known_method&i.gap.eq(1)&i.n_start.gt(0)&i.n_end.gt(0)]
rows=[]
for name,lo,hi in [('historical_extension',1991,2010),('recent_existing',2011,2020),('full_scope',1991,2020)]:
    a=c[c.season.between(lo,hi)];b=i[i.start.ge(lo)&i.end.le(hi)]
    rows.append(dict(scope=name,start_year=lo,end_year=hi,count_records=len(a),count_sites=a.site_id.nunique(),count_regions=a.region.nunique(),annual_intervals=len(b),interval_sites=b.site_id.nunique(),interval_regions=b.region.nunique()))
pd.DataFrame(rows).to_csv(OUT/'historical_count_support.csv',index=False)
i.groupby('region').agg(intervals=('site_id','size'),sites=('site_id','nunique')).reset_index().to_csv(OUT/'historical_count_interval_regions.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
