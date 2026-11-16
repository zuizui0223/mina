#!/usr/bin/env python3
"""Physical-only Antarctic sea-ice exposure: absolute SIC, source nesting weights and geography.

Original data:
 Actions 43845907301 -> source_root/outputs/cmip6_projection_v1/site_model_changes.csv
 Actions 43872754084 -> source_site_nest_proxy.csv
 Actions 42610664607 -> source_observed_2456.csv; panantarctic_595_site_inventory.csv
No biological climate-dose coefficient is used.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SCENARIOS = [("ssp245", "2041-2060"), ("ssp245", "2081-2100"),
             ("ssp585", "2041-2060"), ("ssp585", "2081-2100")]


def main(a):
    counts = pd.read_csv(a.weights)
    inventory = pd.read_csv(a.inventory)
    history = pd.read_csv(a.observed)
    climate = pd.read_csv(a.model_changes)
    assert len(counts) == 271 and counts.site_id.is_unique
    assert len(climate) == 21420 and climate.site_id.nunique() == 595
    assert counts.n.ge(0).all() and np.isclose(counts.n.sum(), 2848329.5)
    assert set(climate.source_id.unique()) == {"ACCESS-CM2", "BCC-CSM2-MR", "CESM2"}
    assert climate.complete_years.eq(20).all()
    w = counts.merge(inventory[["site_id", "polar_100km_fixed_grid_block"]],
                     on="site_id", validate="one_to_one")
    xy = w.polar_250km_fixed_grid_block.str.split(":", expand=True).astype(int)
    w["nested_500km_block"] = (xy[0] // 2).astype(str) + ":" + (xy[1] // 2).astype(str)
    sp = (history.loc[history.season.between(2011, 2020)]
          .groupby(["site_id", "species"], as_index=False).observed_nest_count.median())
    assert len(sp) == 331
    assert np.allclose(sp.groupby("site_id").observed_nest_count.sum()
                       .reindex(w.site_id).to_numpy(), w.n.to_numpy())

    sic = climate.loc[climate.variable_id.eq("siconc")]
    # One 20-year model-mean for each source site, model and scenario.
    site = (sic.groupby(["experiment_id", "period", "site_id"], as_index=False)
            .agg(baseline=("baseline_1995_2014", "mean"),
                 future=("seasonal_mean", "mean"), delta=("change", "mean")))
    assert np.allclose(site.baseline + site.delta, site.future, atol=1e-9)
    results, species, diagnostics, regional = [], [], [], []
    # Match the separately source-tested 5000-permutation region-conditional diagnostic.
    prng=np.random.default_rng(a.seed)
    prng.integers(0,27,size=(4000,27))  # fixed original 250km block bootstrap RNG stream
    base_weights=w.n.to_numpy(float)
    shuffled_weights=np.tile(base_weights,(5000,1))
    for _,grp in w.groupby("source_region",sort=True):
        idx=grp.index.to_numpy()
        order=np.argsort(prng.random((5000,len(idx))),axis=1)
        shuffled_weights[:,idx]=base_weights[idx][order]
    for experiment, period in SCENARIOS:
        frame = w.merge(site.loc[site.experiment_id.eq(experiment)
                                 & site.period.eq(period), ["site_id", "baseline", "future", "delta"]],
                        on="site_id", validate="one_to_one")
        assert len(frame) == 271
        n = frame.n.to_numpy(float)
        delta = frame.delta.to_numpy(float)
        nest_mean = float(np.average(delta, weights=n))
        equal_mean = float(delta.mean())
        between, within = 0., 0.
        for _, g in frame.groupby("source_region"):
            count_share = g.n.sum() / n.sum()
            site_share = len(g) / len(frame)
            equal_r = float(g.delta.mean())
            weighted_r = float(np.average(g.delta, weights=g.n))
            between += (count_share - site_share) * equal_r
            within += count_share * (weighted_r - equal_r)
            regional.append(dict(experiment=experiment, period=period,
                                 source_region=g.source_region.iloc[0], sites=len(g),
                                 source_nest_share=count_share, baseline_sic_nest_pct=np.average(g.baseline,weights=g.n),
                                 future_sic_nest_pct=np.average(g.future,weights=g.n),
                                 delta_sic_nest_pp=weighted_r))
        gap = nest_mean - equal_mean
        shuffle_center = sum(g.n.sum()/n.sum()*g.delta.mean()
                             for _,g in frame.groupby("source_region"))
        shuffled_within=(shuffled_weights@delta)/n.sum()-shuffle_center
        perm_p=(1+np.sum(np.abs(shuffled_within)>=abs(within)))/5001
        assert abs(between + within - gap) < 1e-8

        res = dict(experiment=experiment, period=period, sites=len(frame),
                   source_proxy_nests=n.sum(),
                   effective_nest_sites=n.sum() ** 2 / (n*n).sum(),
                   baseline_sic_equal_pct=frame.baseline.mean(),
                   baseline_sic_nest_pct=np.average(frame.baseline, weights=n),
                   future_sic_equal_pct=frame.future.mean(),
                   future_sic_nest_pct=np.average(frame.future, weights=n),
                   delta_sic_equal_pp=equal_mean, delta_sic_nest_pp=nest_mean,
                   gap_pp=gap, between_region_pp=between, within_region_pp=within,
                   region_conditional_permutation_p_diagnostic=perm_p)
        for threshold in (15, 50):
            flag = frame.future <= threshold
            res["future_le%d_site_share" % threshold] = flag.mean()
            res["future_le%d_nest_share" % threshold] = frame.loc[flag,"n"].sum()/n.sum()
        results.append(res)
        joined = sp.merge(frame[["site_id","baseline","future","delta"]], on="site_id",validate="many_to_one")
        for name, g in joined.groupby("species"):
            v = g.observed_nest_count.to_numpy(float)
            species.append(dict(experiment=experiment,period=period,species=name,
                                sites=len(g),source_nest_proxy=v.sum(),
                                baseline_sic_nest_pct=np.average(g.baseline,weights=v),
                                future_sic_nest_pct=np.average(g.future,weights=v),
                                delta_sic_nest_pp=np.average(g.delta,weights=v)))
        for scale in ("polar_100km_fixed_grid_block", "polar_250km_fixed_grid_block",
                      "nested_500km_block", "source_region"):
            ids, unique = pd.factorize(frame[scale], sort=True)
            groups=len(unique)
            rng=np.random.default_rng(a.seed)
            draws=rng.integers(0,groups,size=(a.resamples,groups))
            duplicate=np.empty((a.resamples,groups),dtype=np.int16)
            for k in range(groups):
                duplicate[:,k]=(draws==k).sum(axis=1)
            weight=duplicate[:,ids]
            resampled=(weight@(n*delta))/(weight@n) - (weight@delta)/weight.sum(axis=1)
            diagnostics.append(dict(experiment=experiment,period=period,
                                    cluster_scale=scale,clusters=groups,
                                    resamples=a.resamples,seed=a.seed,
                                    q025_pp=np.quantile(resampled,.025),
                                    median_pp=np.median(resampled),
                                    q975_pp=np.quantile(resampled,.975),
                                    fraction_positive=(resampled>0).mean()))
    # Nested site/region sampling is a sensitivity diagnostic, NOT a CI for biology.
    output=Path(a.out)
    output.mkdir(exist_ok=True, parents=True)
    pd.DataFrame(results).to_csv(output/"absolute_sic_source_weighting.csv",index=False)
    pd.DataFrame(species).to_csv(output/"absolute_sic_species.csv",index=False)
    pd.DataFrame(diagnostics).to_csv(output/"absolute_sic_multiscale_resampling.csv",index=False)
    pd.DataFrame(regional).to_csv(output/"absolute_sic_region.csv",index=False)
    print(pd.DataFrame(results).round(3).to_string(index=False))
    print(pd.DataFrame(diagnostics).query("experiment == 'ssp585' and period == '2081-2100'").round(3).to_string(index=False))


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("weights", "inventory", "observed", "model-changes", "out"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--resamples",type=int,default=10000)
    p.add_argument("--seed",type=int,default=20261116)
    main(p.parse_args())
