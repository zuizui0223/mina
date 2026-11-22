#!/usr/bin/env python3
"""Independent source-cohort and covariance arithmetic verification, no p-values.

Input: original repo-archived actual source site×species median nest records.
Only original colony site IDs; missing species/years are never coded as zero.
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'allocation_20261115'
def load(p):
    with p.open(encoding='utf8',newline='') as stream:
        return list(csv.DictReader(stream))
def n(v):
    return float(v)
def mean(a):
    return sum(a)/len(a)
def cov(a,b):
    mx,my=mean(a),mean(b)
    return mean([(x-mx)*(y-my) for x,y in zip(a,b)])
def cor(a,b):
    d=cov(a,a)*cov(b,b)
    return cov(a,b)/math.sqrt(d) if d>1e-20 else None
def near(a,b,tol=3e-8):
    assert a is not None and b is not None and abs(float(a)-float(b))<tol,(a,b)
rows=load(HERE/'original_adelie_19_26_35_site_growth_cohorts.csv')
metrics={r['cohort']:r for r in load(HERE/'adelie_latitude_nesting_scale_3rosters_summary.csv')}
parts=load(HERE/'adelie_latitude_nesting_scale_by_source_region.csv')
raw35=load(HERE/'original_35_adelie_2decade_source_rows.csv')
raw43={r['site_id']:r for r in load(OLD/'original_three_decade_43_source_site_species.csv') if r['species']=='ADPE'}
raw50={r['site_id']:r for r in load(OLD/'original_strict_paired_end_50_source_site_species.csv') if r['species']=='ADPE'}
assert len(rows)==80 and len(parts)==14 and len(metrics)==3
assert len(raw35)==35 and len(raw43)==19 and len(raw50)==26
assert set(raw43)<=set(raw50)<=set(r['site_id'] for r in raw35)
assert n(next(r for r in raw35 if r['site_id']=='ADAR')['n_early'])==318110
assert n(next(r for r in raw35 if r['site_id']=='ADAR')['n_late'])==445440
names={'all_three_decades':19,'two_plus_endpoint_years':26,'one_plus_endpoint_year':35}
for roster,k in names.items():
    q=[r for r in rows if r['cohort']==roster]
    assert len(q)==k and len({r['site_id'] for r in q})==k
    for r in q:
        assert int(float(r['n_early']))>=0 and int(float(r['n_late']))>=0
        assert float(r['year_late'])>float(r['year_early'])
        if roster=='all_three_decades':
            src=raw43[r['site_id']]
            near(r['n_early'],src['median_original_nest_count_0'])
            near(r['n_late'],src['median_original_nest_count_2'])
        if roster=='two_plus_endpoint_years':
            src=raw50[r['site_id']]
            near(r['n_early'],src['site_median_observed_nests_early'])
            near(r['n_late'],src['site_median_observed_nests_late'])
    x=[-n(r['latitude']) for r in q]
    y=[math.log1p(n(r['n_late']))-math.log1p(n(r['n_early'])) for r in q]
    groups=defaultdict(list)
    for i,r in enumerate(q):
        groups[r['source_region']].append(i)
    across=cov(x,y)
    mx,my=mean(x),mean(y)
    bx=wx=0.
    rx=[];ry=[]
    for reg,ix in groups.items():
        xg=[x[i] for i in ix];yg=[y[i] for i in ix]
        weight=len(ix)/k
        vbetween=weight*(mean(xg)-mx)*(mean(yg)-my)
        vwithin=weight*cov(xg,yg)
        bx+=vbetween;wx+=vwithin
        specific=[z for z in parts if z['cohort']==roster and z['source_region']==reg]
        assert len(specific)==1
        near(vbetween,specific[0]['between_region_contribution_to_total_site_cov'])
        near(vwithin,specific[0]['within_region_contribution_to_total_site_cov'])
        rx.extend([val-mean(xg) for val in xg])
        ry.extend([val-mean(yg) for val in yg])
    assert len(rx)==len(q)
    assert abs(bx+wx-across)<1e-11
    # Within correlation is insensitive to order because aligned residuals appended together
    a=metrics[roster]
    near(cor(x,y),a['r_site_equal_pooled_south_lat_vs_log_nest_change'])
    near(cor(rx,ry),a['r_site_equal_region_demeaned_south_lat_vs_log_nest_change'])
    near(across,a['site_equal_original_latitude_log_growth_covariance'])
    near(bx,a['source_region_between_covariance'])
    near(wx,a['source_region_within_covariance'])
    near(bx/across,a['proportion_of_pooled_covariance_between_reporting_regions'])
    vals0=[n(r['n_early']) for r in q];vals1=[n(r['n_late']) for r in q]
    c=111.195*(sum(v*x0 for v,x0 in zip(vals1,x))/sum(vals1)-
                 sum(v*x0 for v,x0 in zip(vals0,x))/sum(vals0))
    near(c,a['observed_nest_count_weighted_south_shift_km'],1e-7)
    assert n(a['n_regions'])==len(groups)
    print('SOURCE_REPRODUCED',roster,'n',k,'pooled_r',round(cor(x,y),4),
          'region_r',round(cor(rx,ry),4),'between_cov_pct',round(100*bx/across,2),
          'nest_weighted_shift_km',round(c,3))
print('PASS original 19/26/35 Adélie count rosters, region covariance identity and geographic shift')
