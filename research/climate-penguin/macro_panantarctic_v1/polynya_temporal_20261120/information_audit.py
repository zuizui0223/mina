"""Post-fit disclosure of zero-information labeled clusters; not gate replacement."""
import pandas as pd
from run import HERE, CONTROLS, residualize, fit, save

d=pd.read_csv(HERE/'matched_analysis.csv')
x=residualize(d[CONTROLS+['P0','P1']],d)
s=pd.DataFrame({'source_region':d.source_region,'P0_residual_ss':x[:,-2]**2,'P1_residual_ss':x[:,-1]**2}).groupby('source_region',as_index=False).sum()
s['contributes_exposure_variation']=s.P0_residual_ss.gt(1e-16)&s.P1_residual_ss.gt(1e-16)
save(s,'region_information_audit.csv')
sub=d[d.source_region.isin(s.loc[s.contributes_exposure_variation,'source_region'])].copy()
r,_,_=fit(sub,['P0','P1'])
out=pd.DataFrame(r);out['n']=len(sub);out['regions']=sub.source_region.nunique()
save(out,'informative_regions_sensitivity.csv');print(out.to_string(index=False))
