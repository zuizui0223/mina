a <- commandArgs(trailingOnly=TRUE)
x <- readRDS(a[1])
x <- x[x[['season']]>=1996 & x[['season']]<=2007,]
xy <- t(vapply(x[['geometry']],function(g)as.numeric(g),numeric(2)))
d <- unique(data.frame(site_id=x[['site_id']],easting=xy[,1],northing=xy[,2]))
write.table(d,a[2],sep=',',row.names=FALSE,quote=TRUE,eol='\n')
