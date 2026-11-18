"""All current/previous conditional effects: 72 exploratory cluster checks."""
from pathlib import Path
import hashlib,itertools,json
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/previous_september_v1'


def main():
    src=OUT/'paired_cohort.csv';ref=OUT/'correlations.csv'
    cohort=pd.read_csv(src);reference=pd.read_csv(ref)
    rng=np.random.default_rng(20261031);rows=[];checks=0
    for r in reference.to_dict('records'):
        a=cohort[(cohort.scope==r['scope'])&(cohort.species==r['species'])&(cohort.feature==r['feature'])]
        for target,control in [('current','previous'),('previous','current')]:
            z=pd.get_dummies(a.cam,dtype=float).to_numpy()
            if r['mode']=='site_year':z=np.column_stack([z,pd.get_dummies(a.season_start_year,drop_first=True,dtype=float)])
            z=np.column_stack([z,a[control]]);rank=np.linalg.matrix_rank(z)
            u,_,_=np.linalg.svd(z,full_matrices=False);q=u[:,:rank]
            y=a.y.to_numpy();ry=y-q@(q.T@y)
            x=a[target].to_numpy();rx=x-q@(q.T@x)
            assert np.linalg.norm(rx)>1e-9 and len(a)>rank+1
            h=rx/np.linalg.norm(rx);statistic=float((h@ry)**2)
            partial=float(np.corrcoef(rx,ry)[0,1])
            assert np.isclose(partial,r[target+'_given_'+control+'_r'],atol=1e-9)
            rec={k:r[k] for k in ['scope','species','mode','feature','n','sites','years']}
            rec.update(target=target,control=control,partial_r=partial,statistic=statistic)
            for label,cluster in [('site',a.cam),('year',a.season_start_year)]:
                groups,inv=np.unique(cluster,return_inverse=True);G=len(groups)
                enumerated=G<=12
                signs=np.array(list(itertools.product([-1.,1.],repeat=G))) if enumerated else rng.choice([-1.,1.],size=(9999,G))
                pseudo=ry[:,None]*signs[:,inv].T;stats=(h@pseudo)**2
                count=int((stats>=statistic-1e-10).sum())
                rec[label+'_p']=count/len(stats) if enumerated else (count+1)/(len(stats)+1)
                rec[label+'_draws']=len(stats);rec[label+'_enumerated']=enumerated
                for index in [0,len(signs)-1]:
                    yp=q@(q.T@y)+pseudo[:,index]
                    null=yp-z@np.linalg.lstsq(z,yp,rcond=None)[0]
                    design=np.column_stack([z,x]);full=yp-design@np.linalg.lstsq(design,yp,rcond=None)[0]
                    assert np.isclose(null@null-full@full,stats[index],atol=1e-7)
                    checks+=1
            rec['max_p']=max(rec['site_p'],rec['year_p']);rows.append(rec)
    t=pd.DataFrame(rows);assert len(t)==72
    for base in ['site_p','year_p','max_p']:
        for method in ['fdr_bh','fdr_by']:t[base+'_'+method]=multipletests(t[base],method=method)[1]
    t.to_csv(OUT/'cluster_sensitivity.csv',index=False)
    receipt=dict(status='exploratory_cluster_sensitivity',family_size=72,seed=20261031,
        source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),reference_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(),
        independently_refitted_draws=checks,nominal_max_below_005=int(t.max_p.lt(.05).sum()),
        bh_max_below_005=int(t.max_p_fdr_bh.lt(.05).sum()),by_max_below_005=int(t.max_p_fdr_by.lt(.05).sum()),
        limitations=['Separate site/year restricted-null signs are not calibrated two-way inference',
                    'Residual symmetry and nonstudentized score assumptions; exhaustive signs are not unconditional exactness',
                    'Post-exploration family includes both temporal effects, not project-wide correction'])
    (OUT/'cluster_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt));print(t.query("scope=='all_source_labels' and mode=='site_year' and target=='previous'")
        [['species','feature','partial_r','site_p','year_p','max_p','max_p_fdr_bh','max_p_fdr_by']].to_string(index=False))


if __name__=='__main__':main()
