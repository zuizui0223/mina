"""Conditional four-environment index shifts; no causal or calendar-day forecast."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
from scipy.spatial import Delaunay

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/relationship_response_v1'))
from analyze import fe_fit
OUT=ROOT/'outputs/four_environment_scenarios_v1'
FEATURES=['airC','ice10','salt01','waterC']
KEYS=['scope','species','cam','source_id','member_id','experiment_id','period']
PATHS={
    'cohort':'relationship_response_v1/cohort.csv',
    'climate':'conditional_response_v1/climate_transformations.csv',
    'salt':'salinity_scenario_component_v1/matched_salt_changes.csv',
    'water':'surface_temperature_projection_v1/matched_site_changes.csv',
}


def main():
    OUT.mkdir(exist_ok=True)
    data={k:pd.read_csv(ROOT/'outputs'/p) for k,p in PATHS.items()}
    c=data['cohort']; climates=[]
    obs=c.groupby(['scope','species','cam'])[FEATURES].mean().reset_index()
    for transform in ['additive','bounded']:
        a=data['climate'].pivot(index=KEYS,columns='variable_id',values=transform+'_future').reset_index()
        a=a.rename(columns={'tas':'airC','siconc':'ice10'})
        a.ice10/=10
        a=a.merge(data['salt'][KEYS+['additive_future_salt']],on=KEYS,validate='one_to_one')
        a['salt01']=a.pop('additive_future_salt')/.1
        a=a.merge(data['water'][KEYS+['additive_future_water_C']],on=KEYS,validate='one_to_one')
        a['waterC']=a.pop('additive_future_water_C')
        assert len(a)==984
        a=a.merge(obs,on=['scope','species','cam'],suffixes=('','_observed'),validate='many_to_one')
        for f in FEATURES:a['delta_'+f]=a[f]-a[f+'_observed']
        a['physical_ice']=a.ice10.between(0,10)
        a['transform']=transform
        climates.append(a)
    climate=pd.concat(climates,ignore_index=True)
    assert np.isfinite(climate[FEATURES]).all().all()
    coefficients=[];deletions=[];sites=[];summaries=[]
    for (scope,species),cohort in c.groupby(['scope','species']):
        x=cohort[FEATURES].to_numpy();center=x.mean(axis=0);scale=x.std(axis=0)
        assert (scale>0).all()
        hull=Delaunay((x-center)/scale)
        target=climate[(climate.scope==scope)&(climate.species==species)].copy()
        target['outside_four_variable_hull']=hull.find_simplex((target[FEATURES].to_numpy()-center)/scale,tol=1e-9)<0
        target['outside_any_species_marginal_range']=((target[FEATURES].to_numpy()<x.min(axis=0))|(target[FEATURES].to_numpy()>x.max(axis=0))).any(axis=1)
        for mode in ['site','site_year']:
            beta,info=fe_fit(cohort,FEATURES,mode)
            assert beta is not None
            coef=dict(scope=scope,species=species,mode=mode,n=len(cohort),**info)
            coef.update({f:float(b) for f,b in zip(FEATURES,beta)})
            coefficients.append(coef)
            deleted={}
            for cluster in ['cam','year']:
                fits=[]
                for value in sorted(cohort[cluster].unique()):
                    b,details=fe_fit(cohort[cohort[cluster]!=value],FEATURES,mode)
                    rec=dict(scope=scope,species=species,mode=mode,cluster=cluster,deleted=str(value),**details)
                    rec.update({f:float(v) if b is not None else np.nan for f,v in zip(FEATURES,b if b is not None else [np.nan]*4)})
                    deletions.append(rec)
                    if b is not None:fits.append(b)
                deleted[cluster]=np.asarray(fits)
            t=target.copy();t['mode']=mode
            parts=[]
            for f,b in zip(FEATURES,beta):
                name='component_'+f;t[name]=t['delta_'+f]*b;parts.append(name)
            t['index_shift']=t[parts].sum(axis=1)
            assert np.allclose(t.index_shift,t[['delta_'+f for f in FEATURES]].to_numpy()@beta)
            t.loc[~t.physical_ice,'index_shift']=np.nan
            sites.append(t)
            for key,a in t.groupby(['source_id','member_id','experiment_id','period','transform']):
                rec=dict(scope=scope,species=species,mode=mode,**dict(zip(['source_id','member_id','experiment_id','period','transform'],key)))
                rec.update(sites=len(a),invalid_ice=int((~a.physical_ice).sum()),outside_hull=int(a.outside_four_variable_hull.sum()),
                           outside_marginal=int(a.outside_any_species_marginal_range.sum()),mean_index_shift=np.nan)
                for name in parts:rec[name]=np.nan
                if a.physical_ice.all():
                    change=a[['delta_'+f for f in FEATURES]].mean().to_numpy()
                    rec['mean_index_shift']=float(change@beta)
                    for name,b,v in zip(parts,beta,change):rec[name]=float(b*v)
                    assert np.isclose(sum(rec[name] for name in parts),rec['mean_index_shift'])
                    for cluster,bs in deleted.items():
                        vals=bs@change
                        rec[cluster+'_coefficient_delete_min']=float(vals.min())
                        rec[cluster+'_coefficient_delete_max']=float(vals.max())
                        rec[cluster+'_valid_deletion_fits']=len(bs)
                summaries.append(rec)
    pd.DataFrame(coefficients).to_csv(OUT/'coefficients.csv',index=False)
    pd.DataFrame(deletions).to_csv(OUT/'coefficient_deletions.csv',index=False)
    pd.concat(sites,ignore_index=True).to_csv(OUT/'site_components.csv',index=False)
    summary=pd.DataFrame(summaries);assert len(summary)==288
    summary.to_csv(OUT/'summary.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(status='conditional_sensitivity_not_calibrated_forecast',
        regressions=len(coefficients),deletion_fits=len(deletions),summaries=len(summary),
        input_sha256={p:hashlib.sha256((ROOT/'outputs'/p).read_bytes()).hexdigest() for p in PATHS.values()},
        limitations=['tos change used as proxy for top-level potential temperature change',
        'Index not calendar days; fixed effects not projected',
        'Deletion ranges not confidence intervals; climate target held fixed',
        'Four-variable convex hull is descriptive support not a calibrated validity boundary',
        'Vegetation and drift omitted; conditional coefficients not causal mechanisms']),indent=2)+'\n')
    print(summary.query("scope=='all_source_labels' and transform=='bounded' and experiment_id=='ssp585' and period=='2081-2100'")
          [['species','mode','source_id','mean_index_shift','component_airC','component_ice10','component_salt01','component_waterC','year_coefficient_delete_min','year_coefficient_delete_max','outside_hull','sites']].to_string(index=False))


if __name__=='__main__':main()
