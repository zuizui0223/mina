#!/usr/bin/env Rscript
# Export exclusively ORIGINAL Youngflesh L4/5/7 preselected old guano pixels
# belonging to exactly fixed published-matched 860 site×season historical rows.
# Do not read 2013+ imagery, DEEP-AA exposures or old/new ecological outcomes.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=3L) stop("Usage: Rscript exporter.R original_RDS original860_membership_csv original_pixel_out.csv")
rds_path <- args[[1]]
matched_path <- args[[2]]
out_path <- args[[3]]
x <- readRDS(rds_path)
need <- c("site_id","season","year","month","day","cell","satellite",
          "guano_bin","bad","blue","green","red","nir","swir1","swir2")
if (!all(need %in% names(x))) stop("Native original old RDS pixel/sensor/band fields missing")
if(length(x[["site_id"]])<150000L || length(x[["site_id"]])>200000L){
  stop("Original full RDS pixel population has changed")
}
mem <- read.csv(matched_path,stringsAsFactors=FALSE)
if (!all(c("site_id","season","n_source_pixels","n_observed_days") %in% names(mem))){
  stop("Old matched-860 source membership and count columns missing")
}
if(nrow(mem)!=860L || length(unique(mem$site_id))!=88L ||
   length(unique(mem$source_region))!=13L ||
   anyDuplicated(paste(mem$site_id,mem$season,sep=":")) ||
   min(mem$season)!=1996L || max(mem$season)!=2012L){
  stop("Original frozen 860 site×season target membership changed")
}
keys <- paste(as.character(x[["site_id"]]),as.integer(x[["season"]]),sep=":")
allow <- paste(mem$site_id,mem$season,sep=":")
selected <- keys %in% allow
if(sum(selected)!=sum(mem$n_source_pixels)){
  stop(sprintf("Original frozen 860 pixel denominator mismatch %d != %d",sum(selected),sum(mem$n_source_pixels)))
}
d <- as.data.frame(x[,need,drop=FALSE])
# sf's [ method may reattach geometry; explicitly convert to plain data frame
d <- as.data.frame(d)[selected,need,drop=FALSE]
if (!all(as.character(d$guano_bin) %in% c("1","TRUE","true")) ||
    !all(as.character(d$bad) %in% c("0","FALSE","false"))) {
  stop("Original publisher selected pixel labels are not all guano=true,bad=false")
}
if(!all(as.integer(d$satellite)%in%c(4L,5L,7L)))stop("Unsupported old Landsat sensor")
if(!all(as.integer(d$month)%in%c(11L,12L,1L,2L)))stop("Pixel acquisition outside fixed Nov–Feb")
bands <- c("blue","green","red","nir","swir1","swir2")
if (!all(is.finite(as.matrix(d[,bands]))))stop("Publisher old RDS selected reflectance contains nonfinite bands")
key <- paste(d$site_id,d$season,sep=":")
sizes <- as.integer(table(factor(key,levels=allow)))
if (!identical(sizes,as.integer(mem$n_source_pixels))){
  stop("Original source image pixel counts differ on a frozen site×season key")
}
daykey <- paste(d$site_id,d$season,d$year,d$month,d$day,sep=":")
day_sites <- strsplit(unique(daykey),":",fixed=TRUE)
daysitekeys <- vapply(day_sites,function(v)paste(v[1:2],collapse=":"),character(1))
daycounts <- as.integer(table(factor(daysitekeys,levels=allow)))
if (!identical(daycounts,as.integer(mem$n_observed_days))){
  stop("Original observed unique calendar day counts differ from frozen original 860")
}
# No derived optical δ15N Y in exporter: predictors and actual time keys only.
df <- d[,c("site_id","season","year","month","day","cell","satellite",bands),drop=FALSE]
write.csv(df,out_path,row.names=FALSE,na="")
cat("OLD_RDS_860_PIXELS_SOURCE_ONLY_VERIFIED",
    "source_original_full_rows",length(x[["site_id"]]),
    "source_exact860_pixel_rows",nrow(df),
    "fixed_site_seasons",nrow(mem),
    "original_source_days",length(unique(daykey)),
    "old_source_sensors",paste(sort(unique(df$satellite)),collapse=","),
    "\n")
