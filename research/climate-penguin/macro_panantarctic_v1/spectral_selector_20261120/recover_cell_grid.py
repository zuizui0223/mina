"""Recover row-major coordinate lattices from TRAINING cell IDs, not spectra.

This validates the coordinate lattice, not center/corner semantics, resampling,
guano purity, or a mapping to the native Landsat pixels. No ecological response.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).parent
TOL=1e-5

def recover(g):
    g=g[['cell','easting','northing']].drop_duplicates().sort_values('cell')
    if g.cell.duplicated().any():return [],'CELL_HAS_MULTIPLE_COORDINATES'
    c=g.cell.to_numpy(dtype=int)-1
    x=g.easting.to_numpy();y=g.northing.to_numpy()
    if len(g)<3:return [],'INSUFFICIENT_POINTS'
    fits=[]
    # Finite, reported search domain. Lack of a fit is not proof no lattice exists.
    for n in range(2,min(4096,int(g.cell.max()))+1):
        col=c%n;row=c//n
        vc=np.var(col);vr=np.var(row)
        if vc==0 or vr==0:continue
        sx=np.mean((col-col.mean())*(x-x.mean()))/vc
        sy=np.mean((row-row.mean())*(y-y.mean()))/vr
        if not(29<sx<31 and -31<sy<-29):continue
        ox=np.mean(x-sx*col);oy=np.mean(y-sy*row)
        error=float(max(abs(x-ox-sx*col).max(),abs(y-oy-sy*row).max()))
        if error<TOL:
            fits.append(dict(ncols=n,dx_m=float(sx),dy_m=float(sy),
              first_index_easting=float(ox),first_index_northing=float(oy),
              max_training_axis_error_m=error))
    return fits,'UNIQUE_LATTICE' if len(fits)==1 else 'AMBIGUOUS_OR_UNRECOVERED'

def main():
    d=pd.read_csv(ROOT/'source_positive_records.csv')
    output=[];checks=[]
    for site,g in d[d.phase.eq('train')].groupby('site_id'):
        fits,status=recover(g)
        record=dict(site_id=site,region=g.region.iloc[0],status=status,n_fits=len(fits),
          training_rows=len(g),training_coordinates=len(g[['cell','easting','northing']].drop_duplicates()))
        if len(fits)==1:
            record.update(fits[0]);f=fits[0]
            test=d[d.phase.eq('test')&d.site_id.eq(site)]
            c=test.cell.to_numpy(dtype=int)-1
            error=np.maximum(abs(test.easting.to_numpy()-f['first_index_easting']-f['dx_m']*(c%f['ncols'])),
                             abs(test.northing.to_numpy()-f['first_index_northing']-f['dy_m']*(c//f['ncols'])))
            checks.append(dict(site_id=site,region=g.region.iloc[0],test_rows=len(test),
              test_seasons=test.season.nunique(),matching_rows=int((error<TOL).sum()),
              max_test_axis_error_m=float(error.max()) if len(error) else None))
        output.append(record)
    pd.DataFrame(output).to_csv(ROOT/'training_recovered_lattices.csv',index=False,lineterminator='\n')
    pd.DataFrame(checks).to_csv(ROOT/'heldout_coordinate_checks.csv',index=False,lineterminator='\n')
    excluded=d[d.phase.eq('test')&~d.site_id.isin([r['site_id'] for r in output if r['status']=='UNIQUE_LATTICE'])]
    excluded.groupby(['site_id','region']).agg(rows=('cell','size'),seasons=('season','nunique')).reset_index().to_csv(ROOT/'test_without_training_lattice.csv',index=False,lineterminator='\n')
    summary=dict(training_sites=len(output),unique_training_lattices=sum(r['status']=='UNIQUE_LATTICE' for r in output),
      test_rows_with_unique_training_lattice=sum(r['test_rows'] for r in checks),
      test_rows_coordinate_match=sum(r['matching_rows'] for r in checks),
      test_rows_without_unique_training_lattice=len(excluded),
      diagnostic_search_ncols=[2,4096],diagnostic_cell_spacing_open_interval_m=[29,31],
      tolerance_axis_m=TOL,grid_fit_uses_spectra=False,test_used_to_fit=False,
      original_footprint_semantics_verified=False,classifier_fitted=False)
    (ROOT/'lattice_recovery_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
