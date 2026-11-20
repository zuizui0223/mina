"""Join published center-labeled pixels and final scene table; no ecological Y."""
import io
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).parent
EVIDENCE=ROOT/'public_grid_evidence'

def main():
    d=pd.read_csv(ROOT/'source_positive_records.csv')
    text=(EVIDENCE/'schwaller2013_pangaea804588.txt').read_text(encoding='utf-8')
    p=pd.read_csv(io.StringIO(text.split('*/',1)[1].lstrip()),sep='\t')
    p['acquisition_date']=pd.to_datetime(p['File name (of source file)'].str.slice(9,16),format='%Y%j').dt.strftime('%Y%m%d')
    p['pathrow']=p['File name (of source file)'].str.slice(3,9)
    p=p.rename(columns={'UTM east [m]':'easting','UTM north [m]':'northing'})
    p[['easting','northing']]=p[['easting','northing']].astype(float)
    d['acquisition_date']=d['Landsat.Product.Identifier.L1'].str.split('_').str[3]
    d['pathrow']=d['Landsat.Product.Identifier.L1'].str.split('_').str[2]
    keys=['pathrow','acquisition_date','easting','northing']
    if p.duplicated(keys).any():raise ValueError('Published pixel join is not unique')
    match=d.merge(p,on=keys,how='inner',validate='many_to_one')
    final=pd.read_csv(EVIDENCE/'youngflesh2026_tableS2.csv')
    pairs=final[['Site ID','Landsat Product Identifier']].drop_duplicates().rename(columns={'Site ID':'site_id','Landsat Product Identifier':'Landsat.Product.Identifier.L1'})
    d=d.merge(pairs.assign(in_final_scene_table=True),how='left',on=['site_id','Landsat.Product.Identifier.L1'],validate='many_to_one')
    d['in_final_scene_table']=d.in_final_scene_table.eq(True)
    match=match.merge(d[['site_id','Landsat.Product.Identifier.L1','cell','in_final_scene_table']],on=['site_id','Landsat.Product.Identifier.L1','cell'],validate='one_to_one')
    match.to_csv(ROOT/'published_pixel_exact_matches.csv',index=False,lineterminator='\n')
    match.groupby(['site_id','region','phase']).agg(rows=('cell','size'),seasons=('season','nunique'),scenes=('Landsat.Product.Identifier.L1','nunique')).reset_index().to_csv(ROOT/'published_pixel_match_support.csv',index=False,lineterminator='\n')
    support=[]
    for scope,g in [('exact_published_pixels',match),('same_sites_all_rows_assumption_only',d[d.site_id.isin(match.site_id)])]:
        for phase,h in g.groupby('phase'):
            support.append(dict(scope=scope,phase=phase,sites=h.site_id.nunique(),regions=h.region.nunique(),seasons=h.season.nunique(),rows=len(h)))
    pd.DataFrame(support).to_csv(ROOT/'published_pixel_support_scopes.csv',index=False,lineterminator='\n')
    outside=d[~d.in_final_scene_table]
    outside.groupby(['site_id','phase','season','Landsat.Product.Identifier.L1']).size().reset_index(name='rows').to_csv(ROOT/'source_rows_outside_final_scene_table.csv',index=False,lineterminator='\n')
    (ROOT/'published_source_crosscheck_summary.json').write_text(json.dumps(dict(
      published_pixels=len(p),exact_matches=len(match),matching_sites=match.site_id.nunique(),
      matching_regions=match.region.nunique(),matching_seasons=match.season.nunique(),
      matches_not_in_final_scene_table=int((~match.in_final_scene_table).sum()),
      source_rows_not_in_final_scene_table=len(outside),
      contemporary_independent_guano_labels=False),indent=2)+'\n',encoding='utf-8',newline='\n')
    print(pd.DataFrame(support).to_string(index=False));print('Source rows outside final S2:',len(outside))

if __name__=='__main__':main()
