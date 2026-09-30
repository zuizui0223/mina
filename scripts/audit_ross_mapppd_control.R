#!/usr/bin/env Rscript

# Audit Ross Island Adelie breeding-pair counts from the same pinned mapppdr
# snapshot already used elsewhere in mina. This touches no individual resight data.

COMMIT <- "88c73a507e0921b2541c218c71eaf16721bc6502"
BASE <- sprintf(
  "https://raw.githubusercontent.com/CCheCastaldo/mapppdr/%s/data",
  COMMIT
)

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) >= 1) args[[1]] else "build/ross_mapppd"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

tmp <- tempfile("mapppdr-ross-")
dir.create(tmp)
for (object in c("penguin_obs", "sites", "species")) {
  target <- file.path(tmp, paste0(object, ".rda"))
  download.file(sprintf("%s/%s.rda", BASE, object), target, mode = "wb", quiet = TRUE)
  loaded <- load(target, envir = .GlobalEnv)
  if (!(object %in% loaded)) stop(sprintf("missing %s", object))
}

site_candidates <- sites[
  grepl("Royds|Bird|Crozier", sites$site_name, ignore.case = TRUE),
  ,
  drop = FALSE
]
write.csv(site_candidates, file.path(out_dir, "site_candidates.csv"), row.names = FALSE, na = "")

common <- tolower(species$common_name)
adelie <- species[
  grepl("adel", common) |
    (species$genus == "Pygoscelis" & species$species == "adeliae"),
  ,
  drop = FALSE
]
if (nrow(adelie) != 1) {
  print(adelie)
  stop(sprintf("expected exactly one Adelie species row, got %d", nrow(adelie)))
}
write.csv(adelie, file.path(out_dir, "adelie_species.csv"), row.names = FALSE, na = "")

# Do not guess site aliases. Keep all name-matched candidates in the audit.
obs <- penguin_obs[
  penguin_obs$site_id %in% site_candidates$site_id &
    penguin_obs$species_id == adelie$species_id,
  ,
  drop = FALSE
]
write.csv(obs, file.path(out_dir, "ross_adelie_obs.csv"), row.names = FALSE, na = "")

nests <- obs[obs$type == "nests" & !is.na(obs$count), , drop = FALSE]
write.csv(nests, file.path(out_dir, "ross_adelie_nest_counts.csv"), row.names = FALSE, na = "")

cat(sprintf("mapppdr_commit=%s\n", COMMIT))
cat("penguin_obs_columns=", paste(names(penguin_obs), collapse=","), "\n", sep="")
cat("site_candidates=", nrow(site_candidates), "\n", sep="")
for (i in seq_len(nrow(site_candidates))) {
  cat(sprintf(
    "site[%d]=%s|%s\n",
    i,
    as.character(site_candidates$site_id[i]),
    as.character(site_candidates$site_name[i])
  ))
}
cat("adelie_species_id=", adelie$species_id[1], "\n", sep="")
cat("ross_observation_rows=", nrow(obs), "\n", sep="")
cat("nest_count_rows=", nrow(nests), "\n", sep="")
if (nrow(nests) > 0) {
  for (sid in unique(nests$site_id)) {
    local <- nests[nests$site_id == sid, , drop=FALSE]
    sname <- as.character(site_candidates$site_name[match(sid, site_candidates$site_id)])
    cat(sprintf(
      "coverage=%s|%s|n=%d|years=%d-%d|distinct_years=%d\n",
      sid, sname, nrow(local), min(local$year), max(local$year),
      length(unique(local$year))
    ))
  }
}
