from pathlib import Path
import json,zipfile,hashlib
from acquire import R
from optical import sites,F
def pack():
    active=list(F.glob("*_series.json")) + list(F.glob("*_mask.npy"))
    items=[j for p in active if p.suffix==".json" for j in json.loads(p.read_text())]
    files=sorted(set(active+[F/f"{j['site']}_{j['id']}.npz" for j in items]+list((R/"raw").glob("*.gz"))))
    assert len(list((R/"raw").glob("*.gz")))==381
    with zipfile.ZipFile(R/"satellite_inputs.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for f in files:z.write(f,f.relative_to(R))
    rows=[(f.relative_to(R).as_posix(),hashlib.sha256(f.read_bytes()).hexdigest()) for f in files]
    import pandas as pd
    pd.DataFrame(rows,columns=["path","sha256"]).to_csv(R/"satellite_manifest.csv",index=False,lineterminator="\n")
if __name__=="__main__":pack()
