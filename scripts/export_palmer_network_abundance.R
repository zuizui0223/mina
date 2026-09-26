#!/usr/bin/env Rscript

# Stage-2 abundance export for the predeclared six-island Palmer network plus
# the Biscoe Point non-island benchmark.
#
# Site membership was frozen before this script was added:
# primary islands = TORG, LITC, HUMB, CHIS, CORM, DREA
# benchmark       = BISC

COMMIT <- "88c73a507e0921b2541c218c71eaf16721bc6502"
BASE <- sprintf(
  "https://raw.githubusercontent.com/CCheCastaldo/mapppdr/%s/data",
  COMMIT
)
ANALYSIS_SITES <- c("TORG", "LITC", "HUMB", "CHIS", "CORM", "DREA", "BISC")

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) >= 1) args[[1]] else "build/palmer_network_stage2"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

tmp <- tempfile("mapppdr-stage2-")
dir.create(tmp)
for (object in c("penguin_obs", "sites", "species", "site_species")) {
  target <- file.path(tmp, paste0(object, ".rda"))
  download.file(
    sprintf("%s/%s.rda", BASE, object),
    target,
    mode = "wb",
    quiet = TRUE
  )
  loaded <- load(target, envir = .GlobalEnv)
  if (!(object %in% loaded)) {
    stop(sprintf("expected object %s missing", object))
  }
}

common <- tolower(species$common_name)
focal_species <- species[
  grepl("adel", common) |
    grepl("chinstrap", common) |
    grepl("gentoo", common),
  ,
  drop = FALSE
]
if (nrow(focal_species) != 3) {
  print(species)
  stop(sprintf("expected three focal species, observed %d", nrow(focal_species)))
}

focal_sites <- sites[sites$site_id %in% ANALYSIS_SITES, , drop = FALSE]
if (nrow(focal_sites) != length(ANALYSIS_SITES)) {
  stop("not all frozen analysis sites were resolved")
}

focal_membership <- site_species[
  site_species$site_id %in% ANALYSIS_SITES &
    site_species$species_id %in% focal_species$species_id,
  ,
  drop = FALSE
]

focal_obs <- penguin_obs[
  penguin_obs$site_id %in% ANALYSIS_SITES &
    penguin_obs$species_id %in% focal_species$species_id,
  ,
  drop = FALSE
]

write.csv(focal_sites, file.path(out_dir, "sites.csv"), row.names = FALSE, na = "")
write.csv(focal_species, file.path(out_dir, "species.csv"), row.names = FALSE, na = "")
write.csv(
  focal_membership,
  file.path(out_dir, "site_species.csv"),
  row.names = FALSE,
  na = ""
)
write.csv(
  focal_obs,
  file.path(out_dir, "penguin_obs.csv"),
  row.names = FALSE,
  na = ""
)

cat(sprintf("mapppdr_commit=%s\n", COMMIT))
cat(sprintf("analysis_site_count=%d\n", nrow(focal_sites)))
cat(sprintf("membership_rows=%d\n", nrow(focal_membership)))
cat(sprintf("observation_rows=%d\n", nrow(focal_obs)))
