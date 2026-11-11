"""Reproduce Tables from archived paired censuses and the matched 34-site ocean panel."""
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parent
counts = pd.read_csv(next(root.glob("observed_2species*.csv")))
ocean = pd.read_csv(next(root.glob("original_GLORYS*.csv"))).rename(columns={
    "source_SIC_pp": "ice", "source_glorys_thetao_C": "temperature"})
keys = ["site_id", "year", "source_region", "source_250km_block"]
data = counts.merge(ocean[keys + ["ice", "temperature"]], on=keys, validate="many_to_one")
assert len(data) == len(counts) == 39 and not data.duplicated(["species_pair", *keys]).any()
denom = data.nests_source_gentoo + data.nests_source_baseline_species
assert (denom > 0).all()
data["share"] = 100 * data.nests_source_gentoo / denom
rows, contrasts = [], []
for pair, panel in data.groupby("species_pair"):
    # Equal site weight; climatologies use a common calendar for every site.
    def sites(panel_subset, last_year):
        env = ocean[ocean.year <= last_year].groupby("site_id")[["ice", "temperature"]].mean()
        return panel_subset.groupby(["source_region", "site_id"]).share.mean().reset_index().join(env, on="site_id")

    regions = sites(panel, 2020).groupby("source_region")
    for region, group in regions:
        contrasts.append(dict(pair=pair, region=region, n_sites=len(group),
                              **group[["share", "ice", "temperature"]].mean().to_dict()))
    for site, series in panel.groupby("site_id"):
        sequence = list(series.sort_values("year").itertuples())
        for a, b in zip(sequence, sequence[1:]):
            for mode in ["all_years", "past_only"]:
                cutoff = 2020 if mode == "all_years" else a.year
                train = sites(panel[(panel.source_region != a.source_region) & (panel.year <= cutoff)], cutoff)
                for cols in [["temperature"], ["ice"], ["temperature", "ice"]]:
                    x = train[cols].to_numpy()
                    design = np.column_stack((np.ones(len(train)), x))
                    pred = np.nan
                    if len(train) > len(cols) + 1 and np.linalg.matrix_rank(design) == len(cols) + 1:
                        slopes = np.linalg.lstsq(design, train.share, rcond=None)[0][1:]
                        delta = [getattr(b, c) - getattr(a, c) for c in cols]
                        pred = np.clip(a.share + np.dot(slopes, delta), 0, 100) - a.share
                    rows.append(dict(pair=pair, region=a.source_region, site=site,
                        start=a.year, end=b.year, mode=mode, model="+".join(cols), train_sites=len(train),
                        delta_temp=b.temperature-a.temperature, delta_ice=b.ice-a.ice,
                        observed=b.share-a.share, predicted=pred))
p = pd.DataFrame(rows)
p.to_csv(root/"predictions.csv", index=False)
pd.DataFrame(contrasts).to_csv(root/"region_means.csv", index=False)
scores = []
for (pair, region, mode, model), group in p.groupby(["pair","region","mode","model"]):
    for subset, g in [("all", group), ("warming",group[group.delta_temp > 0])]:
        v = g.dropna(subset=["predicted"])
        scores.append(dict(pair=pair, region=region, mode=mode, model=model, subset=subset,
            possible=len(g), scored=len(v), sites=v.site.nunique(),
            mae=(v.predicted-v.observed).abs().mean(), persistence_mae=v.observed.abs().mean(),
            correct_direction=int(((v.observed*v.predicted)>0).sum()),
            nonzero_observed=int((v.observed!=0).sum())))
pd.DataFrame(scores).to_csv(root/"scores.csv", index=False)

# Literal space-for-time substitution: two regional means determine a secant,
# with no residual degrees of freedom. This diagnostic is in sample by region.
means = pd.DataFrame(contrasts)
regional_predictions = []
for pair, group in means.groupby("pair"):
    cold, warm = group.sort_values("temperature").itertuples(index=False)
    base = p[(p.pair == pair) & (p["mode"] == "all_years") & (p.model == "temperature")]
    for variable, delta in [("temperature","delta_temp"), ("ice","delta_ice")]:
        slope = (warm.share-cold.share)/(getattr(warm,variable)-getattr(cold,variable))
        for r in base.itertuples():
            start_share = data.loc[(data.species_pair == pair) & (data.site_id == r.site) &
                                   (data.year == r.start), "share"].item()
            change = np.clip(start_share+slope*getattr(r,delta),0,100)-start_share
            regional_predictions.append(dict(pair=pair, site=r.site, region=r.region, start=r.start,
                end=r.end, model=variable, warming=r.delta_temp>0, slope=slope,
                observed=r.observed, predicted=change))
q = pd.DataFrame(regional_predictions)
q.to_csv(root/"regional_substitution.csv",index=False)
for (pair, model), group in q.groupby(["pair","model"]):
    for g in [group,group[group.warming]]:
        print(pair,model,len(g),round((g.observed-g.predicted).abs().mean(),3),
              round(g.observed.abs().mean(),3),int((g.observed*g.predicted>0).sum()))
