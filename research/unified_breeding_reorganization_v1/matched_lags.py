"""V2 same-start and same-end temporal contrast on source-pinned original panels."""
import argparse, csv, hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import build_replicated_concentration_figure_data as f
from scripts.fetch_lter_census import EXPECTED_SHA256
LAGS=(1,5,10)
def state(n):
    n=np.asarray(n,dtype=float);N=n.sum()
    if len(n)<3 or np.any(n<0) or np.any(n!=np.floor(n)) or N<2: raise ValueError('invalid composition')
    p=n/N
    return N,p,float(np.sum(n*(n-1))/(N*(N-1)))
def pair(a,b):
    n,p,u=state(a);m,q,v=state(b)
    return np.array([.5*abs(q-p).sum(),u+v-2*np.dot(p,q),v-u,np.log(m/n)])
def med(v):
    return [float(x) for x in np.median(v,axis=0)]
KEYS=('TV','D2','deltaU','logNratio')
def matched(panel,direction):
    years=sorted(panel);anchor=[y for y in years if all(y+direction*h in panel for h in LAGS)]
    out={'anchors':anchor,'n':len(anchor)}
    if len(anchor)<3:return out
    vals=np.array([[pair(panel[y],panel[y+h]) if direction==1 else pair(panel[y-h],panel[y]) for h in LAGS] for y in anchor])
    out['lag_medians']={str(h):dict(zip(KEYS,med(vals[:,i,:]))) for i,h in enumerate(LAGS)}
    diff=vals[:,2,:]-vals[:,0,:]
    out['median_within_anchor_10minus1']=dict(zip(KEYS,med(diff)))
    out['positive_within_anchor_10minus1']=dict(zip(KEYS,np.sum(diff>0,axis=0).astype(int).tolist()))
    out['strata_by_lag']={str(h):{'decline':int((vals[:,i,3]<-np.log(1.1)).sum()),'stable':int((abs(vals[:,i,3])<=np.log(1.1)).sum()),'increase':int((vals[:,i,3]>np.log(1.1)).sum())} for i,h in enumerate(LAGS)}
    return out
def panel_dict(yr,mat):
    assert mat.shape[1]==len(yr)
    out={}
    for y,n in zip(yr,mat.T):
        if n.sum()>=2:
            state(n);out[int(y)]=n
    return out
def check_neff(panel,first,last,annual=None):
    ne={y:1/np.dot(state(n)[1],state(n)[1]) for y,n in panel.items()}
    assert np.isclose(ne[min(ne)],first,atol=1e-10,rtol=0)
    assert np.isclose(ne[max(ne)],last,atol=1e-10,rtol=0)
    if annual is not None:
        assert set(ne)=={int(y) for y in annual}
        assert all(np.isclose(ne[int(y)],v,atol=1e-10,rtol=0) for y,v in annual.items())
def selftest():
    a=[40,30,20,10];b=[10,20,30,40]
    assert np.isclose(pair(a,b)[0],.4) and np.isclose(pair(a,b)[2],0)
    assert pair(a,[20,15,10,5])[1]<0
    x={y:a for y in (1990,1991,1995,2000,2005,2010)}
    assert matched(x,1)['anchors']==[1990]
    assert matched(x,-1)['anchors']==[]
def main():
    ap=argparse.ArgumentParser()
    for n in ('palmer','signy-ad','signy-ch','ross','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();selftest()
    assert hashlib.sha256(a.palmer.read_bytes()).hexdigest()==EXPECTED_SHA256
    raw=a.ross.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='eaf47bf87158ef219d75b1be9eb8e50d0703ebaa'
    root=Path(__file__).resolve().parents[2];rd=root/'results'
    p=json.loads((rd/'PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json').read_text())['observed']
    panels={}
    for name,(units,y,m) in f._palmer_panels(a.palmer).items():
        panel=panel_dict(y,m);check_neff(panel,p[name]['first_neff'],p[name]['last_neff']);panels['Palmer_'+name]=panel
    ad,meta=f.read_official_zip(a.signy_ad)
    assert meta['selected_csv_sha256']==f.SIGNY_ADELIE_SHA
    y,m=f._signy_panel(ad,f.SIGNY_ADELIE_UNITS,canonicalize=f._canonical_adelie);panel=panel_dict(y,m)
    obs=json.loads((rd/'SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json').read_text())['observed'];check_neff(panel,obs['first_neff'],obs['last_neff'],obs['annual_neff']);panels['Signy_ADPE']=panel
    ch,meta=f.read_official_zip(a.signy_ch)
    assert meta['selected_csv_sha256']==f.SIGNY_CHINSTRAP_SHA
    y,m=f._signy_panel(ch,f.SIGNY_CHINSTRAP_UNITS);panel=panel_dict(y,m)
    obs=json.loads((rd/'SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json').read_text())['observed'];check_neff(panel,obs['first_effective_breeding_patch_number'],obs['last_effective_breeding_patch_number'],obs['annual_effective_breeding_patch_number']);panels['Signy_CHPE']=panel
    ross={}
    for row in csv.DictReader(raw.decode().splitlines()):
        y=int(row.pop('year'));ross[y]=np.array([int(x) for x in row.values()])
    assert len(ross)==26;panels['Ross_ADPE']=ross
    assert len(panels)==6
    result={'status':'EXECUTED_MATCHED_LOCAL_LAGS','panel_count':6,'geographic_systems':3,'sources':{'palmer_sha256':EXPECTED_SHA256,'signy_ad_selected_csv_sha256':f.SIGNY_ADELIE_SHA,'signy_ch_selected_csv_sha256':f.SIGNY_CHINSTRAP_SHA,'ross_blob':'eaf47bf87158ef219d75b1be9eb8e50d0703ebaa'},'panels':{}}
    for key,panel in panels.items():
        result['panels'][key]={'first':min(panel),'last':max(panel),'years':len(panel),'units':len(next(iter(panel.values()))),'common_start':matched(panel,1),'common_end':matched(panel,-1)}
    for direction in ('common_start','common_end'):
        good=[x[direction] for x in result['panels'].values() if x[direction]['n']>=3]
        result[direction+'_summary']={'supported_panels':len(good),'anchors_total':sum(x['n'] for x in good),'positive_median_10minus1':{k:sum(x['median_within_anchor_10minus1'][k]>0 for x in good) for k in KEYS}}
    result['limitations']='Five preselected declining panels; 3 geographic systems; repeated anchors overlap; no temporal scale causal effect, random population sample or new independent replication.'
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
