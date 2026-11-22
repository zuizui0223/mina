#!/usr/bin/env python3
"""Strict same-source penguin pair census: identity, absolute change, subtotal.

Post-hoc descriptive extension of original source matches, no causal/forecast tests.
Every site/year/species number here comes from the previous true co-census
source-verified CSV rather than inferred absence or merged independent sites.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

PARSER=argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parent,help='Directory containing the two source-verified strict-pair CSVs')
PARSER.add_argument('--out-dir',type=Path,default=Path(__file__).resolve().parent,help='Where to save derived audit files')
ARGS=PARSER.parse_args()
SOURCE=ARGS.source_dir
HERE=ARGS.out_dir
HERE.mkdir(parents=True,exist_ok=True)
rows=pd.read_csv(SOURCE/'strict_original_pair_1993_2020_matched_siteyears.csv')
old=pd.read_csv(SOURCE/'strict_original_18_pair_site_longterm_slopes.csv')
assert len(rows)==183 and len(old)==18
assert not rows.duplicated(['species_pair','site_id','year']).any()
assert rows['genuine_source_shared_citation_method'].all()
assert (rows['first_observed_nests']>=0).all() and (rows['second_observed_nests']>=0).all()
expected={'ADPE__GEPE':6,'CHPE__GEPE':9,'ADPE__CHPE':3}
assert rows.groupby('species_pair')['site_id'].nunique().to_dict()==expected
assert len({*rows['site_id']})==12
assert len(set(rows['source_250km_block']))==4
assert len(set(rows['source_region']))==2
assert np.max(np.abs(rows['relative_log1p_second_minus_first']-
                     (np.log1p(rows['second_observed_nests'])-np.log1p(rows['first_observed_nests']))))<1e-12

def ols10(x,y):
    a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
    return float(np.dot(a-a.mean(),b-b.mean())/np.sum((a-a.mean())**2)*10)

out=[]
for (pair,site), z in rows.groupby(['species_pair','site_id']):
    z=z.sort_values('year'); t=z['year'].to_numpy();n1=z['first_observed_nests'].to_numpy();n2=z['second_observed_nests'].to_numpy()
    assert len(z)>=5 and (max(t)-min(t)>=10)
    o=old[(old.species_pair==pair)&(old.site_id==site)].iloc[0]
    slope1=ols10(t,np.log1p(n1));slope2=ols10(t,np.log1p(n2)); sr=slope2-slope1
    assert abs(slope1-o.first_species_log_nests_slope_decade_same_shared_years)<1e-10
    assert abs(slope2-o.second_species_log_nests_slope_decade_same_shared_years)<1e-10
    assert abs(sr-o.relative_log_ratio_slope_decade)<1e-10
    assert int(n1[0])==int(o.first_nests_first_species) and int(n1[-1])==int(o.last_nests_first_species)
    assert int(n2[0])==int(o.first_nests_second_species)
    assert int(n2[-1])==int(o.last_nests_second_species)
    assert int(n1[-1])==int(o.last_nests_first_species)
    assert abs(ols10(t,z.mean_source_SIC_pp)-o.sic_slope)<1e-8
    first_total=int(n1[0]+n2[0]);last_total=int(n1[-1]+n2[-1]);
    out.append({'pair':pair,'site':site,'region':z.source_region.iloc[0],
                'block':z.source_250km_block.iloc[0],'n_years':len(t),'span_yr':int(t[-1]-t[0]),
                'first_year':int(t[0]),'last_year':int(t[-1]),
                'first_species_slope':slope1,'second_species_slope':slope2,
                'ratio_slope':sr,'both_species_opposite_direction':bool(slope1<0 and slope2>0),
                'fraction_ratio_slope_from_second_species_rise':float(slope2/sr) if abs(sr)>1e-9 else None,
                'sic_slope_pp_per_decade':float(o.sic_slope),
                'first_species_nests_start':int(n1[0]),'first_species_nests_end':int(n1[-1]),
                'second_species_nests_start':int(n2[0]),'second_species_nests_end':int(n2[-1]),
                'first_species_nest_endpoint_delta':int(n1[-1]-n1[0]),
                'second_species_nest_endpoint_delta':int(n2[-1]-n2[0]),
                'pair_subtotal_nests_start':first_total,'pair_subtotal_nests_end':last_total,
                'pair_subtotal_pct_change':float(100*(last_total/first_total-1)),
                'pair_subtotal_log_slope':ols10(t,np.log1p(n1+n2)),
                'pair_subtotal_log_slope_drop_first':ols10(t[1:],np.log1p(n1[1:]+n2[1:])),
                'pair_subtotal_log_slope_drop_last':ols10(t[:-1],np.log1p(n1[:-1]+n2[:-1])),
                'first_species_slope_drop_first':ols10(t[1:],np.log1p(n1[1:])),
                'first_species_slope_drop_last':ols10(t[:-1],np.log1p(n1[:-1])),
                'second_species_slope_drop_first':ols10(t[1:],np.log1p(n2[1:])),
                'second_species_slope_drop_last':ols10(t[:-1],np.log1p(n2[:-1]))})

out=pd.DataFrame(out).sort_values(['pair','site'])
out.to_csv(HERE/'strict_18_pairs_absolute_vs_relative_component_decomposition.csv',index=False,float_format='%.12g')

# Build one de-duplicated observed (site, year, species) datum. All three original
# pair edges must lead to one identical count in a triple site-year.
observations=[]
for r in rows.itertuples(index=False):
 a,b=r.species_pair.split('__')
 observations.extend([(r.site_id,r.year,a,r.first_observed_nests,r.species_pair),
                      (r.site_id,r.year,b,r.second_observed_nests,r.species_pair)])
obs=pd.DataFrame(observations,columns=['site','year','species','count','from_pair'])
assert (obs.groupby(['site','year','species'])['count'].nunique()==1).all(), 'Original pair counts disagree in one of shared site/year/species identities'
unique=obs.drop_duplicates(['site','year','species'])
triple_support=unique.groupby(['site','year'])['species'].nunique()
triples=triple_support[triple_support==3].reset_index()[['site','year']]
assert len(triples)==34 and triples.site.nunique()==3
w=unique.merge(triples,on=['site','year'],how='inner').pivot(index=['site','year'],columns='species',values='count').reset_index()
assert w.notna().all().all() and len(w)==34
w['three_species_subtotal']=w[['ADPE','CHPE','GEPE']].sum(axis=1)
w['two_species_A_G_subtotal']=w[['ADPE','GEPE']].sum(axis=1)
w.to_csv(HERE/'strict_34_three_species_siteyears_actual_counts.csv',index=False)
three=[]
for site,z in w.groupby('site'):
 z=z.sort_values('year'); a=z.year.to_numpy();n=z.three_species_subtotal.to_numpy();
 x={sp:ols10(a,np.log1p(z[sp])) for sp in ['ADPE','CHPE','GEPE']};
 three.append({'site':site,'n_three_species_common_years':len(z),'first_year':int(a.min()),'last_year':int(a.max()),
               'ADPE_slope':x['ADPE'],'CHPE_slope':x['CHPE'],'GEPE_slope':x['GEPE'],
               'ADPE_CHPE_subtotal_slope':ols10(a,np.log1p(z.ADPE+z.CHPE)),
               'three_species_subtotal_slope':ols10(a,np.log1p(n)),
               'two_species_A_G_subtotal_slope_on_exact_three_years':ols10(a,np.log1p(z.two_species_A_G_subtotal)),
               'first_three_species_total':int(n[0]),'last_three_species_total':int(n[-1]),
               'first_ADPE_CHPE_total':int(z.ADPE.iloc[0]+z.CHPE.iloc[0]),
               'last_ADPE_CHPE_total':int(z.ADPE.iloc[-1]+z.CHPE.iloc[-1]),
               'gentoo_share_start_pct':float(100*z.GEPE.iloc[0]/n[0]),
               'gentoo_share_end_pct':float(100*z.GEPE.iloc[-1]/n[-1]),
               'gentoo_share_pp_change':float(100*(z.GEPE.iloc[-1]/n[-1]-z.GEPE.iloc[0]/n[0])),
               'three_species_endpoint_pct_change':float(100*(n[-1]/n[0]-1))})
three=pd.DataFrame(three).sort_values('site')
three.to_csv(HERE/'strict_three_species_total_sitelevel_sensitivity.csv',index=False,float_format='%.12g')

co={}
for pair,z in out.groupby('pair'):
 co[pair]={'n_sites':len(z),'n_count_years':int(rows[rows.species_pair==pair].shape[0]),
 'n_second_species_increase':int((z.second_species_slope>0).sum()),
 'n_first_species_decrease':int((z.first_species_slope<0).sum()),
 'n_second_increase_first_decrease':int(z.both_species_opposite_direction.sum()),
 'n_relative_ratio_increase':int((z.ratio_slope>0).sum()),
 'n_subtotal_endpoint_increase':int((z.pair_subtotal_pct_change>0).sum()),
 'n_subtotal_ols_increase':int((z.pair_subtotal_log_slope>0).sum()),
 'n_subtotal_ols_positive_both_1yr_deletion':int(((z.pair_subtotal_log_slope>0)&(z.pair_subtotal_log_slope_drop_first>0)&(z.pair_subtotal_log_slope_drop_last>0)).sum()),
 'n_sic_rising':int((z.sic_slope_pp_per_decade>0).sum()),
 'median_first_species_slope':float(z.first_species_slope.median()),
 'median_second_species_slope':float(z.second_species_slope.median()),
 'median_relative_ratio_slope':float(z.ratio_slope.median()),
 'median_second_species_fraction_positive_ratio_contribution':float(z.loc[z.ratio_slope>0,'fraction_ratio_slope_from_second_species_rise'].median()),
 'median_subtotal_endpoint_pct_change':float(z.pair_subtotal_pct_change.median()),
 'median_subtotal_log_slope':float(z.pair_subtotal_log_slope.median()),
 'region_count':int(z.region.nunique()),'block_count':int(z.block.nunique())}
res={'source_rows':183,'source_triple_years':34,'unique_sites':12,'n_source_site_species_pairs':18,
     'pair_results':co,'triple_total_results':three.to_dict('records'),
     'limitations':['original same citekey and method but same day/effort unproven','2 geographic regions only','same source site-year reused across species contrasts','no inference of interactions or habitat takeover from count alone','nests at surveyed sites, not population totals','post-result descriptive and not population independent validation']}
(HERE/'reweighting_component_summary.json').write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(res,indent=2,ensure_ascii=False))
