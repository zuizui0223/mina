# Original positive-record recurrence; missing pixel-years remain unknown.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3L)
x <- readRDS(args[1])
sites <- read.csv(args[2], stringsAsFactors=FALSE)
sites <- sites[sites$radius_km==100,]
stopifnot(nrow(sites)==88L, !anyDuplicated(sites$site_id))
dir.create(args[3], recursive=TRUE, showWarnings=FALSE)
crs <- attr(x$geometry, 'crs')
stopifnot(grepl('3031', crs$input))
keep <- x$site_id %in% sites$site_id & x$season>=1996 & x$season<=2012
y <- x[keep,]
xy <- t(vapply(y$geometry, function(g) as.numeric(g), numeric(2)))
d <- data.frame(site_id=as.character(y$site_id), season=as.integer(y$season),
                cell=as.character(y$cell), east=xy[,1], north=xy[,2],
                guano=as.character(y$guano_bin), bad=as.character(y$bad))
stopifnot(all(is.finite(d$east)), all(is.finite(d$north)))
write.csv(as.data.frame(table(d$guano,d$bad)), file.path(args[3],'source_label_counts.csv'),row.names=FALSE)
good <- d$guano %in% c('1','TRUE','true') & d$bad %in% c('0','FALSE','false')
coordinates <- unique(d[c('site_id','cell','east','north')])
cellkey <- paste(coordinates$site_id,coordinates$cell,sep='::')
conflicting <- unique(cellkey[duplicated(cellkey)])
d <- d[good & !(paste(d$site_id,d$cell,sep='::') %in% conflicting),]
rows <- list(); summaries <- list()
for (id in sort(sites$site_id)) {
  sub <- d[d$site_id==id,]
  nseasons <- length(unique(sub$season))
  if (nrow(sub)>0) {
    unique_seasons <- unique(sub[c('east','north','season')])
    pixel <- aggregate(season~east+north, unique_seasons, length)
    names(pixel)[3] <- 'positive_seasons'
    pixel$site_id <- id
    pixel$available_site_seasons <- nseasons
    pixel$recurrence <- pixel$positive_seasons/nseasons
    pixel$primary_selected <- nseasons>=10 & pixel$positive_seasons>=8 & pixel$recurrence>=0.8
    pixel$calendar_14_of_17 <- pixel$positive_seasons>=14
    rows[[id]] <- pixel
    count <- sum(pixel$primary_selected)
  } else count <- 0L
  summaries[[id]] <- data.frame(site_id=id, available_site_seasons=nseasons,
    primary_pixels=count, reason=if(nseasons<10) 'fewer_than_10_source_seasons' else if(count==0) 'no_80pct_recurrent_coordinate' else 'selected')
}
pixels <- do.call(rbind, rows)
write.csv(pixels,file.path(args[3],'all_historical_coordinate_recurrence.csv'),row.names=FALSE)
write.csv(pixels[pixels$primary_selected,],file.path(args[3],'fixed_recurrent_guano_roi.csv'),row.names=FALSE)
write.csv(do.call(rbind,summaries),file.path(args[3],'all_88_site_accounting.csv'),row.names=FALSE)
cat('source selected rows',nrow(d),'conflicting site/cell IDs',length(conflicting),'\n')
cat('primary pixels',sum(pixels$primary_selected),'sites',length(unique(pixels$site_id[pixels$primary_selected])),'\n')
cat('strict 14/17 pixels',sum(pixels$calendar_14_of_17),'\n')
