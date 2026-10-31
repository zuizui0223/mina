// Original MAPPPD count ratios vs observed satellite sea ice: source-checked temporal diagnostic.
// Run: node research/climate-penguin/work/species_ratio_annual_ice_v1/build.mjs --check-receipt
// Inputs and the expected receipt are frozen on the climate-penguin research branch.
// These are exploratory observational associations, not projected future penguin abundances.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve, join } from "node:path";

const outputBase = resolve("research/climate-penguin/outputs");
const outdir = join(outputBase, "species_ratio_annual_ice_v1");
const pathMap = {
  bio: "comparison_audit/mapppd_unambiguous_site_seasons.csv",
  ice: "climate_penguin/macro_monthly_seaice_1991_2020.csv",
  paired: "warming_species_breeding_v1/matched_species_breeding_change.csv",
  future: "warming_species_breeding_v1/future_climate_coobserved_sites.csv",
};
const expectedBlobs = {
  bio: "fc134e364cf38699fa7611d7dee5fbbbcb370c0a",
  ice: "4fcea71c2d8b1069b6ad143f6522061ed434daf5",
  paired: "f17b4a21e9e5a045a40f5a4af9019e3bbc011758",
  future: "97ae24e98a0cb5f6b36e275d036cb4b71c953312",
};

function parseCSV(src) {
  const lines = []; let row = [], value = "", quoted = false;
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (quoted) {
      if (c === '"' && src[i + 1] === '"') { value += '"'; i++; }
      else if (c === '"') quoted = false;
      else value += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(value); value = ""; }
    else if (c === "\n") {
      row.push(value.replace(/\r$/, ""));
      if (row.length > 1) lines.push(row);
      row = []; value = "";
    } else value += c;
  }
  if (row.length || value) { row.push(value); lines.push(row); }
  if (quoted || !lines.length) throw Error("Invalid CSV");
  const header = lines.shift();
  return lines.map((parts, i) => {
    if (parts.length !== header.length) throw Error("CSV width " + i);
    return Object.fromEntries(header.map((x, j) => [x, parts[j]]));
  });
}
function csv(rows) {
  if (!rows.length) throw Error("Empty result");
  const cols = Object.keys(rows[0]);
  const escape = v => {
    const s = v == null ? "" : String(v);
    return /[",\r\n]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
  };
  return cols.join(",") + "\n" +
    rows.map(r => cols.map(c => escape(r[c])).join(",")).join("\n") + "\n";
}
function mean(a) { if (!a.length) throw Error("Empty mean"); return a.reduce((s, x) => s + x, 0) / a.length; }
function pearson(a, b) {
  if (a.length !== b.length || a.length < 3) return null;
  const x = mean(a), y = mean(b);
  const cov = a.reduce((s, v, i) => s + (v - x) * (b[i] - y), 0);
  const den = Math.sqrt(a.reduce((s, v) => s + (v - x) ** 2, 0) *
    b.reduce((s, v) => s + (v - y) ** 2, 0));
  return den > 0 ? cov / den : null;
}
function slope(x, y) {
  const mx = mean(x), my = mean(y);
  const den = x.reduce((s, v) => s + (v - mx) ** 2, 0);
  if (!den) throw Error("Unidentified slope");
  return x.reduce((s, v, i) => s + (v - mx) * (y[i] - my), 0) / den;
}
function within(rows, field, dimensions) {
  const values = rows.map(r => r[field]);
  for (let iter = 0; iter < 300; iter++) {
    let max = 0;
    for (const dimension of dimensions) {
      const sums = new Map();
      for (let i = 0; i < rows.length; i++) {
        const key = rows[i][dimension], z = sums.get(key) || { sum: 0, n: 0 };
        z.sum += values[i]; z.n++; sums.set(key, z);
      }
      for (let i = 0; i < rows.length; i++) {
        const v = sums.get(rows[i][dimension]), shift = v.sum / v.n;
        values[i] -= shift;
        max = Math.max(max, Math.abs(shift));
      }
    }
    if (max < 1e-12) break;
  }
  return values;
}
function adjusted(rows, x, y, dimensions) {
  const a = within(rows, x, dimensions), b = within(rows, y, dimensions);
  const den = a.reduce((s, v) => s + v * v, 0);
  return {
    n: rows.length,
    unique_site_years: new Set(rows.map(r => r.site + "|" + r.year)).size,
    partial_r: pearson(a, b),
    slope_per_10pp: den ? 10 * a.reduce((s, v, i) => s + v * b[i], 0) / den : null,
    residual_ice_sd: Math.sqrt(mean(a.map(v => v * v))),
  };
}
function error(rows, predictor) {
  const differences = rows.map(r => r[predictor] - r.delta_ratio);
  return {
    mae: mean(differences.map(Math.abs)),
    rmse: Math.sqrt(mean(differences.map(v => v * v))),
  };
}
function assertClose(a, b, label, tol = 1e-9) {
  if (!Number.isFinite(a) || Math.abs(a - b) > tol) throw Error("Receipt mismatch " + label + ": " + a + " vs " + b);
}
const receipt = JSON.parse(readFileSync(join(outdir, "expected_receipt.json"), "utf8"));
const inputs = {};
for (const [name, path] of Object.entries(pathMap)) {
  const bytes = readFileSync(join(outputBase, path));
  const blob = createHash("sha1").update(Buffer.from("blob " + bytes.length + "\0")).update(bytes).digest("hex");
  if (blob !== expectedBlobs[name] || blob !== receipt.blobs[name]) throw Error("Input source drift: " + name + " " + blob);
  inputs[name] = parseCSV(bytes.toString("utf8"));
}
const { bio: B, ice: I, paired: P, future: F } = inputs;
if (B.length !== 2999 || I.length !== 9600 || P.length !== 13 || F.length !== 32) throw Error("Source cohort drift");
const sites = new Set(P.map(p => p.site_id));
if (sites.size !== 8 || new Set(P.map(p => p.site_id + "|" + p.compared_species)).size !== 13) throw Error("Paired site gate");
const bmap = new Map(B.filter(r => sites.has(r.site_id)).map(r =>
  [[r.site_id, r.species_id, r.season, r.method].join("|"), r]));
const imap = new Map(I.filter(r => sites.has(r.site_id) && r.inner_km === "0" && r.complete_month === "True").map(r =>
  [[r.site_id, r.year, r.month].join("|"), +r.sic_mean]));
const yearly = [], groupTrends = [], intervals = [];
for (const p of P) {
  if (p.gate !== "1" || p.method_reference !== p.method_compared || p.reference_species !== "ADPE")
    throw Error("Unmatched source definition");
  const group = p.site_id + "|" + p.compared_species;
  const one = [];
  for (const year of p.common_years.split(";").map(Number)) {
    const ad = bmap.get([p.site_id, "ADPE", year, p.method_reference].join("|"));
    const other = bmap.get([p.site_id, p.compared_species, year, p.method_compared].join("|"));
    if (!ad || !other || +ad.count < 0 || +other.count < 0) throw Error("Missing/negative paired count: " + group);
    const months = [8, 9, 10, 11].map(m => imap.get([p.site_id, year, m].join("|")));
    if (months.some(v => !Number.isFinite(v))) throw Error("Missing real sea ice: " + group);
    one.push({
      site: p.site_id, group, region: p.region, compared_species: p.compared_species, year,
      adelie_n: +ad.count, compared_n: +other.count,
      log1p_count_ratio: Math.log1p(+other.count) - Math.log1p(+ad.count),
      sic_september_pct: months[1], sic_aug_nov_pct: mean(months),
    });
  }
  const yr = one.map(r => r.year), log = one.map(r => r.log1p_count_ratio);
  assertClose(slope(yr, log) * 10, +p.common_year_log1p_ratio_slope_decade, "original same-year trend " + group);
  groupTrends.push({
    group, site: p.site_id, compared_species: p.compared_species,
    n_shared_years: one.length,
    log1p_ratio_slope_decade: slope(yr, log) * 10,
    same_year_september_sic_slope_pp_decade: slope(yr, one.map(r => r.sic_september_pct)) * 10,
  });
  yearly.push(...one);
  for (let i = 1; i < one.length; i++) {
    if (one[i].year !== one[i - 1].year + 1) continue;
    intervals.push({
      site: p.site_id, group, compared_species: p.compared_species, year: one[i].year,
      n_adelie_before: one[i - 1].adelie_n, n_adelie_after: one[i].adelie_n,
      n_compared_before: one[i - 1].compared_n, n_compared_after: one[i].compared_n,
      delta_ratio: one[i].log1p_count_ratio - one[i - 1].log1p_count_ratio,
      delta_sic_september_pp: one[i].sic_september_pct - one[i - 1].sic_september_pct,
      delta_sic_aug_nov_pp: one[i].sic_aug_nov_pct - one[i - 1].sic_aug_nov_pct,
    });
  }
}
const assoc = {}, kindStats = {};
assoc.pooled_september_site_and_year = adjusted(yearly, "sic_september_pct", "log1p_count_ratio", ["group", "year"]);
assoc.pooled_aug_nov_site_and_year = adjusted(yearly, "sic_aug_nov_pct", "log1p_count_ratio", ["group", "year"]);
assoc.pooled_september_site = adjusted(yearly, "sic_september_pct", "log1p_count_ratio", ["group"]);
assoc.september_consecutive_difference_r = pearson(intervals.map(r => r.delta_sic_september_pp), intervals.map(r => r.delta_ratio));
assoc.aug_nov_consecutive_difference_r = pearson(intervals.map(r => r.delta_sic_aug_nov_pp), intervals.map(r => r.delta_ratio));
for (const species of ["GEPE", "CHPE"]) {
  const rows = yearly.filter(r => r.compared_species === species), dd = intervals.filter(r => r.compared_species === species);
  kindStats[species] = {
    ratio_years: rows.length, first_difference_intervals: dd.length,
    september_site_and_year: adjusted(rows, "sic_september_pct", "log1p_count_ratio", ["group", "year"]),
    september_consecutive_difference_r: pearson(dd.map(r => r.delta_sic_september_pp), dd.map(r => r.delta_ratio)),
  };
}
const leaveOneSiteOut = [...sites].sort().map(site => {
  const y = yearly.filter(r => r.site !== site), dd = intervals.filter(r => r.site !== site);
  return {
    excluded_site: site,
    september_site_and_year_r: adjusted(y, "sic_september_pct", "log1p_count_ratio", ["group", "year"]).partial_r,
    september_first_difference_r: pearson(dd.map(r => r.delta_sic_september_pp), dd.map(r => r.delta_ratio)),
  };
});
const predictions = [];
for (const obs of intervals) {
  // Strictly earlier test end years; observed test-year SIC makes this a conditional hindcast.
  const train = intervals.filter(r => r.year < obs.year);
  if (train.length < 20) continue; // Frozen early-training support gate.
  const ymean = mean(train.map(r => r.delta_ratio));
  const xmean = mean(train.map(r => r.delta_sic_september_pp));
  const xx = train.reduce((s, r) => s + (r.delta_sic_september_pp - xmean) ** 2, 0);
  const xy = train.reduce((s, r) => s + (r.delta_sic_september_pp - xmean) * (r.delta_ratio - ymean), 0);
  const beta = xy / (xx + 500); // Fixed exploratory ridge penalty on unscaled 9-month delta in percentage points.
  predictions.push({
    group: obs.group, site: obs.site, compared_species: obs.compared_species, test_year: obs.year,
    n_earlier_training_intervals: train.length,
    actual_delta_ratio: obs.delta_ratio, observed_test_year_delta_sic_pp: obs.delta_sic_september_pp,
    predict_no_change: 0, predict_prior_mean: ymean,
    predict_prior_mean_plus_sic: ymean + beta * (obs.delta_sic_september_pp - xmean),
  });
}
const err = (col) => {
  const diff = predictions.map(r => r[col] - r.actual_delta_ratio);
  return { mae: mean(diff.map(Math.abs)), rmse: Math.sqrt(mean(diff.map(v => v * v))) };
};
const scenarios = [];
for (const experiment of ["ssp245", "ssp585"]) for (const period of ["2041-2060", "2081-2100"]) {
  const data = F.filter(x => x.experiment === experiment && x.period === period);
  if (data.length !== 8 || new Set(data.map(r => r.site_id)).size !== 8) throw Error("Future source join changed");
  scenarios.push({
    experiment, period, site_count: data.length,
    tas_change_C_three_model_site_mean: mean(data.map(x => +x.tas_C_change_model_mean)),
    sic_change_pp_three_model_site_mean: mean(data.map(x => +x.SIC_pp_change_model_mean)),
    sites_all_models_tas_up: data.filter(x => x.all3_tas_increase === "1").length,
    sites_all_models_sic_down: data.filter(x => x.all3_sic_decrease === "1").length,
    sites_all_model_marine_cells_within50km: data.filter(x => x.all3_marine_cell_within50km === "1").length,
  });
}
const histDeclines = F.filter(x => x.experiment === "ssp585" && x.period === "2081-2100");
const summary = {
  version: 1, status: "observed_same_site_species_ratio_change_no_calibrated_future_demographic_response",
  source_git_blobs: expectedBlobs,
  counts: {
    original_MAPPPD_site_species_seasons: B.length, original_monthly_satellite_rows: I.length,
    matched_species_pairs: P.length, unique_sites: sites.size, matched_ratio_years: yearly.length,
    unique_site_years: new Set(yearly.map(r => r.site + "|" + r.year)).size,
    consecutive_ratio_intervals: intervals.length,
    historical_1991_2020_SIC_decline_sites: histDeclines.filter(r => +r.historical_obs_SIC_trend_pp_decade < 0).length,
    paired_window_september_SIC_decline_contrasts: groupTrends.filter(r => r.same_year_september_sic_slope_pp_decade < 0).length,
    matched_increasing_species_ratios: groupTrends.filter(r => r.log1p_ratio_slope_decade > 0).length,
  },
  historical: { associations: assoc, species: kindStats, leave_one_site_out: leaveOneSiteOut, group_trends: groupTrends },
  chronological_conditional_hindcast: {
    definition: "all records with interval end_year < test end_year, min 20 prior intervals, fixed ridge 500; same-year observed SIC input, full-panel cohort selection",
    test_intervals: predictions.length, test_sites: new Set(predictions.map(r => r.site)).size,
    no_change: err("predict_no_change"),
    prior_mean: err("predict_prior_mean"),
    prior_mean_plus_sic: err("predict_prior_mean_plus_sic"),
  },
  future_physical_scenarios_only: scenarios,
  boundary: "Association and chronology are exploratory and share site/ocean cells. Climate is not established to predict future species ratios or nest counts. No population/occupancy forecast. Salinity, SST, vegetation and snow are not entered into these same-year site counts.",
};
const expected = receipt.values;
if (process.argv.includes("--check-receipt")) {
  for (const [key, value] of Object.entries(receipt.counts)) {
    if (summary.counts[key] !== value) throw Error("Cohort gate " + key);
  }
  assertClose(assoc.pooled_september_site_and_year.partial_r, expected.pooled_site_year_r, "pooled site/year r");
  assertClose(assoc.september_consecutive_difference_r, expected.pooled_firstdiff_r, "pooled first difference");
  assertClose(kindStats.GEPE.september_site_and_year.partial_r, expected.gentoo_site_year_r, "gentoo adjusted r");
  assertClose(kindStats.CHPE.september_site_and_year.partial_r, expected.chinstrap_site_year_r, "chinstrap adjusted r");
  assertClose(summary.chronological_conditional_hindcast.no_change.mae, expected.zero_mae, "zero MAE");
  assertClose(summary.chronological_conditional_hindcast.prior_mean.mae, expected.prior_mean_mae, "prior MAE");
  assertClose(summary.chronological_conditional_hindcast.prior_mean_plus_sic.mae, expected.sic_mae, "SIC MAE");
  if (predictions.length !== receipt.predictions) throw Error("Prediction fold drift");
}
mkdirSync(outdir, { recursive: true });
writeFileSync(join(outdir, "summary.json"), JSON.stringify(summary, null, 2) + "\n");
writeFileSync(join(outdir, "same_year_ratios.csv"), csv(yearly));
writeFileSync(join(outdir, "consecutive_ratio_intervals.csv"), csv(intervals));
writeFileSync(join(outdir, "chronological_conditional_hindcasts.csv"), csv(predictions));
writeFileSync(join(outdir, "validation.json"), JSON.stringify({
  input_git_blobs_verified: true,
  frozen_receipt_passed: process.argv.includes("--check-receipt"),
  four_original_inputs_verified: Object.keys(inputs),
  matched_yearly: yearly.length, consecutive: intervals.length, forecast_checks: predictions.length,
  validated_at: "2026-10-31",
}, null, 2) + "\n");
console.log(JSON.stringify({
  counts: summary.counts, adjusted_september_r: assoc.pooled_september_site_and_year.partial_r,
  gentoo_r: kindStats.GEPE.september_site_and_year.partial_r,
  chinstrap_r: kindStats.CHPE.september_site_and_year.partial_r,
  future_2050_2100_climate: scenarios,
  conditional_hindcast: summary.chronological_conditional_hindcast,
  frozen_receipt_passed: process.argv.includes("--check-receipt"),
}, null, 2));
