#!/usr/bin/env Rscript
# Original Youngflesh 2026 RDS source-only frozen pixel and guano-bin geometry audit.
# Does not read isotope Y, does not open 2013–2021 image reflectance, no polynya fit.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=3L) stop("Expected 3 positional args: original_rds original88_csv out_directory")
root <- args[[1]]
original88 <- args[[2]]
out <- args[[3]]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
x <- readRDS(root)
needed <- c("site_id","season","year","month","day","cell","satellite","guano_bin","bad","geometry")
if (!all(needed %in% names(x))) stop("Expected original raw site/cell/guano_bad/geometry columns absent")
if (length(x$site_id)<150000L || length(x$site_id)>200000L) stop("Original raw RDS denominator drift")
source <- read.csv(original88,stringsAsFactors=FALSE)
source <- source[source$radius_km==100L,]
if (nrow(source)!=88L || anyDuplicated(source$site_id)) stop("Original fixed site IDs drift")
eligible <- as.character(x$site_id) %in% source$site_id & as.integer(x$season)<=2012
if (sum(eligible)<10000L) stop("Original known site geometry support unexpectedly tiny")
field <- function(name) x[[name]][eligible]
geo <- x[["geometry"]]
geolist <- geo[eligible]
if (length(geolist)!=sum(eligible)) stop("Source geometry length mismatch")
print(paste("SOURCE_ROOT_CLASSES", paste(class(x),collapse=";")))
print(paste("SOURCE_GEOMETRY_CLASSES", paste(class(geo),collapse=";")))
print(str(attributes(geo)$crs))
print("SOURCE_FIRST_GEOMETRY_RAW")
print(str(geolist[[1]]))
# The original source's sf point geometry may be sf POINT, matrix, or WKT;
# do not infer CRS or coordinates if the source is not a numeric point.
extract_xy <- function(p) {
  if (is.numeric(p) && length(p)==2L) return(as.numeric(p))
  if (is.matrix(p) && nrow(p)==1L && ncol(p)>=2L) return(as.numeric(p[1,1:2]))
  c(NA_real_,NA_real_)
}
xy <- vapply(geolist,extract_xy, numeric(2))
if (!is.matrix(xy) || nrow(xy)!=2L)stop("RDS geometry coordinate conversion result invalid")
good <- colSums(is.finite(xy))==2L
crs <- attr(geo,"crs")
crs_input <- if(is.list(crs) && !is.null(crs$input)) as.character(crs$input) else "CRS_NOT_EXPLICIT"
if (!is.finite(sum(good)))stop("Cannot count genuine numeric pixel centers")
d <- data.frame(
 site_id=as.character(field("site_id")),
 season=as.integer(field("season")),
 source_acquisition_year=as.integer(field("year")),
 source_acquisition_month=as.integer(field("month")),
 source_acquisition_day=as.integer(field("day")),
 source_satellite=as.character(field("satellite")),
 source_pixel_cell_id=as.character(field("cell")),
 original_guano_bin=as.character(field("guano_bin")),
 original_bad_flag=as.character(field("bad")),
 source_geometry_easting=xy[1,],
 source_geometry_northing=xy[2,],
 source_geometry_numeric_point=good,
 stringsAsFactors=FALSE
)
if (any(is.na(d$site_id)) || any(is.na(d$source_pixel_cell_id)))stop("Original source polygon/pixel IDs missing")
# Unique coordinates for same cell should stay fixed, else cannot use historical pixel footprint.
coords <- d[good, c("site_id","source_pixel_cell_id","source_geometry_easting","source_geometry_northing")]
coords <- unique(coords)
lookup <- paste(coords$site_id,coords$source_pixel_cell_id,sep="::")
dup <- unique(lookup[duplicated(lookup)])
fixed_unique <- coords[!(lookup %in% dup),]
fixed_unique$original_site_cell_has_one_unchanging_true_geometric_location <- TRUE
write.csv(fixed_unique,file.path(out,"original_88_source_stable_site_cell_coordinate_candidates_NOT_future_roi.csv"),row.names=FALSE)
per_site <- data.frame()
for(site in sort(unique(d$site_id))){
  sub <- d[d$site_id==site,]
  if (!nrow(sub)) next
  per_site <- rbind(per_site,data.frame(
    site_id=site,n_source_pixel_rows=nrow(sub),
    n_source_unique_pixel_ids=length(unique(sub$source_pixel_cell_id)),
    n_raw_image_seasons=length(unique(sub$season)),
    n_native_point_geometry_rows=sum(sub$source_geometry_numeric_point),
    n_stable_location_cells=sum(fixed_unique$site_id==site),
    n_original_l7_rows=sum(sub$source_satellite %in% c("7",7)),
    n_old_guano_bin_1_rows=sum(sub$original_guano_bin %in% c("1","TRUE","true")),
    n_old_bad_flag_true_rows=sum(sub$original_bad_flag %in% c("1","TRUE","true"))
  ))
}
write.csv(per_site,file.path(out,"original_88_site_geometry_roi_source_only_support.csv"),row.names=FALSE)
result <- list(
 status=if(sum(good)==nrow(d) && length(dup)==0L)
  "PASS_ORIGINAL_88_RAW_GUANO_PIXEL_GEOMETRY_SOURCE_ONLY"
 else "GUANO_GEOMETRY_OR_STABLE_PIXEL_ROI_SOURCE_LIMITED",
 source_kind="Youngflesh 2026 source original published RDS, old 1984–2012 seasonal records only",
 raw_source_rows_total=length(x$site_id),
 original_sites_selected=88L,
 original_pixel_rows_selected=nrow(d),
 native_point_coordinate_rows=sum(good),
 native_geometry_class=paste(class(geo),collapse=";"),
 native_geometry_crs=crs_input,
 source_site_cell_number_with_multiple_distinct_coordinates=length(dup),
 stable_geolocated_original_site_cell_rows=nrow(fixed_unique),
 original_guano_bin_label_distribution=as.list(table(d$original_guano_bin)),
 original_bad_flag_distribution=as.list(table(d$original_bad_flag)),
 source_satellite_counts=as.list(table(d$source_satellite)),
 original_source_88_sites_with_any_geometry=sum(per_site$n_stable_location_cells>0),
 no_2013_2021_new_L8_image_values_opened=TRUE,
 no_new_delta15N_proxy_computed=TRUE,
 no_source_polynya_response_test_run=TRUE,
 old_historic_guano_pixel_geometry_not_a_frozen_valid_new_2013_2021_guano_classification=TRUE
)
# Use base R hand-written metadata representation without introducing jsonlite dependency
dput(result,file=file.path(out,"original_88_guano_RDS_geometry_source_receipt.R"))
cat("ORIGINAL_88_PIXEL_GEOMETRY_AUDIT_STATUS",result$status,"\n")
cat("ORIGINAL_88_PIXEL_GEOMETRY_AUDIT_SUMMARY",result$original_pixel_rows_selected,
  result$native_point_coordinate_rows,result$source_site_cell_number_with_multiple_distinct_coordinates,
  result$stable_geolocated_original_site_cell_rows,"\n")
print(result[c("original_guano_bin_label_distribution","original_bad_flag_distribution","source_satellite_counts")])
