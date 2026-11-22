#!/usr/bin/env python3
"""Two post-selection falsification checks of original-source penguin isotope proxy.
No prey fractions, causal salinity effect, confirmatory permutation p, or
out-of-region transfer claim. Required inputs are frozen GH Actions artifacts.
"""
import argparse,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd

BASE=['mean_doy_centered','mean_doy_sq','GLORYS_NovFeb_thetao_C','author_SIC_150km_NovFeb_center_approx_fraction']
OUTCOME='predicted_d15N_season_day_equal'
SALT='GLORYS_NovFeb_salinity'

def fe(v, groups):
    v=np.asarray(v,dtype=float).copy()
    for _ in range(500):
        old=v.copy()
        for code,count in groups:
            v-= (np.bincount(code,weights=v,minlength=len(count))/count)[code]
        if np.max(abs(v-old))<1e-11:break
    else:raise ValueError('two-way source effects failed to converge')
    for code,count in groups:
        if max(abs(np.bincount(code,weights=v,minlength=len(count))/count))>1e-7:
            raise ValueError('fixed effects not removed')
    return v

def prep(d):
    g=[pd.factorize(d.site_id,sort=True)[0],
       pd.factorize(d.source_region.astype(str)+'__'+d.season.astype(str),sort=True)[0]]
    groups=[(a,np.bincount(a)) for a in g]
    x=np.column_stack([fe(d[c],groups) for c in BASE])
    y=fe(d[OUTCOME],groups)
    yr=y-x@np.linalg.lstsq(x,y,rcond=None)[0]
    return groups,x,yr

def score(s,groups,x,y):
    s=fe(s,groups)
    s=s-x@np.linalg.lstsq(x,s,rcond=None)[0]
    den=s@s
    if den<1e-12:raise ValueError('no unique source salinity information')
    n=s@y
    return float(n/den),float(n*n/(den*(y@y)))

def source(d,zip_path):
    with zipfile.ZipFile(zip_path) as z:
        m=pd.read_csv(z.open('unique_wet_cell_NovFeb_GLORYS_monthly.csv'))
    if len(m)!=5520 or not m.valid.all():raise ValueError('true 92 cells x 15 seasons x 4 source months required')
    m['season']=np.where(m.source_month.isin([11,12]),m.source_year,m.source_year-1)
    m['cell']=m.source_original_wet_grid_y.astype(str)+':'+m.source_original_wet_grid_x.astype(str)
    a=m.groupby(['season','cell']).agg(salt=('GLORYS_surface_salinity','mean'),months=('GLORYS_surface_salinity','size')).reset_index()
    if not a.months.eq(4).all():raise ValueError('source marine missing months')
    mat=a.pivot(index='season',columns='cell',values='salt')
    if mat.isna().any().any():raise ValueError('source marine incomplete')
    d=d.copy().reset_index(drop=True)
    d['cell']=d.source_wet_grid_y.astype(str)+':'+d.source_wet_grid_x.astype(str)
    years={int(k):i for i,k in enumerate(mat.index)}
    cells={k:i for i,k in enumerate(mat.columns)}
    yy=d.season.map(years).to_numpy()
    cc=d.cell.map(cells).to_numpy()
    if not np.isfinite(cc).all():raise ValueError('unmapped source marine wet grid')
    cc=cc.astype(int)
    true=mat.to_numpy()[yy,cc]
    if np.max(abs(true-d[SALT].to_numpy()))>1e-10:raise ValueError('source original real salinity values altered')
    return d,mat,yy,cc,years,cells

def spatial(d,mat,yy,cc,cells,n,seed):
    groups,x,y=prep(d)
    beta,r2=score(d[SALT],groups,x,y)
    if abs(beta-.8341458422028288)>1e-6 or abs(r2-.02880176895240346)>1e-9:
        raise ValueError('primary original model failed numerical identity')
    grouped={k:sorted(set(g.cell)) for k,g in d.groupby('source_region')}
    rng=np.random.default_rng(seed)
    z=mat.to_numpy()
    rows=[]
    for iteration in range(n):
        donors={}
        for region,c in grouped.items():
            src=np.array([cells[k] for k in c],dtype=int)
            if len(src)<2:
                donors[c[0]]=int(src[0])
                continue
            for _ in range(150):
                order=rng.permutation(len(src))
                if not np.any(order==np.arange(len(src))):break
            else:raise ValueError('region cannot be deranged')
            donors.update({c[i]:int(src[order[i]]) for i in range(len(c))})
        pseudo=z[yy,d.cell.map(donors).to_numpy(dtype=int)]
        b,s=score(pseudo,groups,x,y)
        rows.append({'iteration':iteration,'beta':b,'partial_r2':s})
    df=pd.DataFrame(rows)
    return {'source_true_beta':beta,'source_true_partial_r2':r2,
        'n_permutations':n,'random_seed':seed,
        'pseudo_beta_median':float(df.beta.median()),
        'pseudo_partial_r2_median':float(df.partial_r2.median()),
        'pseudo_partial_r2_975':float(df.partial_r2.quantile(.975)),
        'n_pseudo_r2_at_least_true':int((df.partial_r2>=r2).sum()),
        'pseudo_assignment_rank_fraction_not_a_randomization_p':float((1+(df.partial_r2>=r2).sum())/(n+1)),
        'source_regions_with_1_cell_unpermuted':[name for name,v in grouped.items() if len(v)==1],
        'provenance_note':'Real whole-cell Nov-Feb salinity trajectories shuffled only within original source regions; not an exchangeable randomized experiment.'},df

def temporal(d,mat,cc,years,cells):
    # Same original observed rows for current, earlier and later salt controls.
    eligible=d.season.map(lambda t:(t-1 in years) and (t+1 in years))
    q=d.loc[eligible].copy().reset_index(drop=True)
    if (len(q),q.site_id.nunique(),q.source_region.nunique(),q.cell.nunique())!=(721,87,12,81):
        raise ValueError('time-placebo original source eligibility drift')
    g,x,y=prep(q)
    z=mat.to_numpy()
    ind=q.cell.map(cells).to_numpy(dtype=int)
    result=[]
    for label,delta in [('preceding',-1),('current',0),('following',1)]:
        exposure=z[q.season.map(lambda t:years[t+delta]).to_numpy(dtype=int),ind]
        b,r2=score(exposure,g,x,y)
        result.append({'exposure':label,'beta':b,'partial_r2':r2})
    if abs(result[1]['beta']-.808562382535)>1e-6 or abs(result[1]['partial_r2']-.02894709375949)>1e-9:
        raise ValueError('time-matched source present coefficient drift')
    if abs(result[2]['beta']-(-.653200249627))>1e-6:
        raise ValueError('time-shift future coefficient drift')
    return {'n_site_seasons':len(q),'n_sites':q.site_id.nunique(),'regions':q.source_region.nunique(),
       'n_distinct_wet_cells':q.cell.nunique(),
       'start_seasons':sorted(q.season.unique().tolist()),'same_rows_same_controls':result,
       'future_exposure_not_direct_cause':True,
       'interpretation':'Both true-period positive and following-period negative isotope associations; biological direction and isotope baseline not identified.'}

def run(matched,glorys,out,n=1000,seed=20261117):
    with zipfile.ZipFile(matched) as z:
        d=pd.read_csv(z.open('matched_860_original_isotope_ocean_ice_site_seasons.csv'))
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(860,88,13):
        raise ValueError('GitHub source original CI cohort changed')
    d,mat,yy,cc,years,cells=source(d,glorys)
    results,df=spatial(d,mat,yy,cc,cells,n,seed)
    t=temporal(d,mat,cc,years,cells)
    report={'status':'PASS_SOURCE_AUDITED_EXPLORATORY_PLACEBO_NO_CAUSAL_OR_DIET_RESULT',
      'source_original_n':860,'source_sites':88,'source_wet_cells':82,'regions':13,
      'spatial_assignment':results,'temporally_misaligned_source_exposures':t,
      'post_selection_not_confirmatory':True,
      'caveats':['reconstructed optical delta15N, not original hierarchical diet posterior',
                 'region/cell autocorrelation means spatial permutation rank is not a causal p-value',
                 'following-year marine conditions can co-vary with prior/current unobserved processes',
                 'source 11-Feb seawater does not measure tracked foraging footprint',
                 'no fish-versus-krill fraction, isotope baseline control or prospective replication']}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/'source_region_trajectory_assignment_sensitivity.csv',index=False)
    (out/'isotope_salinity_spatial_temporal_negative_controls.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--original-860-zip',required=True)
    p.add_argument('--glorys-zip',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--permutations',type=int,default=1000)
    a=p.parse_args()
    run(a.original_860_zip,a.glorys_zip,a.out,n=a.permutations)
