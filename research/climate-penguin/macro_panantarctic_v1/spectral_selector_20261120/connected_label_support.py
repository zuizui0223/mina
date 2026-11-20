"""Same-scene positive-neighborhood support. Missing labels are NOT negatives."""
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).parent

def interior_cells(cells,ncols,radius):
    points={((int(c)-1)//ncols,(int(c)-1)%ncols) for c in cells}
    offsets=[(dr,dc) for dr in range(-radius,radius+1) for dc in range(-radius,radius+1)]
    return {r*ncols+c+1 for r,c in points if all((r+dr,c+dc) in points for dr,dc in offsets)}

def phase_counts(d,grids,phase):
    records=[];retained=[]
    for (site,scene),g in d[d.phase.eq(phase)].groupby(['site_id','Landsat.Product.Identifier.L1']):
        fit=grids[grids.site_id.eq(site)]
        if len(fit)!=1 or fit.iloc[0].status!='UNIQUE_LATTICE':continue
        if g.cell.duplicated().any() or g.season.nunique()!=1 or g.region.nunique()!=1:
            raise ValueError('Scene-row grain drift')
        core3=interior_cells(g.cell,int(fit.iloc[0].ncols),1)
        core5=interior_cells(g.cell,int(fit.iloc[0].ncols),2)
        if not core5<=core3:raise ValueError('Nested support violated')
        records.append(dict(phase=phase,site_id=site,region=g.region.iloc[0],season=int(g.season.iloc[0]),
          original_product=scene,source_positive_rows=len(g),core3_rows=len(core3),core5_rows=len(core5)))
        for cell in sorted(core3):
            retained.append(dict(phase=phase,site_id=site,original_product=scene,cell=cell,core5=cell in core5))
    return pd.DataFrame(records),pd.DataFrame(retained)

def support(s):
    records=[]
    for phase,g in s.groupby('phase'):
        for rule,col in [('source','source_positive_rows'),('core3','core3_rows'),('core5','core5_rows')]:
            a=g[g[col]>0]
            records.append(dict(phase=phase,rule=rule,sites=a.site_id.nunique(),regions=a.region.nunique(),
              seasons=a.season.nunique(),site_scene_pairs=len(a),unique_scenes=a.original_product.nunique(),
              rows=int(a[col].sum()),minimum_support=bool(a.site_id.nunique()>=30 and a.region.nunique()>=6 and a.season.nunique()>=4)))
    return pd.DataFrame(records)

def main():
    d=pd.read_csv(ROOT/'source_positive_records.csv');grids=pd.read_csv(ROOT/'training_recovered_lattices.csv')
    train,train_cells=phase_counts(d,grids,'train');s=support(train)
    passed=bool(s.loc[s.rule.eq('core3'),'minimum_support'].iloc[0])
    records=[train];cells=[train_cells]
    if passed:
        test,test_cells=phase_counts(d,grids,'test');records.append(test);cells.append(test_cells)
    all_records=pd.concat(records,ignore_index=True);all_cells=pd.concat(cells,ignore_index=True)
    all_records.to_csv(ROOT/'connected_label_scene_support.csv',index=False,lineterminator='\n')
    all_cells.to_csv(ROOT/'connected_label_cells.csv',index=False,lineterminator='\n')
    totals=support(all_records);totals.to_csv(ROOT/'connected_label_support.csv',index=False,lineterminator='\n')
    regions=[]
    for (phase,region),g in all_records.groupby(['phase','region']):
        for rule,col in [('source','source_positive_rows'),('core3','core3_rows'),('core5','core5_rows')]:
            a=g[g[col]>0]
            regions.append(dict(phase=phase,region=region,rule=rule,sites=a.site_id.nunique(),seasons=a.season.nunique(),rows=int(a[col].sum())))
    pd.DataFrame(regions).to_csv(ROOT/'connected_label_region_support.csv',index=False,lineterminator='\n')
    common=[]
    if passed:
        for rule,col in [('core3','core3_rows'),('core5','core5_rows')]:
            a=all_records[all_records[col]>0]
            sites=set(a[a.phase.eq('train')].site_id)&set(a[a.phase.eq('test')].site_id)
            for phase,g in a[a.site_id.isin(sites)].groupby('phase'):
                common.append(dict(rule=rule,phase=phase,sites=g.site_id.nunique(),regions=g.region.nunique(),seasons=g.season.nunique(),rows=int(g[col].sum())))
    pd.DataFrame(common).to_csv(ROOT/'connected_label_common_site_support.csv',index=False,lineterminator='\n')
    (ROOT/'connected_label_verdict.json').write_text(json.dumps(dict(training_core3_support_passed=passed,
      heldout_support_evaluated=passed,guano_purity_verified=False,original_source_gate_passed=False,
      classifier_fitted=False,new_isotope_estimated=False),indent=2)+'\n',encoding='utf-8',newline='\n')
    print(totals.to_string(index=False));print(pd.DataFrame(common).to_string(index=False))

if __name__=='__main__':main()
