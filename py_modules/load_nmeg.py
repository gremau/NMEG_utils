""" 
Functions for loading various NMEG data files

 load_nmeg.py
 Greg Maurer
"""

import numpy as np
#import ipdb as ipdb
import datetime as dt
import pandas as pd
import os

now = dt.datetime.now()


def load_aflx_file( fname, year ) :
    """
    Load a specified ameriflux file and return a pandas DataFrame object.
    DataFrame has a datetime index and has been reindexed to include all
    30 minute periods in one year. Two file formats (old AF or new AF
    format) can be parsed and headers/index will be converted from old to
    new format.
    
    Args:
        fname (str) : path and filename of desired AF file
        year (int)  : year of ameriflux file

    Return:
        parsed_df   : pandas DataFrame    
    """
    # a date parser for older AF files (2007-2008)
    def dparse1( yr, doy, hhmm ):       
        yr = int( yr )
        # Some files have a line of zeros at the end - hack it
        if yr != year:
            yr = 1955

        hhmm = hhmm.zfill( 4 )
        doy = int( doy )
        return ( dt.datetime( yr - 1, 12, 31 ) + 
                dt.timedelta( days=doy, hours=int( hhmm[ 0:2 ] ),
                    minutes=int( hhmm[2:4] )))
        
    print('Parsing ' + fname)

    # The old files, which we are still using for now, have different date
    # columns and variable names, so they need to be parsed a little
    # differently and converted.
    if year < 2009:
        # Use old date parser
        parsed_df =  pd.read_csv( fname, skiprows=( 0,1,2,4 ), header=0,
                parse_dates={ 'Date':[ 0, 1, 2 ] }, date_parser=dparse1,
                na_values='-9999', index_col='Date' )
        # Rename old columns to new format
        parsed_df.rename(columns={ 
            'FC':'FC_F', 'Rg':'SW_IN_F', 'Rg_out':'SW_OUT', 'Rlong_in':'LW_IN',
            'Rlong_out':'LW_OUT', 'VPD':'VPD_F', 'RH':'RH_F',
            'PRECIP':'P_F', 'TA':'TA_F', 'RE':'RECO', 'FC_flag':'FC_F_FLAG'}, 
            inplace=True)

    else:
        # Use ISO date parse
        parsed_df =  pd.read_csv( fname, skiprows=( 0,1,2,4 ), header=0,
                parse_dates={ 'Date': [0] },
                na_values='-9999', index_col='Date' )


    # We will reindex to include every 30-min period during the given year,
    # from YR-01-01 00:30 to YR+1-01-01 00:00
    full_idx = pd.date_range( str( year ) + '-01-01 00:30:00',
            str( year + 1 ) + '-01-01 00:00:00', freq = '30T')

    # Remove irregular data and reindex dataframes
    idxyrs = parsed_df.index.year > 2005;
    parsed_df = parsed_df.iloc[ idxyrs, : ]
    if len( parsed_df.index ) < len( full_idx ):
        print( "WARNING: some observations may be missing!" )
    
    parsed_df = parsed_df.reindex( full_idx )
    
    return parsed_df


def get_multiyr_aflx( site, afpath,
                      startyear=now.year - 1, endyear=now.year - 1,
                      gapfilled=True) :
    """
    Load a list of 1-year ameriflux files, append them, and then return
    a pandas DataFrame object of AF data from startyear to endyear.

    Args:
        site        : Site name ( Ameriflux style )
        afpath      : Path to directory of ameriflux files
        startyear   : First year of data to include
        endyear     : Last year of data to include
        gapfilled   : Boolean, true=with_gaps, false=gapfilled files parsed

    Return:
        site_df     : pandas DataFrame containing multiple years of AF data
                      from one site
    """
    
    if gapfilled:
        file_gap_type = 'gapfilled'
    else:
        file_gap_type = 'with_gaps'
    
    # Create empty dataframe spanning all days in  startyear to endyear
    newidx = pd.date_range( str( startyear ) + '-01-01 00:30:00',
            str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')
    df = pd.DataFrame( index = newidx )
    
    # Get a list of filenames in the directory
    file_list = os.listdir( afpath )

    # Select desired files from file_list (by site and gapfilling)
    site_file_list = [ s for s in file_list if site in s ]
    site_file_list = [ s for s in site_file_list if file_gap_type in s ]
    # Initialize DataFrame
    site_df = pd.DataFrame()
    # Loop through each year and fill the dataframe
    for j in range(startyear, endyear + 1):
        fName = '{0}_{1}_{2}.txt'.format( site, j, file_gap_type )
        # If theres is a file for that year, load it
        if fName in site_file_list:
            # Call load_aflx_file
            year_df = load_aflx_file( afpath + fName, j )
            # And append to site_df
            site_df = site_df.append( year_df )
        else:
            print( 'WARNING: ' + fName + ' is missing')

    # Now standardize the time period and index of site_df and put
    # multiyear site flux values in measurement-specific dataframe
    idxyrs = site_df.index.year > startyear - 1;
    site_df = site_df.iloc[ idxyrs, : ]
    site_df = site_df.reindex( newidx )

    return site_df


def get_multisite_aflx_var( varname, sites, afpath,
                            startyear=now.year - 1, endyear=now.year - 1,
                            gapfilled=True ):
    """
    Load ameriflux files for a list of sites, append them, select out a
    desired variable and then return a pandas DataFrame object of one AF
    variable with columns for each site in list from startyear to endyear.

    Args:
        varname     : Desired Ameriflux variable
        sites       : List of site names ( Ameriflux style )
        afpath      : Path to directory of ameriflux files
        startyear   : First year of data to include
        endyear     : Last year of data to include
        gapfilled   : Boolean, true=with_gaps, false=gapfilled files parsed

    Return:
        site_df     : pandas DataFrame containing multiple years of AF data
                      from one site
    """
    
    # Create empty dataframe spanning startyear to endyear
    # Will contain the multi-year column for each site
    newidx = pd.date_range(str(startyear) + '-01-01',
                           str(endyear + 1) + '-01-01', freq = '30T')
    df = pd.DataFrame(index = newidx)
    
    # List AF site names in same order
    siteNames = sites
    for i, site in enumerate(siteNames):
        # Get the multi-year Ameriflux data for the site
        site_df = get_multiyr_aflx( site, afpath, gapfilled, 
                                    startyear, endyear )
        df[ site ] = site_df[ varname ]

    return df


def loadPRISMfile(fname) :
    """
    Load a daily PRISM data file (found in ancillary_met_data file)
    
    Args:
        fname (str) : the full file path and name

    Return:
        df : pandas data frame 
    """       
        
    return pd.read_csv(fname, header=0,
            parse_dates = True, index_col='date');

    
def load_PJ_VWC_file(fname) :
    """
    Load a daily VWC data file (made by Laura)
    
    Args:
        fname (str) : the full file path and name

    Return:
        df : pandas data frame 
    """       
        
    return pd.read_csv(fname, header=0,
            parse_dates = [['year','month','mday']],
            index_col=2,na_values='NA');    


def add_WY_cols( df ) :
    """
    Add water year columns
    
    Args:
        df (obj) : a pandas Data.Frame object with a timeseries index

    Return:
        df_wy (obj) : a copy of df with water year columns added 
    """
    df_wy = df.copy()
    # Add water year columns
    wy = df.index + dt.timedelta(days=61) #61 = Nov 1st, 91 = Oct 1st wy start
    df_wy['year_w'] = wy.year
    df_wy['doy_w'] = wy.dayofyear
    # Add hydrologic season columns
    df_wy['season'] = 'Null'
    df_wy.season[(df_wy.index.month > 10) | (df_wy.index.month < 3)] = 'cold'
    df_wy.season[(df_wy.index.month > 2) & (df_wy.index.month < 7)] = 'spring'
    df_wy.season[(df_wy.index.month > 6) & (df_wy.index.month < 11)] = 'monsoon'

    return df_wy
