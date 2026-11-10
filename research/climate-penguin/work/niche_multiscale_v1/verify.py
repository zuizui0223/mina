"""Independent csv/Counter/scipy verification, without importing analysis helpers."""
from pathlib import Path
import argparse,csv,datetime,hashlib,io,itertools,json,math,zipfile
from collections import Counter,defaultdict
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

def numeric(v):
    try:x=float(v)
    except (ValueError,TypeError):return None
    return x if math.isfinite(x) and x>=0 else None

def run(out):
    sp=['Adelie','Chinstrap','Gentoo'];data={};groups=defaultdict(list);sources=[]
    for s in sp:
        with zipfile.ZipFile(out/'source'/f'{s}.zip') as z:
            a=z.read(next(n for n in z.namelist() if n.endswith('_diet_summary.csv')))
            b=z.read(next(n for n in z.namelist() if n.endswith('_diet_krill.csv')))
        originals=list(csv.DictReader(io.StringIO(a.decode('utf-8-sig'))));krill=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
        sources.append(dict(species=s,summary_sha256=hashlib.sha256(a).hexdigest(),krill_sha256=hashlib.sha256(b).hexdigest()))
        bykey=defaultdict(list)
        for row in krill:bykey[row['DATE'],row['RECORD_ID']].append(row)
        for row in originals:
            d=datetime.date.fromisoformat(row['DATE']);yr=d.year-(d.month<=4)
            if not 2001<=yr<=2009:continue
            fish,crust,total,e=[numeric(row[k]) for k in ['FISH_MASS_g','CRUSTACEAN_MASS_g','TOTAL_MASS_g','EUPHAUSIA_SUPERBA_MASS_g']]
            frac=None
            if fish is not None and crust is not None and total is not None and total>0 and fish+crust>0 and fish+crust<=total*1.05+.05 and (e is None or e<=crust*1.05+.05):frac=fish/(fish+crust)
            lengths=[];st=Counter()
            for k in bykey[row['DATE'],row['RECORD_ID']]:
                length=numeric(k.get('REMOVED_CARAPACE_LENGTH_mm',k.get('REMOVED_CARAPACE_LENGTH')))
                if length is not None and length>0:lengths.append(length)
                label=k['MATURITY_STAGE'].strip()
                if label not in {'U','Unknown','UNKNOWN','nan','NA',''}:st[label]+=1
            groups[s,yr].append(dict(fish=frac,length=lengths,stage=st,day=(d-datetime.date(yr,10,1)).days))
    def distance(a,b,metric):
        if metric=='fish':return abs(np.mean([r['fish'] for r in a])-np.mean([r['fish'] for r in b]))
        if metric=='size_assumed_common_scale':
            av=[v for r in a for v in r['length']];bv=[v for r in b for v in r['length']]
            aw=[1/len(r['length'])/len(a) for r in a for _ in r['length']];bw=[1/len(r['length'])/len(b) for r in b for _ in r['length']]
            assert np.isclose(sum(aw),1) and np.isclose(sum(bw),1)
            return wasserstein_distance(av,bv,aw,bw)
        pa=Counter();pb=Counter()
        for r in a:
            for c,n in r['stage'].items():pa[c]+=n/sum(r['stage'].values())/len(a)
        for r in b:
            for c,n in r['stage'].items():pb[c]+=n/sum(r['stage'].values())/len(b)
        assert np.isclose(sum(pa.values()),1) and np.isclose(sum(pb.values()),1)
        return sum(abs(pa[c]-pb[c]) for c in pa.keys()|pb.keys())/2
    f=pd.read_csv(out/'annual_distances.csv');checked=0;checks=[]
    for variant,window in [('full',-1),('date_matched',7),('date_matched',14)]:
        for yr in range(2001,2010):
            for metric in ['fish','size_assumed_common_scale','stage_labels']:
                pairvals=[]
                for a,b in [('Gentoo','Adelie'),('Gentoo','Chinstrap'),('Adelie','Chinstrap')]:
                    key={'fish':'fish','size_assumed_common_scale':'length','stage_labels':'stage'}[metric]
                    aa=[r for r in groups[a,yr] if r[key] is not None and (key=='fish' or len(r[key])>0)]
                    bb=[r for r in groups[b,yr] if r[key] is not None and (key=='fish' or len(r[key])>0)]
                    if variant=='date_matched':
                        ac=[r for r in aa if any(abs(r['day']-q['day'])<=window for q in bb)]
                        bc=[r for r in bb if any(abs(r['day']-q['day'])<=window for q in aa)]
                        aa,bb=ac,bc
                    val=distance(aa,bb,metric) if min(len(aa),len(bb))>=3 else np.nan
                    published=f[(f.variant==variant)&(f.window==window)&(f.year==yr)&(f.metric==metric)&(f.pair==a+'-'+b)].distance.item()
                    assert np.isclose(val,published,equal_nan=True), (variant,yr,metric,a,b,val,published)
                    pairvals.append(val);checked+=1
                published=f[(f.variant==variant)&(f.window==window)&(f.year==yr)&(f.metric==metric)&(f.pair=='Gentoo-vs-others')].distance.item()
                assert np.isclose(np.mean(pairvals[:2]),published,equal_nan=True);checked+=1
    metrics=['fish','size_assumed_common_scale','stage_labels']
    d=f[(f.variant=='full')&(f.pair=='Gentoo-vs-others')].pivot(index='year',columns='metric',values='distance')[metrics]
    ice=f[(f.variant=='full')&(f.pair=='Gentoo-vs-others')&(f.metric=='fish')].sort_values('year').sic_aug_nov.to_numpy()
    # Independent permutation of distance rows instead of ice labels.
    normalized=(d.to_numpy()-d.to_numpy().mean(axis=0))/np.linalg.norm(d.to_numpy()-d.to_numpy().mean(axis=0),axis=0)
    ix=(ice-ice.mean())/np.linalg.norm(ice-ice.mean());obs=ix@normalized
    counts=np.zeros(3,dtype=int);countsmax=np.zeros(3,dtype=int);n=0
    iterator=itertools.permutations(range(9))
    while True:
        batch=list(itertools.islice(iterator,4096))
        if not batch:break
        rr=np.einsum('n,knj->kj',ix,normalized[np.array(batch)])
        counts+=(np.abs(rr)>=np.abs(obs)-1e-12).sum(axis=0)
        countsmax+=(np.max(np.abs(rr),axis=1)[:,None]>=np.abs(obs)-1e-12).sum(axis=0);n+=len(batch)
    exact=pd.read_csv(out/'exact_three_metric_family.csv').set_index('metric').loc[metrics]
    assert n==362880 and np.allclose(exact.p_exact,counts/n) and np.allclose(exact.p_max3,countsmax/n)
    result=dict(status='pass',independently_rebuilt_distance_cells=checked,independent_permutations=n,independent_exact_tests=3,raw_sources=sources,scope='full and both date-matched source reconstructions, scipy weighted W1 vs production CDF, stage and mass distances, exact p and max3; not global CI',limitations='unit equality and maturity-code harmonization remain unresolved, not cured by numerical agreement')
    (out/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8',newline='\n');print(json.dumps(result,indent=2))
    summary=json.loads((out/'summary.json').read_text(encoding='utf-8'))
    summary['status']='analysis_and_independent_numerical_verification_complete_with_source_limits'
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8',newline='\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
