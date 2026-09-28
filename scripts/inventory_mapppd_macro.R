#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NA_character_) {
  idx <- match(flag, args)
  if (is.na(idx) || idx == length(args)) return(default)
  args[[idx + 1]]
}

root <- get_arg("--mapppdr-dir")
out <- get_arg("--out")
if (is.na(root) || is.na(out)) stop("--mapppdr-dir and --out are required")

load(file.path(root, "data", "sites.rda"))
load(file.path(root, "data", "species.rda"))
load(file.path(root, "data", "site_species.rda"))
load(file.path(root, "data", "penguin_obs.rda"))

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("jsonlite is required")
}

nest <- penguin_obs[
  penguin_obs$type == "nests" & !is.na(penguin_obs$count),
  ,
  drop = FALSE
]

species_ids <- sort(unique(site_species$species_id))

species_rows <- lapply(species_ids, function(sp) {
  ss <- site_species[site_species$species_id == sp, , drop = FALSE]
  no <- nest[nest$species_id == sp, , drop = FALSE]
  if (nrow(no) > 0) {
    by_site <- split(no, no$site_id)
    n_years <- vapply(
      by_site,
      function(x) length(unique(x$year[!is.na(x$year)])),
      numeric(1)
    )
    spans <- vapply(
      by_site,
      function(x) {
        y <- unique(x$year[!is.na(x$year)])
        if (length(y) == 0) return(NA_real_)
        max(y) - min(y)
      },
      numeric(1)
    )
    site_ids <- names(by_site)
  } else {
    n_years <- numeric()
    spans <- numeric()
    site_ids <- character()
  }

  data.frame(
    species_id = sp,
    known_breeding_sites = length(unique(ss$site_id)),
    nest_count_records = nrow(no),
    sites_with_nest_counts = length(unique(site_ids)),
    sites_ge_2_years = sum(n_years >= 2),
    sites_ge_5_years = sum(n_years >= 5),
    sites_ge_10_years = sum(n_years >= 10),
    sites_ge_20_years = sum(n_years >= 20),
    sites_span_ge_10y = sum(spans >= 10, na.rm = TRUE),
    sites_span_ge_20y = sum(spans >= 20, na.rm = TRUE),
    sites_span_ge_30y = sum(spans >= 30, na.rm = TRUE),
    sites_ge5_and_span_ge10 = sum(n_years >= 5 & spans >= 10, na.rm = TRUE),
    sites_ge10_and_span_ge20 = sum(n_years >= 10 & spans >= 20, na.rm = TRUE),
    stringsAsFactors = FALSE
  )
})
species_summary <- do.call(rbind, species_rows)

species_lookup <- species[, c("species_id", "common_name", "genus", "species")]
species_summary <- merge(
  species_summary,
  species_lookup,
  by = "species_id",
  all.x = TRUE,
  sort = FALSE
)

site_richness <- table(site_species$site_id)
year_values <- penguin_obs$year[!is.na(penguin_obs$year)]

accuracy_counts <- as.data.frame(table(
  nest$accuracy,
  useNA = "ifany"
), stringsAsFactors = FALSE)
names(accuracy_counts) <- c("accuracy", "n")

vantage_counts <- as.data.frame(table(
  nest$vantage,
  useNA = "ifany"
), stringsAsFactors = FALSE)
names(vantage_counts) <- c("vantage", "n")

result <- list(
  schema_version = 1,
  inventory_id = "mina-mapppd-macro-inventory-v1",
  mapppdr_commit = "88c73a507e0921b2541c218c71eaf16721bc6502",
  total_sites = nrow(sites),
  total_site_species_links = nrow(site_species),
  total_observation_records = nrow(penguin_obs),
  total_nest_count_records = nrow(nest),
  observation_year_min = if (length(year_values)) min(year_values) else NA,
  observation_year_max = if (length(year_values)) max(year_values) else NA,
  regions = length(unique(sites$region)),
  ccamlr_units = length(unique(sites$ccamlr_id)),
  site_species_richness = list(
    sites_with_1_species = sum(site_richness == 1),
    sites_with_2_species = sum(site_richness == 2),
    sites_with_3plus_species = sum(site_richness >= 3),
    max_species_per_site = max(site_richness)
  ),
  species_summary = species_summary,
  nest_accuracy_counts = accuracy_counts,
  nest_vantage_counts = vantage_counts,
  candidate_trend_gate = list(
    definition = "at least 5 distinct nest-count years spanning at least 10 years",
    total_site_species_units = sum(species_summary$sites_ge5_and_span_ge10)
  ),
  stricter_trend_gate = list(
    definition = "at least 10 distinct nest-count years spanning at least 20 years",
    total_site_species_units = sum(species_summary$sites_ge10_and_span_ge20)
  )
)

dir.create(dirname(out), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(result, out, pretty = TRUE, auto_unbox = TRUE, na = "null")
cat(jsonlite::toJSON(result, pretty = TRUE, auto_unbox = TRUE, na = "null"))
cat("\n")
