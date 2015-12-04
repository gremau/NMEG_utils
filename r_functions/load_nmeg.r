# This file creates datasets from NMEG Ameriflux files and calculates
# Annual sums of fluxes.
#
# Greg Maurer - Nov 23, 2014

library(xts)

# Function to load one 30 minute ameriflux file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
load_aflx_file <- function( fname, year ){

    header <- read.csv(fname, skip=3, nrows=1)
    df <- read.csv(fname, skip=5, header=FALSE)
    df[df==-9999] <- NA
    colnames(df) <- colnames(header)

    return( df )
}


# Function to load a multiyear, 30 minute ameriflux file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
get_multiyr_aflx <- function( site, afpath, 
                             startyear=as.numeric(format(Sys.Date(), '%Y' )-1),
                             endyear=as.numeric(format(Sys.Date(), '%Y' )),
                             gapfilled=TRUE, old_dparse=FALSE){
    if (gapfilled==TRUE) {
        file_gap_type <- 'gapfilled'
    } else {
        file_gap_type <- 'with_gaps'
    }
    
    filenames <- list.files(afpath, full.names=TRUE)
    filenames <- filenames[grepl(site, filenames)]
    filenames <- filenames[grepl(file_gap_type, filenames)]

    my_df <- NULL

    for (i in 1:length(filenames)){
        file <- filenames[i]
        header <- read.csv(file, skip=3, nrows=1)
        df <- read.csv(file, skip=5, header=FALSE)
        df[df==-9999] <- NA
        colnames(df) <- colnames(header)

        if (is.data.frame( my_df )){
            my_df <- rbind(my_df, df)
        } else { 
            my_df <- df
        }
    }

    return( my_df )
}

# Load shared daily file for a site from NMEG_utils. If asked, this script will
# call the python script that makes these files.
get_daily_file <- function( site, make_new=FALSE ){
    if (make_new==TRUE){
        system('python ~/current/NMEG_utils/output_file_scripts/export_daily_files.py')
    }
    # The daily files are put here:
    dlypath <- '~/current/NMEG_utils/processed_data/'
    filenames <- list.files(dlypath, full.names=TRUE)
    filenames <- filenames[grepl(paste(site, '_daily.csv', sep=''), filenames)]
    df <- read.csv(filenames, header=TRUE)
    # Remove last row (2015 data containing NAs)
    df <- df[1:nrow(df)-1,]
    return(df)
}

# Convert daily dataframe into a time series (xts) object
daily_to_xts <- function( df ){
    # Get time column (should be $X)
    df_t <- as.Date(df$X)
    # Separate into numeric columns 
    df_num <- df[,2:ncol(df)]
    # Convert to xt
    df_xts <- xts(df_num, df_t)

    return(df_xts)
}

