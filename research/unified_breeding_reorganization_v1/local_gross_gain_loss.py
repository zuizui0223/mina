"""V3 local source comparator. Same exact V2 matched starts, no inference."""
import argparse, csv, hashlib, json, sys
from pathlib import Path
import numpy as np
from matched_lags import f, EXPECTED_SHA256, panel_dict, check_neff, LAGS
from jncc_gross_gain_loss import measures, local
from jncc_all_direction import group
def main():
    ap=argparse.ArgumentParser()
    for n in ('palmer','signy-ad','signy-ch','ross','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args()
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
    prior=json.loads((Path(__file__).parent/'MATCHED_LAGS_RESULT_20261125.json').read_text())
    out={'status':'EXECUTED_LOCAL_GAIN_LOSS','panels':{},'interpretation':'Six already studied panels, five selected for decline; 71 common starts; overlapping contrasts not independent.'}
    allrows=[]
    def summarize(rows):
        z=[r['m'] for r in rows]
        if not z:return {'n':0}
        return {'n':len(z),'mixed':sum(q['mixed'] for q in z),'material':sum(q['material'] for q in z),'median_C':float(np.median([q['C'] for q in z])),'any_gain':sum(q['any_gain'] for q in z),'any_loss':sum(q['any_loss'] for q in z),'positive_deltaU':sum(q['deltaU']>0 for q in z),'positive_deltaU_nonmixed':sum(q['deltaU']>0 and not q['mixed'] for q in z),'any_positive_to_zero':sum(q['positive_to_zero']>0 for q in z),'any_zero_to_positive':sum(q['zero_to_positive']>0 for q in z)}
    for key,panel in panels.items():
        anchors=[y for y in sorted(panel) if all(y+h in panel for h in LAGS)]
        assert anchors==prior['panels'][key]['common_start']['anchors']
        rows=[]
        for y in anchors:
            for h in LAGS:
                x=panel[y].astype(np.int64);z=panel[y+h].astype(np.int64)
                rows.append({'year':y,'lag':h,'group':group(x.sum(),z.sum()),'m':local(x,z)})
        out['panels'][key]={'anchors':len(anchors),'by_lag':{str(h):summarize([v for v in rows if v['lag']==h]) for h in LAGS}}
        allrows.extend(rows)
    assert len(allrows)==213
    out['descriptive_overlapping_rows_by_lag']={str(h):summarize([v for v in allrows if v['lag']==h]) for h in LAGS}
    out['descriptive_by_lag_and_direction']={str(h):{g:summarize([v for v in allrows if v['lag']==h and v['group']==g]) for g in ('decline','near_stable','increase')} for h in LAGS}
    a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
