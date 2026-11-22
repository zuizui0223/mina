#!/usr/bin/env python3
"""Check 19/26-site original-count southward and Hill q2 cohort comparisons.

Original 43 three-decade, 50 two-end site-species source records are already
archived next to this script. No pseudoabsence, imputed years or new p-values.
"""
from pathlib import Path
import numpy as np
import pandas as pd

p=Path(__file__).resolve().parent
trip=pd.read_csv(p/'original_three_decade_43_source_site_species.csv')
two=pd.read_csv(p/'original_strict_paired_end_50_source_site_species.csv')
actual=pd.read_csv(p/'same_period_polar_allocation_roster_comparison.csv')
influence=pd.read_csv(p/'site_region_block_influence_on_latitude_concentration.csv')
assert (len(trip),len(two),len(actual))==(43,50,9)
species=('ADPE','CHPE','GEPE')
assert trip.groupby('species').size().to_dict()=={'ADPE':19,'CHPE':12,'GEPE':12}
assert two.groupby('species').size().to_dict()=={'ADPE':26,'CHPE':12,'GEPE':12}
assert set(zip(trip.site_id,trip.species))<=set(zip(two.site_id,two.species))

def normalize(z,label):
    columns={'n0':'median_original_nest_count_0','n1':'median_original_nest_count_2',
      'sic0':'mean_original_aug_nov_SIC_0_pp','sic1':'mean_original_aug_nov_SIC_2_pp'} if label=='all3_2plus' else {
      'n0':'site_median_observed_nests_early','n1':'site_median_observed_nests_late',
      'sic0':'decadal_original_aug_nov_SIC_early_pp','sic1':'decadal_original_aug_nov_SIC_late_pp'}
    return z[['site_id','species','source_region','polar_250km_block','latitude',*columns.values()]].rename(columns={v:k for k,v in columns.items()})

def calc(z):
    n0=z.n0.to_numpy(float);n1=z.n1.to_numpy(float)
    lat=z.latitude.to_numpy(float);a=n0.sum();b=n1.sum()
    w0=n0/a;w1=n1/b
    sic0=z.sic0.to_numpy(float);sic1=z.sic1.to_numpy(float)
    return {'southward_positive_centroid_shift_km':111.195*(sum(lat*w0)-sum(lat*w1)),
      'hill2_pct_change':100*((b*b/sum(n1*n1))/(a*a/sum(n0*n0))-1),
      'nests_sum_pct_change':100*(b/a-1),
      'weighted_SIC_change':sum(w1*sic1)-sum(w0*sic0),
      'physical_SIC_change':sum((w0+w1)/2*(sic1-sic0)),
      'redistribution_SIC_change':sum((w1-w0)*(sic0+sic1)/2)}

z3=normalize(trip,'all3_2plus');z2=normalize(two,'endpoints_2plus')
matched=z3.merge(z2,on=['site_id','species'],suffixes=('_3','_2'),validate='one_to_one')
assert len(matched)==43
for variable in ('source_region','polar_250km_block'):
    assert (matched[variable+'_3']==matched[variable+'_2']).all()
for variable in ('latitude','n0','n1','sic0','sic1'):
    assert np.max(np.abs(matched[variable+'_3']-matched[variable+'_2']))<1e-8

checked=0
for roster,frame in (('all3_2plus',z3),('endpoints_2plus',z2)):
    for sp in species:
        q=frame[frame.species==sp]
        estimate=calc(q)
        expectation=actual[(actual.cohort==roster)&(actual.species==sp)]
        assert len(expectation)==1
        for variable,value in estimate.items():
            assert abs(value-float(expectation.iloc[0][variable]))<1e-8,(roster,sp,variable)
        for unit in ('site_id','polar_250km_block','source_region'):
            for value in q[unit].unique():
                restricted=q[q[unit]!=value]
                if len(restricted)<3:continue
                entry=influence[(influence.cohort==roster)&(influence.species==sp)&
                   (influence.deleted_unit==unit)&(influence.deleted_id==str(value))]
                assert len(entry)==1,(roster,sp,unit,value)
                res=calc(restricted)
                assert abs(res['southward_positive_centroid_shift_km']-entry.iloc[0].southward_shift_km)<1e-8
                assert abs(res['hill2_pct_change']-entry.iloc[0].hill2_pct_change)<1e-8
                checked+=1
assert checked==136,checked
print('PASS 43 original triple-decade + 50 paired-end site-species records; 6 cohort/species summaries; 136 one-unit omissions')
