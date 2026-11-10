from pathlib import Path
import csv, json, hashlib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'work/data_audit'; OUT=ROOT/'outputs/signy_exploration'; OUT.mkdir(parents=True,exist_ok=True)
YEARS=np.arange(2012,2020)
ROSTERS={'Adelie':['A1+A60','A2','A3','A4','A64'], 'Chinstrap':['C15','C16','C17','C18','C46','C47','C79','C80','C81'], 'Shag':['North Point','Shagnasty Island']}
def read(name):
    rr=list(csv.reader((DATA/name).open(encoding='utf-8-sig',newline=''))); h=rr[0]
    return [dict(zip(h,r[:len(h)-1]+[','.join(r[len(h)-1:])])) for r in rr[1:] if r]
def num(x):
    try:return float(x)
    except (ValueError,TypeError):return np.nan
rows=[]; audit=[]
for sp,fn in [('Adelie','adelie.csv'),('Chinstrap','chinstrap.csv')]:
    expected={'Adelie':'585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62','Chinstrap':'e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b'}
    assert hashlib.sha256((DATA/fn).read_bytes()).hexdigest()==expected[sp]
    for r in read(fn):
        y=int(r['SEASON'][:4]); colony=r['COLONY'].replace(' ','')
        if colony in ['A1','A60']:colony='A1+A60'
        if y not in YEARS:continue
        included=colony in ROSTERS[sp]
        audit.append(dict(species=sp,year=y,original_colony=r['COLONY'],canonical_colony=colony,included=included,comment=r['COMMENTS'],date=r['DATE_PAIR_COUNT']))
        if included:rows.append(dict(species=sp,year=y,colony=colony,count=num(r['TOTAL_NUMBER_OF_PAIRS']),source=fn,unit='reported breeding pairs',date=r['DATE_PAIR_COUNT'],comment=r['COMMENTS']))
for fn,col in [('Signy_shag_nests_north_point.csv','NO_NESTS'),('Signy_shag_nests_shagnasty.csv','TOTAL_NO_NESTS')]:
    for r in read(fn):
        y=int(r['SEASON'][:4])
        if y not in YEARS:continue
        assert r['OBJECT_COUNTED']=='occupied nests'
        rows.append(dict(species='Shag',year=y,colony=r['COLONY'],count=num(r[col]),source=fn,unit='occupied nests',date=r['DATE_COUNT'],comment=r['COMMENTS']))
        audit.append(dict(species='Shag',year=y,original_colony=r['COLONY'],canonical_colony=r['COLONY'],included=True,comment=r['COMMENTS'],date=r['DATE_COUNT']))
panel=pd.DataFrame(rows)
assert not panel.duplicated(['species','year','colony']).any(), 'Pooling needs explicit review'
assert panel['count'].notna().all() and (panel['count']>=0).all()
panel.to_csv(OUT/'matched_counts.csv',index=False)
pd.DataFrame(audit).to_csv(OUT/'selection_and_comments.csv',index=False)
def corr(x,y):return float(np.corrcoef(x,y)[0,1])
def residual(x,t):return x-np.column_stack([np.ones(len(t)),t])@np.linalg.lstsq(np.column_stack([np.ones(len(t)),t]),x,rcond=None)[0]
def metrics(mat):
    total=mat.sum(-1); neff=total**2/(mat**2).sum(-1)
    return total,neff,neff/mat.shape[-1]
def bcorr(x,y):
    x=x-x.mean(-1,keepdims=True); y=y-y.mean(-1,keepdims=True)
    return (x*y).sum(-1)/np.sqrt((x*x).sum(-1)*(y*y).sum(-1))
def stats(mat,years):
    n,k,e=metrics(mat); x=np.log(n)
    loo=[corr(np.delete(x,i),np.delete(e,i)) for i in range(len(x))]
    return dict(n_years=len(years),n_components=mat.shape[1],first_total=float(n[0]),last_total=float(n[-1]),total_percent_change=float(100*(n[-1]/n[0]-1)),first_neff=float(k[0]),last_neff=float(k[-1]),first_evenness=float(e[0]),last_evenness=float(e[-1]),pearson_logN_evenness=corr(x,e),spearman_N_evenness=float(spearmanr(n,e).statistic),detrended_r=corr(residual(x,years),residual(e,years)),first_difference_r=corr(np.diff(x)[np.diff(years)==1],np.diff(e)[np.diff(years)==1]),leave_one_year_out_min=min(loo),leave_one_year_out_max=max(loo),evenness_slope_year=float(np.polyfit(years,e,1)[0]))
rng=np.random.default_rng(20261029); results={}; annual=[]; matrices={}
for sp,roster in ROSTERS.items():
    mat=panel[panel.species==sp].pivot(index='year',columns='colony',values='count').reindex(index=YEARS,columns=roster).to_numpy()
    assert mat.shape==(8,len(roster)) and np.isfinite(mat).all()
    matrices[sp]=mat; n,k,e=metrics(mat); result=stats(mat,YEARS)
    result['sensitivities']={}
    for label,keep in [('omit_shag_2015_boundary_note',YEARS!=2015),('omit_chinstrap_no_empty_nest_data_years',~np.isin(YEARS,[2016,2017,2019]))]:
        result['sensitivities'][label]=stats(mat[keep],YEARS[keep])
    result['null_diagnostics']={}
    for cv in [0,.1,.2]:
        mean=n[:,None]*(mat.sum(0)/mat.sum())[None,:]
        means=np.broadcast_to(mean,(30000,)+mean.shape)
        if cv:means=rng.gamma(1/cv**2,means*cv**2)
        sim=rng.poisson(means).astype(float); sn,sk,se=metrics(sim)
        assert (sn>0).all()
        nr=bcorr(np.log(sn),se)
        slope=((se-se.mean(1,keepdims=True))*(YEARS-YEARS.mean())).sum(1)/((YEARS-YEARS.mean())**2).sum()
        lo=(1+(nr<=result['pearson_logN_evenness']).sum())/30001; hi=(1+(nr>=result['pearson_logN_evenness']).sum())/30001
        result['null_diagnostics'][str(cv)]={'simulations':30000,'r_q025_median_q975':np.quantile(nr,[.025,.5,.975]).tolist(),'r_two_tail_probability':float(min(1,2*min(lo,hi))),'evenness_slope_q025_median_q975':np.quantile(slope,[.025,.5,.975]).tolist()}
    results[sp]=result
    for i,y in enumerate(YEARS):annual.append(dict(species=sp,year=int(y),season=f'{y}/{str(y+1)[2:]}',total=n[i],neff=k[i],evenness=e[i],components=len(roster)))
ann=pd.DataFrame(annual);ann.to_csv(OUT/'annual_metrics.csv',index=False)
# Additional flying species: aggregate-only, excluded from spatial metrics.
pet=read('Giant_petrel_signy_nest_chick_counts.csv')
pet_n={int(r['Season'][:4]):num(r['Total_number_of_nests']) for r in pet}
totals=pd.DataFrame({sp:metrics(m)[0] for sp,m in matrices.items()},index=YEARS)
totals['Giant petrel']=[pet_n[int(y)] for y in YEARS]
totals.to_csv(OUT/'same_year_totals.csv',index_label='year')
cross=[]
for i,a in enumerate(totals):
    for b in list(totals)[i+1:]:
        x=np.log(totals[a].to_numpy());y=np.log(totals[b].to_numpy())
        cross.append(dict(species_a=a,species_b=b,raw_log_count_r=corr(x,y),detrended_r=corr(residual(x,YEARS),residual(y,YEARS)),annual_log_change_r=corr(np.diff(x),np.diff(y))))
pd.DataFrame(cross).to_csv(OUT/'cross_species_correlations.csv',index=False)
(OUT/'results.json').write_text(json.dumps({'status':'exploratory; no flight-effect estimator','years':YEARS.tolist(),'rosters':ROSTERS,'within_species':results,'cross_species':cross,'null_limit':'Independent Poisson/Gamma-Poisson error diagnostics, not serially correlated ecological null; tail areas are not confirmatory tests.'},indent=2),encoding='utf-8')
colors={'Adelie':'#007C91','Chinstrap':'#C05A28','Shag':'#7556A8'}
fig,axes=plt.subplots(2,3,figsize=(12,7.1))
for j,(sp,mat) in enumerate(matrices.items()):
    n,k,e=metrics(mat);ax=axes[0,j]
    ax.plot(YEARS,e,'o-',color=colors[sp]); ax.set_ylim(0,1.03); ax.set_title(f'{sp} | {mat.shape[1]} fixed components');ax.set_ylabel('Effective component number / J');ax.set_xlabel('Breeding season start year');ax.set_xticks([2012,2015,2019]);ax.grid(alpha=.2)
    ax=axes[1,j];ax.plot(n,e,'-',color=colors[sp],alpha=.35);ax.scatter(n,e,c=YEARS,cmap='viridis',s=55)
    for i in [0,3,7]:
        y=YEARS[i]; ax.annotate(str(y),(n[i],e[i]),xytext=(3,-14 if i==0 else 7),textcoords='offset points',fontsize=8)
    ax.set_xscale('log');ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([600,800,1000] if sp=='Chinstrap' else ([250,350,500] if sp=='Shag' else [800,1200,1800])));ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter());ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator());ax.set_ylim(0,1.03);ax.set_xlabel('Reported breeding pairs / occupied nests (log scale)');ax.set_ylabel('Effective component number / J');ax.grid(alpha=.2)
    ax.set_title(f"Pearson r = {results[sp]['pearson_logN_evenness']:+.2f}; detrended = {results[sp]['detrended_r']:+.2f}",fontsize=10)
fig.suptitle('Signy: abundance and spatial evenness, matched 2012/13–2019/20',fontsize=14)
fig.text(.5,.015,'Higher evenness = less concentration. Species use different monitored components; this is not a flight-effect test.',ha='center',fontsize=10)
fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(OUT/'signy_comparison.png',dpi=180);fig.savefig(OUT/'signy_comparison.pdf');plt.close(fig)
print(json.dumps(results,indent=2))
print('CROSS',json.dumps(cross))
