"""Check historical source identity and recover the previously frozen 88 sites."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import pandas as pd

def main(rds, geography, out):
    expected_rds='f86ba97f98bca33c1ff57a1ca1b6783f92c29d952710ce7a4256f0109323b50b'
    expected_zip='702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96'
    rh=hashlib.sha256(rds.read_bytes()).hexdigest()
    raw=geography.read_bytes();zh=hashlib.sha256(raw).hexdigest()
    if (rh,zh)!=(expected_rds,expected_zip):raise ValueError('Frozen source identity changed')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=[n for n in z.namelist() if n.endswith('source_original_88_site_polynya_25km_100km_native_grid_geography.csv')]
        if len(names)!=1:raise ValueError('Geography member missing/ambiguous')
        sites=pd.read_csv(z.open(names[0]));sites=sites[sites.radius_km.eq(100)]
    if len(sites)!=88 or sites.site_id.nunique()!=88:raise ValueError('Frozen site set changed')
    out.mkdir(exist_ok=True,parents=True)
    sites.to_csv(out/'source_sites.csv',index=False,lineterminator='\n')
    (out/'source_identity.json').write_text(json.dumps(dict(rds_sha256=rh,geography_zip_sha256=zh,
      geography_member=names[0],frozen_protocol_commit='75ee5c2eea07635bdc5595ae852348c75303d284',
      raw_source='https://doi.org/10.5281/zenodo.17409948',geography_artifact_id=14539723210),indent=2)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rds',type=Path,required=True)
    p.add_argument('--geography',type=Path,required=True);p.add_argument('--out',type=Path,default=Path(__file__).parent)
    a=p.parse_args();main(a.rds,a.geography,a.out)
