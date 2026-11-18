#!/usr/bin/env node
// Source-locked exploratory forecast gate for the Signy two-species fish contrast.
// No forecast of future nests, occupancy, breeding-space N_eff, or species replacement.
// No external packages; requires Node.js >=18.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const sources = {
  signy: {
    path: resolve(here, "../data/signy_same_year_diet_phenology.csv"),
    git_blob: "8058fe612b005d6041f777cf7bcd65b2b73ae8ec",
  },
  future: {
    path: resolve(here, "../../outputs/diet_niche_scenarios_v1/conditional_scenarios.csv"),
    git_blob: "98049ae400c42f9c5bc394d284bf7d75c80aec5a",
  },
};

function loadPinned(s) {
  const buf = readFileSync(s.path);
  const got = createHash("sha1")
    .update("blob " + buf.byteLength + "\0")
    .update(buf).digest("hex");
  assert.equal(got, s.git_blob, "Changed source file (no silent replacement): " + s.path);
  return buf.toString("utf8");
}

function csv(text) {
  const records = [];
  let row = [], cell = "", quote = false;
  for (let i = 0; i < text.length; ++i) {
    const c = text[i];
    if (c === '"') {
      if (quote && text[i + 1] === '"') { cell += '"'; ++i; }
      else quote = !quote;
    } else if (c === "," && !quote) {
      row.push(cell); cell = "";
    } else if ((c === "\n" || c === "\r") && !quote) {
      if (c === "\r" && text[i + 1] === "\n") ++i;
      row.push(cell); cell = "";
      if (row.length > 1) records.push(row);
      row = [];
    } else cell += c;
  }
  if (cell !== "" || row.length) { row.push(cell); records.push(row); }
  assert.equal(quote, false, "Unterminated quoted CSV cell");
  assert.ok(records.length > 1, "Empty source");
  const head = records.shift();
  return records.map(r => {
    assert.equal(r.length, head.length, "CSV width mismatch");
    return Object.fromEntries(head.map((k, j) => [k, r[j]]));
  });
}
function num(v) {
  assert.ok(v !== "" && v != null, "Missing required number");
  const x = Number(v);
  assert.ok(Number.isFinite(x), "Non-finite required number: " + v);
  return x;
}
function mean(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length; }
function ols(xs, ys) {
  assert.ok(xs.length >= 3 && xs.length === ys.length);
  const xm = mean(xs), ym = mean(ys);
  const xx = xs.reduce((t, x) => t + (x - xm) ** 2, 0);
  assert.ok(xx > 0, "No predictor variation");
  const b = xs.reduce((t, x, i) => t + (x - xm) * (ys[i] - ym), 0) / xx;
  return { slope: b, intercept: ym - b * xm, predict: x => ym + b * (x - xm) };
}
function metrics(vals) {
  return { n: vals.length,
    mae: mean(vals.map(v => Math.abs(v))),
    rmse: Math.sqrt(mean(vals.map(v => v * v))) };
}
function csvOutput(rows) {
  const keys = Object.keys(rows[0]);
  const enc = v => {
    const s = (v === null || v === undefined) ? "" : String(v);
    return /[,"\n\r]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
  };
  return [keys.join(","), ...rows.map(r => keys.map(k => enc(r[k])).join(","))].join("\n") + "\n";
}
function near(a, b, tolerance = 1e-10) { assert.ok(Math.abs(a - b) < tolerance, a + " != " + b); }

const nine = csv(loadPinned(sources.signy)).map(r => ({
  year: num(r.year),
  sic: num(r.sic_aug_nov_pct),
  fish_gap: num(r.diet_gap_fish_fraction),
  stomachs: num(r.n_stomachs_adelie) + num(r.n_stomachs_gentoo),
})).sort((a, b) => a.year - b.year);
assert.equal(nine.length, 9);
assert.deepEqual(nine.map(r => r.year), [2001,2002,2003,2004,2005,2006,2007,2008,2009]);
assert.equal(nine.reduce((n,r) => n+r.stomachs,0), 422);
const climateYears = 9;
const minObservedSic = Math.min(...nine.map(r => r.sic));
const maxObservedSic = Math.max(...nine.map(r => r.sic));

const fitAll = ols(nine.map(r => r.sic), nine.map(r => r.fish_gap));
const slopeLeaveOneYear = nine.map((_, i) => {
  const tr = nine.filter((_, j) => i !== j);
  return ols(tr.map(r => r.sic), tr.map(r => r.fish_gap)).slope * 10;
});
// Fixed chronological scoring: fit on first >=5 seasons; test 2006--2009 only.
// Same year SIC is assumed known: diagnostic annual environmental nowcast,
// not a forecast of future climate or independent regional generalization.
const holdout = [];
for (let i=5; i<nine.length; ++i) {
  const tr=nine.slice(0,i), test=nine[i];
  const ice = ols(tr.map(r=>r.sic),tr.map(r=>r.fish_gap));
  const time = ols(tr.map(r=>r.year),tr.map(r=>r.fish_gap));
  holdout.push({
    year: test.year, observed_fish_gap: test.fish_gap,
    observed_prior_aug_nov_sic_pct: test.sic,
    past_mean: mean(tr.map(r=>r.fish_gap)),
    sea_ice: Math.max(-1,Math.min(1,ice.predict(test.sic))),
    year_linear: Math.max(-1,Math.min(1,time.predict(test.year))),
  });
}
const scores = Object.fromEntries(["past_mean","sea_ice","year_linear"].map(k=>[
  k,metrics(holdout.map(r=>r.observed_fish_gap-r[k]))
]));

// Signy loc020 future data used previously for three-species niche scenarios.
// Here the 9-year response is specifically the SIGNED Gentoo minus Adelie fish share;
// never reuse the old 772-stomach three-species response coefficient.
const rawScenarios=csv(loadPinned(sources.future));
assert.equal(rawScenarios.length, 12);
const future = rawScenarios.map(r => {
  assert.equal(r.location_id, "loc020", "Future grid is not Signy loc020");
  const sic=num(r.delta_adjusted_sic), reference=num(r.observed_reference_sic);
  const distance=num(r.model_cell_distance_km);
  const historicalBias=num(r.historical_model_bias_pp);
  const supported=(sic>=minObservedSic && sic<=maxObservedSic);
  const before=fitAll.predict(reference);
  const after=supported ? fitAll.predict(sic) : null;
  return {
    model:r.model,ssp:r.scenario,period:r.period,location:r.location_id,
    observed_reference_sic_pct:reference,
    historical_model_bias_pp:historicalBias,
    marine_cell_distance_km:distance,
    within_50km:distance<=50,
    future_sea_ice_delta_pp:num(r.model_delta_sic_pp),
    future_bias_adjusted_sic_pct:sic,
    within_nine_year_observed_ice_range:supported,
    fitted_reference_signed_fish_gap:before,
    CONDITIONAL_future_signed_fish_gap:after,
    CONDITIONAL_signed_fish_gap_change:supported ? after-before : null,
    future_breeding_nests_forecast:null,
    future_breeding_space_forecast:null,
  };
});
assert.deepEqual([...new Set(future.map(r=>r.model))].sort(),
  ["ACCESS-CM2","BCC-CSM2-MR","CESM2"]);
assert.equal(future.filter(r=>r.within_nine_year_observed_ice_range).length,11);
assert.equal(future.filter(r=>r.within_50km).length,8);
assert.equal(future.filter(r=>Math.abs(r.historical_model_bias_pp)>20).length,12);
near(fitAll.slope*10, 0.11798599511996022);
near(scores.past_mean.mae,0.32118433559611415);
near(scores.sea_ice.mae,0.18416626285802581);
near(scores.year_linear.mae,0.429288134969247);
near(fitAll.predict(48.68273700076806),0.4525190940241181);

const summary = {
  status: "EXPLORATORY_CONDITIONAL_DIET_SCENARIOS_NOT_VALIDATED_FUTURE_BREEDING",
  frozen_source_git_blobs: Object.fromEntries(Object.entries(sources).map(([k,v])=>[k,v.git_blob])),
  actual_climate_replicates:climateYears, original_stomachs_total:422,
  signy_years: "2001-2009", observed_sic_range_pct:[minObservedSic,maxObservedSic],
  response: "signed mean fish fraction GEPE minus ADPE, not three-species distance",
  slope_signed_gap_per_10_sic_pp:fitAll.slope*10,
  slope_leave_one_year_out_range:[Math.min(...slopeLeaveOneYear),Math.max(...slopeLeaveOneYear)],
  chronological_known_sic_nowcast_2006_2009:scores,
  sic_hindcast_mae_reduction_vs_past_mean:1-scores.sea_ice.mae/scores.past_mean.mae,
  conditional_future_scenarios:12,
  within_observed_sic_support:future.filter(r=>r.within_nine_year_observed_ice_range).length,
  marine_cell_within_50km:future.filter(r=>r.within_50km).length,
  historical_model_bias_pp_range:[Math.min(...future.map(r=>r.historical_model_bias_pp)),
    Math.max(...future.map(r=>r.historical_model_bias_pp))],
  future_diet_scenario_interpretation:
    "observed SIC plus CMIP6 model change, stationary Signy 9-year response; excludes out-of-support row; model historical coastal bias unresolved",
  future_breeding_count_or_colonization_forecast:null,
  prior_independent_Palmer_transfer:
    "Earlier same-species diet transfer was worse than past mean; see palmer_signy_diet_external_v1 report; not recomputed by this program",
  forecast_validation:
    "4 same-island test years only; not independent out-of-region, and no demonstrated model bias correction or ecological transport to 2050/2100",
};
const outIndex = process.argv.indexOf("--out");
if(outIndex!==-1) {
  assert.ok(process.argv[outIndex+1], "--out requires a directory");
  const folder=resolve(process.argv[outIndex+1]); mkdirSync(folder,{recursive:true});
  writeFileSync(resolve(folder,"forecast_summary.json"),JSON.stringify(summary,null,2)+"\n");
  writeFileSync(resolve(folder,"chronological_hindcast.csv"),csvOutput(holdout));
  writeFileSync(resolve(folder,"conditional_signy_two_species.csv"),csvOutput(future));
}
console.log(JSON.stringify(summary,null,2));
