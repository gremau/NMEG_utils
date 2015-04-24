# This file creates datasets from NMEG Ameriflux files and calculates
# Annual sums of fluxes.
#
# Greg Maurer - Nov 23, 2014

setwd('~/current/NMEG_fluxdata/data_analysis/R/')

source('printfigs.r')

proc_path <- '../processed_data/'
raw_reich_path <- '~/sftp/eddyflux/Ameriflux_files_GM/2009-2013_Reichstein'
raw_lass_path <- '~/sftp/eddyflux/Ameriflux_files_GM/2009-2013_Lasslop'

reich_files <- list.files(raw_reich_path, full.names=TRUE)
lass_files <- list.files(raw_lass_path, full.names=TRUE)

reich_files_gf <- reich_files[grepl("gapfilled", reich_files)]
lass_files_gf <- lass_files[grepl("gapfilled", lass_files)]
reich_files_wg <- reich_files[grepl("with_gaps", reich_files)]
lass_files_wg <- lass_files[grepl("with_gaps", lass_files)]

gf_files <- c(reich_files_gf, lass_files_gf)

library(ggplot2)
library(plyr)

df_reich <- data.frame(matrix(NA, nrow=length(reich_files_gf), ncol = 8))
colnames(df_reich) = c('year','site','GPPsum','REsum','NEEsum','ETsum','Psum','Part')

df_lass <- data.frame(matrix(NA, nrow=length(lass_files_gf), ncol = 8))
colnames(df_lass) = c('year','site','GPPsum','REsum','NEEsum','ETsum','Psum','Part')


for (i in 1:length(reich_files_gf)) {
  
  # Read in files
  file <- reich_files_gf[i]
  header <- read.csv(file, skip=3, nrows=1)
  new <- read.csv(file, skip=5, header=FALSE)
  new[new==-9999] <- NA
  colnames(new) <- colnames(header)
  
  toks1 <- strsplit(file, '/')
  fname <- toks1[[1]][[8]]
  toks2 <- strsplit(fname, '_')
  df_reich$year[i] <- toks2[[1]][2]
  df_reich$site[i] <- toks2[[1]][1]
  # Calculate annual sums
  GPPgCm_30min <- new$GPP * (12.011/1e+06) * 1800
  df_reich$GPPsum[i] <- sum(GPPgCm_30min, na.rm = TRUE)
  
  REgCm_30min <- new$RE * (12.011/1e+06) * 1800
  df_reich$REsum[i] <- sum(REgCm_30min, na.rm = TRUE)
  
  NEEgCm_30min <- new$FC * (12.011/1e+06) * 1800
  df_reich$NEEsum[i] <- sum(NEEgCm_30min, na.rm = TRUE)
  
  ETmm_30min <- new$FH2O * (1800/1e+06)
  df_reich$ETsum[i] <- sum(ETmm_30min, na.rm=TRUE)
  
  df_reich$Psum[i] <- sum(new$PRECIP, na.rm=TRUE)
}

for (i in 1:length(lass_files_gf)) {
  
  # Read in files
  file <- lass_files_gf[i]
  header <- read.csv(file, skip=3, nrows=1)
  new <- read.csv(file, skip=5, header=FALSE)
  new[new==-9999] <- NA
  colnames(new) <- colnames(header)
  
  toks1 <- strsplit(file, '/')
  fname <- toks1[[1]][[8]]
  toks2 <- strsplit(fname, '_')
  df_lass$year[i] <- toks2[[1]][2]
  df_lass$site[i] <- toks2[[1]][1]
  # Calculate annual sums
  GPPgCm_30min <- new$GPP * (12.011/1e+06) * 1800
  df_lass$GPPsum[i] <- sum(GPPgCm_30min, na.rm = TRUE)
  
  REgCm_30min <- new$RE * (12.011/1e+06) * 1800
  df_lass$REsum[i] <- sum(REgCm_30min, na.rm = TRUE)
  
  NEEgCm_30min <- new$FC * (12.011/1e+06) * 1800
  df_lass$NEEsum[i] <- sum(NEEgCm_30min, na.rm = TRUE)
  
  ETmm_30min <- new$FH2O * (1800/1e+06)
  df_lass$ETsum[i] <- sum(ETmm_30min, na.rm = TRUE)
  
  df_lass$Psum[i] <- sum(new$PRECIP, na.rm=TRUE)
}

df_reich$Part <- 'Reichstein'
df_lass$Part <- 'Lasslop'

allsums <- rbind(df_reich, df_lass)

allsums$site2 <- 
  revalue(allsums$site, c("US-Mpg"="PJ_girdle",
                                 "US-Mpj"="PJ",
                                 "US-Seg"="GLand",
                                 "US-Sen"="New_GLand",
                                 "US-Ses"="SLand",
                                 "US-Wjs"="JSav",
                                 "US-Vcp"="PPine",
                                 "US-Vcm"="MCon"))

reorder <- c('GLand', 'New_GLand', 'SLand', 'PJ', 'PJ_girdle', 'JSav',
             'PPine', 'MCon')

# Make a new column that includes the citation (made for x axis labeling)
allsums$site2 <- factor(allsums$site2, levels=reorder)

write.table(subset(allsums, Part=='Reichstein'), paste(proc_path, 'export.txt'),
            row.names=F)


REplot <- ggplot(allsums, aes(x=year, y=REsum)) +
  geom_point(aes(colour = factor(Part)), alpha=0.6, size=4) + 
  facet_wrap(~site2) + guides(colour=guide_legend(title="Partitioning"))

GPPplot <- ggplot(allsums, aes(x=year, y=GPPsum)) +
  geom_point(aes(colour = factor(Part)), alpha=0.6, size=4) + 
  facet_wrap(~site2) + guides(colour=guide_legend(title="Partitioning"))

ETplot <- ggplot(allsums, aes(x=year, y=ETsum)) +
  geom_point(aes(colour = factor(Part)), alpha=0.6, size=4) + 
  facet_wrap(~site2) + guides(colour=guide_legend(title="Partitioning"))

Pplot <- ggplot(allsums, aes(x=year, y=Psum)) +
  geom_point(aes(colour = factor(Part)), alpha=0.6, size=4) + 
  facet_wrap(~site2) + guides(colour=guide_legend(title="Partitioning"))

NEEplot <- ggplot(allsums, aes(x=year, y=NEEsum)) +
  geom_point(aes(colour = factor(Part)), alpha=0.6, size=4) + 
  facet_wrap(~site2) + guides(colour=guide_legend(title="Partitioning"))

printfigs(REplot, "RE_part.eps", 8, 6)
printfigs(REplot, "RE_part.svg", 8, 6)
printfigs(GPPplot, "GPP_part.eps", 8, 6)
printfigs(GPPplot, "GPP_part.svg", 8, 6)
printfigs(ETplot, "ET_part.eps", 8, 6)
printfigs(ETplot, "ET_part.svg", 8, 6)
printfigs(Pplot, "P_part.eps", 8, 6)
printfigs(Pplot, "P_part.svg", 8, 6)
printfigs(NEEplot, "NEE_part.eps", 8, 6)
printfigs(NEEplot, "NEE_part.svg", 8, 6)


