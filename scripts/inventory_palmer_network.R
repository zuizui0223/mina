#!/usr/bin/env Rscript

# Outcome-blind inventory of APBP breeding sites within 20 km of Palmer Station.
# This script intentionally never loads penguin_obs.

COMMIT <- "88c73a507e0921b2541c218c71eaf16721bc6502"
BASE <- sprintf(
  "https://raw.githubusercontent.com/CCheCastaldo/mapppdr/%s/data",
  COMMIT
)
PALMER_LAT <- -64.77416666666667
PALMER_LON <- -64.05333333333333
RADIUS_KM <- 20

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) >= 1) args[[1]] else "build/palmer_network_inventory"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

tmp <- tempfile("mapppdr-inventory-")
dir.create(tmp)

for (object in c("sites", "species", "site_species")) {
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

haversine_km <- function(lat1, lon1, lat2, lon2) {
  rad <- pi / 180
  p1 <- lat1 * rad
  p2 <- lat2 * rad
  dp <- (lat2 - lat1) * rad
  dl <- (lon2 - lon1) * rad
  a <- sin(dp / 2)^2 + cos(p1) * cos(p2) * sin(dl / 2)^2
  6371.0088 * 2 * atan2(sqrt(a), sqrt(1 - a))
}

distance <- mapply(
  haversine_km,
  PALMER_LAT,
  PALMER_LON,
  sites$latitude,
  sites$longitude
)

inventory <- sites[distance <= RADIUS_KM, , drop = FALSE]
inventory$distance_from_palmer_km <- distance[distance <= RADIUS_KM]
inventory <- inventory[order(inventory$distance_from_palmer_km), , drop = FALSE]

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

membership <- site_species[
  site_species$site_id %in% inventory$site_id &
    site_species$species_id %in% focal_species$species_id,
  ,
  drop = FALSE
]
membership <- merge(
  membership,
  focal_species[, c("species_id", "common_name")],
  by = "species_id",
  all.x = TRUE
)

write.csv(
  inventory,
  file.path(out_dir, "sites_within_20km.csv"),
  row.names = FALSE,
  na = ""
)
write.csv(
  membership,
  file.path(out_dir, "focal_breeding_membership.csv"),
  row.names = FALSE,
  na = ""
)

cat(sprintf("mapppdr_commit=%s\n", COMMIT))
cat(sprintf("radius_km=%g\n", RADIUS_KM))
cat(sprintf("site_count=%d\n", nrow(inventory)))
cat("sites:\n")
for (i in seq_len(nrow(inventory))) {
  row <- inventory[i, ]
  spp <- membership$common_name[membership$site_id == row$site_id]
  cat(sprintf(
    "%s\t%s\t%.4f km\t%s\n",
    row$site_id,
    row$site_name,
    row$distance_from_palmer_km,
    paste(sort(spp), collapse = ",")
  ))
}
