"""Copy reviewed progress artifacts into a separate mina checkout; never push."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--checkout',required=True);args=ap.parse_args()
checkout=Path(args.checkout).resolve();assert (checkout/'.git').exists()
dest=checkout/'research/climate-penguin'
files=[p for p in (ROOT/'outputs').rglob('*') if p.is_file() and p.suffix in {'.md','.csv','.json','.gz'} and p.name!='GITHUB_SYNC_STATUS.json']
files += [p for p in (ROOT/'work').rglob('*') if p.is_file() and p.suffix == '.py' and checkout not in p.parents and '.git' not in p.parts and '__pycache__' not in p.parts]
manifest=[]
for src in sorted(set(files)):
    rel=src.relative_to(ROOT);target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,target)
    data=target.read_bytes();assert data==src.read_bytes()
    manifest.append(dict(path=rel.as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(dest/'SNAPSHOT_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(files=len(manifest),bytes=sum(x['bytes'] for x in manifest),destination=str(dest)),indent=2))
