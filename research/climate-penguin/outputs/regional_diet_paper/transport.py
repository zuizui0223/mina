"""Apply the Signy slope after calibrating the Palmer mean on the other five seasons."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parent
root = out.parent if (out.parent / "palmer_signy_diet_external_v1").exists() else Path("work/mina-sync/research/climate-penguin/outputs")
d = pd.read_csv(root / "palmer_signy_diet_external_v1/annual_pair_comparison.csv")
d["gap_pp"] = 100 * d.distance
s = d.query("region == 'Signy'")
p = d.query("region == 'Palmer'").copy()
slope, intercept = np.polyfit(s.sic_aug_nov, s.gap_pp, 1)
rows = []
for idx, test in p.iterrows():
    train = p.drop(idx)
    mean = train.gap_pp.mean()
    rows.append(dict(year=int(test.year),sic=test.sic_aug_nov,observed=test.gap_pp,
                     signy_raw=intercept+slope*test.sic_aug_nov,local_mean=mean,
                     local_mean_plus_signy_slope=mean+slope*(test.sic_aug_nov-train.sic_aug_nov.mean())))
pred = pd.DataFrame(rows)
pred["bounded_sensitivity"] = pred.local_mean_plus_signy_slope.clip(0,100)
pred.to_csv(out / "palmer_transfer.csv",index=False)
scores = []
for subset, points in [("all",pred),("inside Signy SIC range",pred[pred.sic.between(s.sic_aug_nov.min(),s.sic_aug_nov.max())])]:
    for model in ["signy_raw","local_mean","local_mean_plus_signy_slope","bounded_sensitivity"]:
        err = points[model]-points.observed
        scores.append(dict(subset=subset,model=model,n=len(err),MAE=abs(err).mean(),RMSE=np.sqrt(np.mean(err**2)),outside_physical=int((~points[model].between(0,100)).sum())))
pd.DataFrame(scores).to_csv(out / "scores.csv",index=False)
fig, axes = plt.subplots(1,2,figsize=(10.8,4.8),layout="constrained")
for region, g in d.groupby("region"):
    color = {"Signy":"#176686","Palmer":"#B75221"}[region]
    axes[0].scatter(g.sic_aug_nov,g.gap_pp,color=color,label=region)
    x = np.array([g.sic_aug_nov.min(),g.sic_aug_nov.max()])
    axes[0].plot(x,np.polyval(np.polyfit(g.sic_aug_nov,g.gap_pp,1),x),color=color)
axes[0].set(xlabel="August–November sea-ice concentration (%)",ylabel="Gentoo–Adélie fish-share gap (percentage points)", title="A   Observed breeding seasons")
axes[0].legend(frameon=False)
for col,label,style,color in [("observed","Observed","o","#B75221"),("local_mean","Local mean (other five seasons)","+","#303030"),("local_mean_plus_signy_slope","Local mean + Signy slope","s","#176686")]:
    axes[1].plot(pred.year,pred[col],marker=style,linestyle="none",color=color,label=label,fillstyle="none" if col.endswith("slope") else "full",markersize=7)
axes[1].axhline(0,color="0.7",linewidth=.8)
axes[1].set(xlabel="Start year of Palmer breeding season",ylabel="Observed or predicted gap (percentage points)",title="B   Transport after local calibration",xticks=pred.year)
axes[1].legend(frameon=False,fontsize=8)
fig.savefig(out / "regional_transfer.png",dpi=190)
print(pd.DataFrame(scores).round(2).to_string(index=False));print(pred.round(2).to_string(index=False))
