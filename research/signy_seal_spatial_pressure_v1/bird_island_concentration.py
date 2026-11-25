"""Independent Bird Island fixed seven-unit concentration test; no climate inference."""
import csv, datetime as dt, hashlib, io, json, math, sys, zipfile
from pathlib import Path
import numpy as np
PIN='338b6ac0415484667afffbe05bcfff3beb16555ea9e37d1363af8eace2c2992d'
INNER='735ab45ab76adcfcfd29a00570e572818817798e03c2727e3cd09cda74378eda'
CSV_PIN='3d182edde201668fb3a658e6b0411a666ae80374f339e28373440ad436bdf212'
ROSTER=('Johnson','Square Pond','Lower Mountain Cwm','Upper Mountain Cwm','Lower Natural Arch','Upper Natural Arch','Landing Beach')
YEARS=tuple(y for y in range(2003,2025) if y!=2005)

def sha(b):return hashlib.sha256(b).hexdigest()
def read(path):
    assert sha(path.read_bytes())==PIN
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        b=z.read('original_source.zip')
    assert sha(b)==INNER
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        files=[v for v in z.namelist() if v.endswith('/gentoo_bi_breeding_success_2025.csv')]
        assert len(files)==1
        raw=z.read(files[0])
    assert sha(raw)==CSV_PIN
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
    assert all(x[0].startswith('#') for x in rows[:28])
    assert rows[28]==['Species','Colony','Date_nests_counted','Number_of_nests','Date_chicks_counted','Number_of_chicks','Comments','','','']
    assert len(rows[29:])==287
    counts={};excluded=0
    for r in rows[29:]:
        assert len(r)==10 and not any(v.strip() for v in r[7:]) and r[0]=='Gentoo penguin'
        if r[1]=='Mountain Cwm':
            assert r[2]=='NA' and r[3].lower() in ('nan','na','')
            excluded+=1;continue
        assert r[1] in ROSTER
        date=dt.datetime.strptime(r[2],'%d/%m/%Y').date();assert date.month in (10,11,12)
        n=float(r[3]);assert math.isfinite(n) and n>=0 and n.is_integer()
        key=(date.year,r[1]);assert key not in counts;counts[key]=int(n)
    assert len(counts)==285 and excluded==2 and max(k[0] for k in counts)==2024
    return np.array([[counts[y,k] for k in ROSTER] for y in range(2003,2025)],dtype=np.int64)
def slope(y,x):
    t=np.asarray(y,dtype=float);t=t-t.mean();return float(t@np.asarray(x,dtype=float)/(t@t))
def neff(a):
    tot=a.sum(axis=-1).astype(float);ss=(a.astype(float)**2).sum(axis=-1)
    assert (ss>0).all()
    return tot**2/ss
def describe(y,a):
    tot=a.sum(axis=1);E=neff(a);s=slope(y,E);n=slope(y,tot)
    return {'years':list(map(int,y)),'total_slope_pairs_per_year':n,'neff_slope_per_year':s,'first_total':int(tot[0]),'last_total':int(tot[-1]),'first_neff':float(E[0]),'last_neff':float(E[-1]),'fractional_neff_change':float(E[-1]/E[0]-1),'annual':[{'season_start':int(yy),'total_pairs':int(nn),'neff':float(ee)} for yy,nn,ee in zip(y,tot,E)]}
def main(src,out):
    a0=read(src);y=np.array(YEARS);a=a0[np.array(list(range(2003,2025)))!=2005];assert a.shape==(21,7)
    p=describe(y,a);full=describe(range(2003,2025),a0)
    loo=[describe(np.delete(y,i),np.delete(a,i,axis=0)) for i in range(len(y))]
    p['leave_one_season_out_total_slope_range']=[min(r['total_slope_pairs_per_year'] for r in loo),max(r['total_slope_pairs_per_year'] for r in loo)]
    p['leave_one_season_out_neff_slope_range']=[min(r['neff_slope_per_year'] for r in loo),max(r['neff_slope_per_year'] for r in loo)]
    result={'status':'DESCRIPTIVE_DECLINE_GATE_FAILED' if p['total_slope_pairs_per_year']>=0 else 'DECLINE_GATE_PASSED','source_pins':{'outer_zip':PIN,'publisher_zip':INNER,'csv':CSV_PIN},'roster':list(ROSTER),'primary':p,'sensitivity_2005_included':full,'decline_eligible':p['total_slope_pairs_per_year']<0,'null_models':{},'independent_geographic_systems':1,'climate_effect_test':False}
    if result['decline_eligible']:
        rng=np.random.default_rng(20261125);tot=a.sum(axis=1);shares=a.sum(axis=0)/a.sum();mu=tot[:,None]*shares[None,:];t=y-y.mean();den=t@t;target=p['neff_slope_per_year']
        for cv in (0,.1,.2):
            scores=[]
            for _ in range(50):
                rate=np.broadcast_to(mu,(2000,*mu.shape)) if cv==0 else rng.gamma(1/cv**2,cv**2,size=(2000,*mu.shape))*mu
                draws=rng.poisson(rate);bad=np.where(draws.sum(axis=-1)==0)
                while len(bad[0]):
                    bmu=mu[bad[1]];lam=bmu if cv==0 else rng.gamma(1/cv**2,cv**2,size=bmu.shape)*bmu
                    draws[bad]=rng.poisson(lam);bad=np.where(draws.sum(axis=-1)==0)
                scores.extend((neff(draws)@t/den).tolist())
            scores=np.array(scores);q=np.quantile(scores,[.025,.975]);hit=int((scores<=target).sum())
            result['null_models'][str(cv)]={'replicates':len(scores),'one_sided_p':(hit+1)/(len(scores)+1),'null_q025_q975':list(map(float,q)),'n_le_observed':hit}
        result['pooled_shares']=dict(zip(ROSTER,map(float,shares)));result['replication_supported']=target<0 and all(v['one_sided_p']<=.05 for v in result['null_models'].values())
    else:result['replication_supported']=None
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('primary','sensitivity_2005_included')},indent=2));print('primary:',{k:v for k,v in p.items() if k!='annual'});print('sensitivity:',{k:v for k,v in full.items() if k!='annual'})
if __name__=='__main__':main(Path(sys.argv[1]),Path(sys.argv[2]))
