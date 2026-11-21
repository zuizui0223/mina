"""Source-frozen exploratory sorting audit, not an ecological randomization experiment.

Input: original matched_rosters.csv (17 long-window Adélie sites); see
EXPLORATORY_REGIONAL_SORTING_NULL_FREEZE_20261121.md for the post-hoc contract.
Standard library only; reproducible xorshift32/Fisher-Yates randomization.
"""
import argparse
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
VARIABLES = ("sic_pp", "salinity", "sst_C")
DRAWS = 49999
SEED = 20261121


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def xorshift32(seed):
    while True:
        seed ^= (seed << 13) & 0xffffffff
        seed ^= seed >> 17
        seed ^= (seed << 5) & 0xffffffff
        seed &= 0xffffffff
        yield seed


def percentile(sorted_values, p):
    t = (len(sorted_values) - 1) * p
    lo, hi = math.floor(t), math.ceil(t)
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] * (hi - t) + sorted_values[hi] * (t - lo)


def compute():
    raw = read_csv(HERE / "matched_rosters.csv")
    rows = [r for r in raw if r["comparison"] == "long" and r["radius"] == "0"]
    assert len(rows) == 17
    assert len({r["site_id"] for r in rows}) == 17
    numeric = ("n0", "n1", "latitude") + tuple(v + str(i) for v in VARIABLES for i in (0, 1))
    for r in rows:
        for field in numeric:
            r[field] = float(r[field])
        assert r["n0"] >= 0 and r["n1"] >= 0
        if r["n0"] == 0:
            assert r["n1"] == 0, "Growth factor undefined for newly occupied sites; freeze excludes these"
    groups = {}
    for r in rows:
        groups.setdefault(r["source_region"], []).append(r)
    assert len(groups) == 4 and sorted(map(len, groups.values())) == [1, 3, 3, 10]
    N0 = sum(r["n0"] for r in rows)
    N1 = sum(r["n1"] for r in rows)
    region_details = [
        dict(name=reg, n=len(g), n0=sum(r["n0"] for r in g), n1=sum(r["n1"] for r in g))
        for reg, g in groups.items()
    ]

    def decompose(variable, changed=None):
        midpoint = lambda r: (r[variable + "0"] + r[variable + "1"]) / 2
        full = 0.0
        between = 0.0
        within = 0.0
        for region, members in groups.items():
            n0 = sum(r["n0"] for r in members)
            n1 = sum(changed[r["site_id"]] if changed is not None else r["n1"] for r in members)
            assert n0 > 0 and n1 > 0
            be = 0.0
            wi = 0.0
            for r in members:
                v0 = r["n0"] / n0
                v1 = (changed[r["site_id"]] if changed is not None else r["n1"]) / n1
                be += 0.5 * (v0 + v1) * midpoint(r)
                wi += (v1 - v0) * midpoint(r)
            between += (n1 / N1 - n0 / N0) * be
            within += 0.5 * (n1 / N1 + n0 / N0) * wi
        for r in rows:
            n1 = changed[r["site_id"]] if changed is not None else r["n1"]
            full += (n1 / N1 - r["n0"] / N0) * midpoint(r)
        assert math.isclose(full, between + within, abs_tol=1e-10)
        return dict(total=full, between=between, within=within)

    observed = {v: decompose(v) for v in VARIABLES}
    previous = read_csv(HERE / "decomposition.csv")
    for variable, row in observed.items():
        match = [x for x in previous if x["comparison"] == "long"
                 and x["radius"] == "0" and x["variable"] == variable]
        assert len(match) == 1
        assert math.isclose(row["total"], float(match[0]["redistribution"]), abs_tol=1e-10)
    draws = {v: {k: [] for k in ("within", "between", "total")} for v in VARIABLES}
    rng = xorshift32(SEED)
    for _ in range(DRAWS):
        shuffled_n1 = {}
        for region, members in groups.items():
            active = [r for r in members if r["n0"] > 0]
            g = [r["n1"] / r["n0"] for r in active]
            for j in range(len(g)-1, 0, -1):
                idx = next(rng) % (j+1)
                g[j], g[idx] = g[idx], g[j]
            proposed = [r["n0"] * v for r, v in zip(active, g)]
            total_late = sum(r["n1"] for r in members)
            factor = total_late / sum(proposed)
            for r, x in zip(active, proposed):
                shuffled_n1[r["site_id"]] = x * factor
            for r in members:
                if r["n0"] == 0:
                    shuffled_n1[r["site_id"]] = 0.0
            assert math.isclose(sum(shuffled_n1[r["site_id"]] for r in members),
                                total_late, rel_tol=1e-12)
        for v in VARIABLES:
            d = decompose(v, shuffled_n1)
            for k in draws[v]:
                draws[v][k].append(d[k])

    result = dict(
        n=17, region_counts=region_details, seed=SEED, draws=DRAWS, results={}
    )
    for v in VARIABLES:
        a = draws[v]
        for k in a:
            a[k].sort()
        obs = observed[v]
        median = percentile(a["within"], .5)
        result["results"][v] = dict(
            observed=obs,
            between_share_of_observed_R=obs["between"]/obs["total"],
            null={k: dict(q025=percentile(a[k], .025),
                          median=percentile(a[k], .5),
                          q975=percentile(a[k], .975)) for k in a},
            within_right_tail=(1 + sum(x >= obs["within"] - 1e-12 for x in a["within"])) / (DRAWS+1),
            within_two_sided_centered=(1 + sum(abs(x-median) >= abs(obs["within"]-median) - 1e-12
                                               for x in a["within"])) / (DRAWS+1),
        )
    return result


def compare(a, b, address="root"):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), address
        for k in a:
            compare(a[k], b[k], address + "." + k)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), address
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, address + "." + str(i))
    elif isinstance(a, (int, float)) and not isinstance(a, bool):
        assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-10), (address, a, b)
    else:
        assert a == b, (address, a, b)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="Compare with committed independently computed JSON")
    args = p.parse_args()
    actual = compute()
    if args.check:
        with (HERE / "REGIONAL_SORTING_NULL_RESULT_20261121.json").open(encoding="utf-8") as f:
            expected = json.load(f)
        compare(actual, expected)
        print("PASS independently reproduce 17-site exact decomposition, all 49,999 xorshift null draws and frozen result")
    else:
        print(json.dumps(actual, indent=2, ensure_ascii=False))
