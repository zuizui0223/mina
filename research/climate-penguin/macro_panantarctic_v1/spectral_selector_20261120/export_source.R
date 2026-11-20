args <- commandArgs(trailingOnly=TRUE)
x <- readRDS(args[1])
sites <- read.csv(file.path(args[2], 'source_sites.csv'))
x <- x[x[['site_id']] %in% sites$site_id & x[['satellite']]==7 &
       x[['season']]>=1996 & x[['season']]<=2012, ]
stopifnot(all(x[['guano_bin']]==1),all(x[['bad']]==0),
          attr(x[['geometry']], 'crs')$input=='EPSG:3031')
xy <- t(vapply(x[['geometry']], function(g) as.numeric(g), numeric(2)))
cols <- c('site_id','region','Landsat.Product.Identifier.L1','satellite',
          'season','year','month','day','cell')
d <- as.data.frame(x)[,cols]
d$easting <- xy[,1]
d$northing <- xy[,2]
d$phase <- ifelse(d$season<=2007,'train','test')
write.table(d,file.path(args[2],'source_positive_records.csv'),sep=',',
            row.names=FALSE,col.names=TRUE,quote=TRUE,eol='\n',fileEncoding='UTF-8')
