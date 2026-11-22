# Outcome-blind temporal persistence diagnostic. Never treat absent positive as non-guano.
a<-commandArgs(trailingOnly=TRUE);stopifnot(length(a)==3)
x<-readRDS(a[1]);sites<-read.csv(a[2],stringsAsFactors=FALSE);sites<-unique(sites$site_id)
x<-x[x$site_id %in% sites & x$season>=1996 & x$season<=2012,]
xy<-t(vapply(x$geometry,function(g)as.numeric(g),numeric(2)))
d<-data.frame(site_id=as.character(x$site_id),season=as.integer(x$season),cell=as.character(x$cell),east=xy[,1],north=xy[,2],guano=as.character(x$guano_bin),bad=as.character(x$bad))
stopifnot(all(d$guano %in% c('1','TRUE','true')),all(d$bad %in% c('0','FALSE','false')))
coords<-unique(d[c('site_id','cell','east','north')]);ck<-paste(coords$site_id,coords$cell);conflict<-unique(ck[duplicated(ck)])
d<-d[!paste(d$site_id,d$cell) %in% conflict,]
d<-unique(d[c('site_id','season','east','north')]);d$key<-paste(d$east,d$north,sep=':')
rows<-list();selected<-list()
for(id in sort(sites)){
 train<-d[d$site_id==id & d$season<=2007,];test<-d[d$site_id==id & d$season>=2008,]
 n<-length(unique(train$season));if(n<10)next
 counts<-table(train$key);keys<-names(counts)[counts>=8 & counts/n>=.8];if(length(keys)==0)next
 selected[[id]]<-data.frame(site_id=id,key=keys,train_seasons=n,train_positive=as.integer(counts[keys]))
 for(y in 2008:2012){
 t<-test[test$season==y,];obs<-nrow(t)>0
 rows[[paste(id,y)]]<-data.frame(site_id=id,season=y,frozen_coordinates=length(keys),site_has_positive_records=obs,redetected_positive=if(obs)sum(keys %in% t$key) else NA,redetection_fraction=if(obs)mean(keys %in% t$key) else NA)
 }
}
write.csv(do.call(rbind,selected),file.path(a[3],'historical_train1996_2007_coordinates.csv'),row.names=FALSE)
write.csv(do.call(rbind,rows),file.path(a[3],'historical_test2008_2012_redetection.csv'),row.names=FALSE)
cat('training sites',length(selected),'test rows',length(rows),'\n')
