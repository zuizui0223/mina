"""Exploratory source-pinned multiscale diet distances, 1 island x 9 years.

Size across all three species is conditional on UNVERIFIED Gentoo unit equality.
Raw stomachs stay in the external workspace, not in git outputs.
"""
from pathlib import Path
import argparse, hashlib, io, itertools, json, zipfile
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
from scipy.stats import pearsonr

SP=('Adelie','Chinstrap','Gentoo');YEARS=list(range(2001,2010))
IDS=['eb421e6d-b93b-4174-904b-9a7b0b401403','95e38251-797c-495a-abc0-40a613599759','fb9bd975-e6fe-406c-84be-01e57d612b5e']
HASHES=[('ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d','318499115f56ce0f9010ea304ec65f969abd063bad7686e9289af6b20b1e03c3'),('a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a','be3b68b22a7e36d3cc6cf81f17d18df9428ca176d8249ee2e63f5b56a93153b6'),('6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902','99dc437260a7782109a745ec53f61f22246bed3ad8a353748fcef4cac9f64164')]
METRICS=['fish','size_assumed_common_scale','stage_labels']
CAT=['J','FS','FAS','MS','MAS'];UNKNOWN={'U','Unknown','UNKNOWN','nan',''}

def save(df,path):df.to_csv(path,index=False,lineterminator='\n')
def corr(x,y):
    return float(np.corrcoef(x,y)[0,1]) if len(x)>=4 and np.std(x)>0 and np.std(y)>0 else np.nan
def resid(x,t):return sm.OLS(x,sm.add_constant(t)).fit().resid
def dist(a,b,metric,dx):
    delta=np.abs(a-b)
    return float(delta[0]) if metric=='fish' else float(delta@dx) if metric=='size_assumed_common_scale' else float(delta.sum()/2)

def load(workspace,out):
    src=out/'source';src.mkdir(parents=True,exist_ok=True)
    ss={};kk={};manifest=[];quality=[]
    for sp,uid,(hs,hk) in zip(SP,IDS,HASHES):
        path=src/(sp+'.zip');url=f'https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={uid}&output=zip.tree'
        if not path.exists():
            r=requests.get(url,timeout=90);r.raise_for_status();path.write_bytes(r.content)
        with zipfile.ZipFile(path) as z:
            raw=[z.read(next(n for n in z.namelist() if n.endswith(suffix))) for suffix in ['_diet_summary.csv','_diet_krill.csv','maturity_stages_code.csv']]
        assert hashlib.sha256(raw[0]).hexdigest()==hs and hashlib.sha256(raw[1]).hexdigest()==hk
        s,k=[pd.read_csv(io.BytesIO(b)) for b in raw[:2]]
        assert not s.duplicated(['DATE','RECORD_ID']).any()
        for frame in [s,k]:
            dt=pd.to_datetime(frame.DATE,format='%Y-%m-%d');assert dt.dt.month.isin([11,12,1,2,3,4]).all()
            frame['year']=dt.dt.year-(dt.dt.month<=4).astype(int)
            frame['day']=(dt-pd.to_datetime(frame.year.astype(str)+'-10-01')).dt.days
        col=next(c for c in k if c.startswith('REMOVED_CARAPACE_LENGTH'))
        k['length']=pd.to_numeric(k[col],errors='coerce')
        k['stage']=k.MATURITY_STAGE.fillna('').astype(str).str.strip()
        fk,ck,tk,ek=[pd.to_numeric(s[c],errors='coerce') for c in ['FISH_MASS_g','CRUSTACEAN_MASS_g','TOTAL_MASS_g','EUPHAUSIA_SUPERBA_MASS_g']]
        valid=(fk.ge(0)&ck.ge(0)&tk.gt(0)&(fk+ck).gt(0)&(fk+ck).le(tk*1.05+.05)&(ek.isna()|ek.le(ck*1.05+.05)))
        s['fish']=np.where(valid,fk/(fk+ck),np.nan)
        s=s[s.year.isin(YEARS)].copy();k=k[k.year.isin(YEARS)].copy()
        keys=s[['DATE','RECORD_ID']];matched=k.merge(keys,on=['DATE','RECORD_ID'],how='inner',validate='many_to_one')
        ss[sp]=s;kk[sp]=matched
        quality.append(dict(species=sp,n_summary=len(s),n_valid_fish=int(s.fish.notna().sum()),n_krill_rows=len(k),n_matched_krill_rows=len(matched),n_unmatched_krill_rows=len(k)-len(matched),n_invalid_length=int((~matched.length.gt(0)).sum()),n_unknown_stage=int(matched.stage.isin(UNKNOWN).sum()),length_column=col))
        manifest.append(dict(species=sp,url=url,summary_sha256=hs,krill_sha256=hk,maturity_catalog_sha256=hashlib.sha256(raw[2]).hexdigest(),length_column=col))
    save(pd.DataFrame(quality),out/'source_quality.csv')
    grid=np.sort(np.unique(np.concatenate([v.loc[v.length.gt(0),'length'].to_numpy() for v in kk.values()])))
    dx=np.diff(grid)
    labels=sorted(set().union(*(set(k.stage) for k in kk.values()))-UNKNOWN)
    groups={};support=[];stages=[]
    for sp in SP:
        kg={(str(a),str(b)):g for (a,b),g in kk[sp].groupby(['DATE','RECORD_ID'])}
        for y in YEARS:
            entries=[]
            for row in ss[sp][ss[sp].year==y].itertuples():
                g=kg.get((row.DATE,row.RECORD_ID),pd.DataFrame(columns=['length','stage']))
                length=np.sort(g.loc[g.length.gt(0),'length'].to_numpy(dtype=float))
                known=g.loc[~g.stage.isin(UNKNOWN),'stage'];catalog=g.loc[g.stage.isin(CAT),'stage']
                st=np.array([(known==lab).sum() for lab in labels],dtype=float)
                ca=np.array([(catalog==lab).sum() for lab in CAT],dtype=float)
                for code,n in g.stage.value_counts().items():stages.append(dict(species=sp,year=y,code=code,n_krill=n))
                entries.append(dict(day=row.day,fish=np.array([row.fish]) if np.isfinite(row.fish) else None,
                    size_assumed_common_scale=np.searchsorted(length,grid[:-1],side='right')/len(length) if len(length) else None,
                    stage_labels=st/st.sum() if st.sum() else None,
                    stage_catalog=ca/ca.sum() if ca.sum() else None,
                    n_length=len(length),n_stage=int(st.sum()),n_catalog=int(ca.sum()),length=length))
            groups[sp,y]=entries
            support.append(dict(species=sp,year=y,n_stomachs=len(entries),n_fish=sum(e['fish'] is not None for e in entries),n_size=sum(e['n_length']>0 for e in entries),n_stage=sum(e['n_stage']>0 for e in entries),n_catalog=sum(e['n_catalog']>0 for e in entries),date_min=min(e['day'] for e in entries),date_max=max(e['day'] for e in entries)))
    save(pd.DataFrame(support),out/'species_year_support.csv')
    save(pd.DataFrame(stages).groupby(['species','year','code'],as_index=False).n_krill.sum(),out/'stage_code_counts.csv')
    root=Path(__file__).resolve().parents[2]
    icepath=root/'outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv'
    ice=pd.read_csv(icepath);ice=ice[(ice.site_id=='GOPT')&(ice.inner_km==0)&ice.year.isin(YEARS)]
    assert not ice.duplicated(['year','month']).any() and ice.complete_month.all() and len(ice)==36
    env=ice.groupby('year').sic_mean.mean().reindex(YEARS).to_numpy()
    sep=ice[ice.month==9].set_index('year').sic_mean.reindex(YEARS).to_numpy()
    manifest.append(dict(source='GOPT 0-100km original derived OSI SAF',sha256=hashlib.sha256(icepath.read_bytes()).hexdigest()))
    (out/'source_manifest.json').write_text(json.dumps(dict(sources=manifest,stage_labels=labels,documented_catalog_codes=CAT,unit_gate='Gentoo numerical carapace scale not verified as mm; triple-species size is conditional only'),indent=2),encoding='utf-8',newline='\n')
    return groups,dx,env,sep

def eligible(entries,metric,variant='full'):
    key='stage_catalog' if variant=='catalog_only' and metric=='stage_labels' else metric
    result=[e for e in entries if e[key] is not None]
    if variant=='common_stomachs':result=[e for e in result if all(e[m] is not None for m in METRICS)]
    if variant=='min5_krill':
        if metric=='size_assumed_common_scale':result=[e for e in result if e['n_length']>=5]
        if metric=='stage_labels':result=[e for e in result if e['n_stage']>=5]
    return result,key

def calculate(groups,dx,variant='full',window=None):
    rows=[];support=[]
    for y in YEARS:
        for metric in METRICS:
            results={}
            for a,b in [('Gentoo','Adelie'),('Gentoo','Chinstrap'),('Adelie','Chinstrap')]:
                aa,key=eligible(groups[a,y],metric,variant);bb,_=eligible(groups[b,y],metric,variant)
                if window is not None and aa and bb:
                    ad=np.array([e['day'] for e in aa]);bd=np.array([e['day'] for e in bb]);close=np.abs(ad[:,None]-bd)<=window
                    aa=[e for e,k in zip(aa,close.any(axis=1)) if k];bb=[e for e,k in zip(bb,close.any(axis=0)) if k]
                n,m=len(aa),len(bb)
                val=dist(np.mean([e[key] for e in aa],axis=0),np.mean([e[key] for e in bb],axis=0),metric,dx) if min(n,m)>=3 else np.nan
                results[a+'-'+b]=val
                rows.append(dict(variant=variant,window=window if window is not None else -1,year=y,metric=metric,pair=a+'-'+b,distance=val))
                support.append(dict(variant=variant,window=window if window is not None else -1,year=y,metric=metric,pair=a+'-'+b,n_a=n,n_b=m,median_date_gap=float(np.median([e['day'] for e in aa])-np.median([e['day'] for e in bb])) if n and m else np.nan))
            vals=[results['Gentoo-Adelie'],results['Gentoo-Chinstrap']]
            rows.append(dict(variant=variant,window=window if window is not None else -1,year=y,metric=metric,pair='Gentoo-vs-others',distance=float(np.mean(vals)) if np.isfinite(vals).all() else np.nan))
    return pd.DataFrame(rows),pd.DataFrame(support)

def describe(x,y,years):
    mask=np.isfinite(y);x=x[mask];years=years[mask];y=y[mask]
    if len(y)<4:return dict(n_years=len(y),r=np.nan)
    m=sm.OLS(y,sm.add_constant(x/10)).fit();hc=m.get_robustcov_results(cov_type='HC3',use_t=True)
    loo=[corr(np.delete(x,i),np.delete(y,i)) for i in range(len(y))]
    adjacent=np.diff(years)==1
    return dict(n_years=len(y),r=corr(x,y),slope_per_10pp=float(m.params[1]),hc3_low=float(hc.conf_int()[1,0]),hc3_high=float(hc.conf_int()[1,1]),p_hc3=float(hc.pvalues[1]),detrended_r=corr(resid(x,years),resid(y,years)),first_difference_r=corr(np.diff(x)[adjacent],np.diff(y)[adjacent]),loo_min=float(np.nanmin(loo)),loo_max=float(np.nanmax(loo)),circular_extreme=sum(abs(corr(x,np.roll(y,i)))>=abs(corr(x,y))-1e-12 for i in range(len(y))),circular_denominator=len(y))

def run(workspace,nrep=1000):
    out=workspace/'outputs/niche_multiscale_v1';out.mkdir(parents=True,exist_ok=True)
    groups,dx,env,sep=load(workspace,out)
    frames=[];supports=[]
    for variant in ['full','common_stomachs','min5_krill','catalog_only']:
        f,s=calculate(groups,dx,variant);frames.append(f);supports.append(s)
    for w in [7,14]:
        f,s=calculate(groups,dx,'date_matched',w);frames.append(f);supports.append(s)
    annual=pd.concat(frames,ignore_index=True);support=pd.concat(supports,ignore_index=True)
    annual['sic_aug_nov']=annual.year.map(dict(zip(YEARS,env)));annual['sic_sep']=annual.year.map(dict(zip(YEARS,sep)))
    save(annual,out/'annual_distances.csv');save(support,out/'pair_support.csv')
    results=[]
    for (variant,w,metric,pair),g in annual.groupby(['variant','window','metric','pair']):
        g=g.sort_values('year')
        for name,x in [('Aug-Nov',env),('September',sep)] if variant=='full' else [('Aug-Nov',env)]:
            results.append(dict(variant=variant,window=w,metric=metric,pair=pair,ice_window=name,**describe(x,g.distance.to_numpy(),np.array(YEARS))))
    results=pd.DataFrame(results)
    matched_comparisons=[]
    for w in [7,14]:
        for metric in METRICS:
            for pair in ['Gentoo-Adelie','Gentoo-Chinstrap','Adelie-Chinstrap','Gentoo-vs-others']:
                matched=annual[(annual.variant=='date_matched')&(annual.window==w)&(annual.metric==metric)&(annual.pair==pair)].dropna(subset=['distance'])
                baseline=annual[(annual.variant=='full')&(annual.metric==metric)&(annual.pair==pair)&annual.year.isin(matched.year)].sort_values('year')
                matched=matched.sort_values('year')
                matched_comparisons.append(dict(window=w,metric=metric,pair=pair,n_years=len(matched),years=';'.join(map(str,matched.year)),unfiltered_same_year_r=corr(baseline.sic_aug_nov,baseline.distance),date_filtered_r=corr(matched.sic_aug_nov,matched.distance)))
    save(pd.DataFrame(matched_comparisons),out/'date_matching_same_year_comparison.csv')
    full=annual[(annual.variant=='full')&(annual.pair=='Gentoo-vs-others')].pivot(index='year',columns='metric',values='distance').reindex(index=YEARS,columns=METRICS)
    assert not full.isna().any().any()
    # Entire 9! permutation family, common shuffled ice order across all endpoints.
    indices=np.array(list(itertools.permutations(range(9))),dtype=np.int16)
    x=(env-env.mean())/np.linalg.norm(env-env.mean());y=full.to_numpy();yc=(y-y.mean(axis=0))/np.linalg.norm(y-y.mean(axis=0),axis=0)
    perm=x[indices]@yc;observed=x@yc
    exact=[]
    for j,metric in enumerate(METRICS):
        exact.append(dict(metric=metric,r=observed[j],n_permutations=len(indices),p_exact=float(np.mean(np.abs(perm[:,j])>=abs(observed[j])-1e-12)),p_max3=float(np.mean(np.max(np.abs(perm),axis=1)>=abs(observed[j])-1e-12))))
    save(pd.DataFrame(exact),out/'exact_three_metric_family.csv')
    cat=annual[(annual.variant=='catalog_only')&(annual.metric=='stage_labels')&(annual.pair=='Gentoo-vs-others')].sort_values('year').distance.to_numpy()
    cat=(cat-cat.mean())/np.linalg.norm(cat-cat.mean());cat_r=float(x@cat)
    save(pd.DataFrame([dict(metric='stage_catalog_only',r=cat_r,p_exact=float(np.mean(np.abs(x[indices]@cat)>=abs(cat_r)-1e-12)),n_permutations=len(indices),scope='posthoc code-definition sensitivity; not separate confirmed finding')]),out/'catalog_stage_exact_sensitivity.csv')
    save(results,out/'associations.csv')
    # All resampling intervals below are conditional on these 9 observed years.
    rng=np.random.default_rng(20261105);resamples=[];annual_balanced=[]
    for metric in METRICS:
        arrays={};mins=[]
        for year in YEARS:
            for sp in SP:
                entries,key=eligible(groups[sp,year],metric)
                arrays[sp,year]=np.stack([e[key] for e in entries]);mins.append(len(entries))
        fixed=min(mins);assert fixed>=3
        for mode in ['equal_within_year','equal_all_years','stomach_bootstrap']:
            sampled=np.empty((nrep,len(YEARS)))
            for iy,year in enumerate(YEARS):
                nwithin=min(len(arrays[sp,year]) for sp in SP)
                for b in range(nrep):
                    means={}
                    for sp in SP:
                        a=arrays[sp,year];n=len(a) if mode=='stomach_bootstrap' else fixed if mode=='equal_all_years' else nwithin
                        idx=rng.choice(len(a),n,replace=(mode=='stomach_bootstrap'));means[sp]=a[idx].mean(axis=0)
                    sampled[b,iy]=(dist(means['Gentoo'],means['Adelie'],metric,dx)+dist(means['Gentoo'],means['Chinstrap'],metric,dx))/2
            rr=np.array([corr(env,v) for v in sampled]);slopes=np.array([np.polyfit(env/10,v,1)[0] for v in sampled])
            resamples.append(dict(metric=metric,method=mode,n_resamples=nrep,minimum_stomachs=fixed,r_median=np.nanmedian(rr),r_low=np.nanquantile(rr,.025),r_high=np.nanquantile(rr,.975),fraction_positive=np.mean(rr>0),slope_median=np.median(slopes),interval_scope='conditional stomach resampling only; no independent years added'))
            for iy,year in enumerate(YEARS):annual_balanced.append(dict(metric=metric,method=mode,year=year,distance_mean=sampled[:,iy].mean(),distance_low=np.quantile(sampled[:,iy],.025),distance_high=np.quantile(sampled[:,iy],.975)))
    save(pd.DataFrame(resamples),out/'sample_size_sensitivity.csv');save(pd.DataFrame(annual_balanced),out/'resampled_annual_distances.csv')
    # Preserve signed earlier endpoint to reconcile with source-linked older result.
    fishsigned=[]
    for y in YEARS:
        vals={sp:np.mean([e['fish'][0] for e in groups[sp,y] if e['fish'] is not None]) for sp in SP}
        fishsigned.append(dict(year=y,**vals,signed_gap=vals['Gentoo']-(vals['Adelie']+vals['Chinstrap'])/2))
    save(pd.DataFrame(fishsigned),out/'prior_signed_fish_gap.csv')
    assert abs(corr(env,np.array([r['signed_gap'] for r in fishsigned]))-.7839)<.0001
    summary=dict(status='analysis_complete_pending_independent_verification',n_islands=1,n_years=9,years=YEARS,n_resamples=nrep,size_gate='three-species size is numerical common-scale assumption; no verified Gentoo mm conversion',maturity_gate='recorded labels; catalogue-only sensitivity; no inferred adult proportions',prior_signed_fish_r=corr(env,np.array([r['signed_gap'] for r in fishsigned])),primary_associations=results[(results.variant=='full')&(results.pair=='Gentoo-vs-others')&(results.ice_window=='Aug-Nov')].to_dict('records'),exact=exact)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(summary,indent=2));print(pd.DataFrame(resamples).to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--resamples',type=int,default=1000);a=p.parse_args();run(a.workspace,a.resamples)
