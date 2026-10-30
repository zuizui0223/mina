"""Restricted-null cluster sign sensitivity for all 48 quadratic checks.

Same score convention as the existing drift block; not exact multiway inference.
"""
from pathlib import Path
import hashlib,itertools,json
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/nonlinear_association_v1'
F=['airC','ice10','salt01','waterC']


def main():
    src=ROOT/'outputs/relationship_response_v1/cohort.csv'
    shapes=OUT/'shape_sensitivity.csv'
    cohort=pd.read_csv(src);reference=pd.read_csv(shapes)
    rng=np.random.default_rng(20261031);rows=[];checks=0
    for r in reference.to_dict('records'):
        a=cohort[(cohort.scope==r['scope'])&(cohort.species==r['species'])]
        x=((a[F]-a[F].mean())/a[F].std()).to_numpy()
        z=pd.get_dummies(a.cam,dtype=float).to_numpy()
        if r['mode']=='site_year':z=np.column_stack([z,pd.get_dummies(a.year,drop_first=True,dtype=float)])
        z=np.column_stack([z,x]);rank=np.linalg.matrix_rank(z)
        u,_,_=np.linalg.svd(z,full_matrices=False);q=u[:,:rank]
        y=a.y.to_numpy();ry=y-q@(q.T@y)
        quadratic=x[:,F.index(r['feature'])]**2
        rq=quadratic-q@(q.T@quadratic);h=rq/np.linalg.norm(rq)
        statistic=float((h@ry)**2)
        assert np.isclose(statistic/(ry@ry),r['partial_r2'],atol=1e-9)
        rec={k:r[k] for k in ['scope','species','mode','feature','n','sites','years','partial_r2']}
        rec['statistic']=statistic
        for label,cluster in [('site',a.cam),('year',a.year)]:
            groups,inv=np.unique(cluster,return_inverse=True);G=len(groups)
            enumerated=G<=12
            signs=np.array(list(itertools.product([-1.,1.],repeat=G))) if enumerated else rng.choice([-1.,1.],size=(9999,G))
            pseudo=ry[:,None]*signs[:,inv].T
            stats=(h@pseudo)**2
            count=int((stats>=statistic-1e-10).sum())
            rec[label+'_p']=count/len(stats) if enumerated else (count+1)/(len(stats)+1)
            rec[label+'_draws']=len(stats);rec[label+'_enumerated']=enumerated
            for index in [0,len(signs)-1]:
                yp=q@(q.T@y)+pseudo[:,index]
                null=yp-z@np.linalg.lstsq(z,yp,rcond=None)[0]
                full_design=np.column_stack([z,quadratic])
                full=yp-full_design@np.linalg.lstsq(full_design,yp,rcond=None)[0]
                assert np.isclose(null@null-full@full,stats[index],atol=1e-7)
                checks+=1
        rec['max_p']=max(rec['site_p'],rec['year_p']);rows.append(rec)
    t=pd.DataFrame(rows);assert len(t)==48
    for base in ['site_p','year_p','max_p']:
        for method in ['fdr_bh','fdr_by']:
            t[base+'_'+method]=multipletests(t[base],method=method)[1]
    t.to_csv(OUT/'cluster_sensitivity.csv',index=False)
    receipt=dict(status='exploratory_cluster_sensitivity',family_size=48,seed=20261031,
        source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),shape_sha256=hashlib.sha256(shapes.read_bytes()).hexdigest(),
        independently_refitted_draws=checks,nominal_max_below_005=int(t.max_p.lt(.05).sum()),
        bh_max_below_005=int(t.max_p_fdr_bh.lt(.05).sum()),by_max_below_005=int(t.max_p_fdr_by.lt(.05).sum()),
        limitations=['One-way site/year restricted-null sign flips separately; maximum not calibrated multiway inference',
                    'Exhaustive signs do not make nuisance-residual sign tests exact under arbitrary errors',
                    'Post-exploration family; not project-wide correction or independent confirmation',
                    'Score statistic not studentized; symmetry and small-cluster limitations remain'])
    (OUT/'cluster_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt));print(t.query("species=='Adelie' and feature=='waterC'").to_string(index=False))


if __name__=='__main__':main()
