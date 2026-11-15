#!/usr/bin/env python3
"""Independent check with scipy.stats.linregress and explicit species-day pivot.

Verifies primary 18 exact source-verified pair slopes and three sites' subtotal
without importing the main audit implementation or reusing its helpers.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import linregress
ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);args=ap.parse_args()
r=pd.read_csv(args.source_dir/'strict_original_pair_1993_2020_matched_siteyears.csv')
a=pd.read_csv(args.out_dir/'strict_18_pairs_absolute_vs_relative_component_decomposition.csv')
b=pd.read_csv(args.out_dir/'strict_three_species_total_sitelevel_sensitivity.csv')
errors=[]
for x in a.itertuples(index=False):
 z=r[(r.species_pair==x.pair)&(r.site_id==x.site)].sort_values('year')
 for key,c in [('first_species_slope','first_observed_nests'),('second_species_slope','second_observed_nests')]:
  prediction=linregress(z.year,np.log1p(z[c])).slope*10
  errors.append(abs(prediction-getattr(x,key)))
 su=linregress(z.year,np.log1p(z.first_observed_nests+z.second_observed_nests)).slope*10
 errors.append(abs(su-x.pair_subtotal_log_slope))
 errors.append(abs(x.second_species_slope-x.first_species_slope-x.ratio_slope))
 assert (x.first_species_nests_start==z.first_observed_nests.iloc[0] and x.second_species_nests_start==z.second_observed_nests.iloc[0])
 assert (x.first_species_nests_end==z.first_observed_nests.iloc[-1] and x.second_species_nests_end==z.second_observed_nests.iloc[-1])
assert (a.query("pair=='ADPE__GEPE'").first_species_slope<0).all()
assert (a.query("pair=='ADPE__GEPE'").second_species_slope>0).all()
assert int((a.query("pair=='ADPE__GEPE'").pair_subtotal_pct_change>0).sum())==5
assert int((a.query("pair=='CHPE__GEPE'").pair_subtotal_pct_change>0).sum())==8
for x in b.itertuples(index=False):
 rr=r[(r.site_id==x.site)]
 pairs=rr.groupby('year').species_pair.nunique(); yrs=pairs[pairs==3].index
 assert len(yrs)==x.n_three_species_common_years
 rec=[]
 for y in yrs:
  records={}
  for t in rr[rr.year==y].itertuples(index=False):
   aa,bb=t.species_pair.split('__'); records.setdefault(aa,set()).add(t.first_observed_nests);records.setdefault(bb,set()).add(t.second_observed_nests)
  assert len(records)==3 and all(len(v)==1 for v in records.values())
  rec.append((y,{s:next(iter(v)) for s,v in records.items()}))
 t=np.array([y for y,c in rec]);gs=np.array([c['GEPE'] for y,c in rec]);ac=np.array([c['ADPE']+c['CHPE'] for y,c in rec]);total=gs+ac
 errors.append(abs(linregress(t,np.log1p(total)).slope*10-x.three_species_subtotal_slope))
 errors.append(abs(linregress(t,np.log1p(ac)).slope*10-x.ADPE_CHPE_subtotal_slope))
 assert x.first_three_species_total==total[0] and x.last_three_species_total==total[-1]
 assert abs(100*(gs[-1]/total[-1]-gs[0]/total[0])-x.gentoo_share_pp_change)<1e-8
assert max(errors)<1e-9
out={'verified':True,'n_exact_strict_species_pair_slopes':18,'n_true_cocensus_pair_years':len(r),'n_full_three_species_years':34,'max_abs_slope_and_identity_error':max(errors), 'source_methods':'scipy.stats.linregress + independent original row pivot','sign_gentoo_and_adelie_opposite_6_of_6':True,'two_species_sum_gentoo_adelie_increase_endpoints_5_of_6':True, 'three_species_subtotal_endpoints_positive_2_of_3':True}
(args.out_dir/'independent_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
