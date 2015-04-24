# load_nmeg.py
# Greg Maurer

""" 
Functions for loading various hidden canyon data files
"""

import numpy as np
import ipdb as ipdb
import datetime as dt
import pandas as pd
import os

now = dt.datetime.now()


def load_aflx_file( fname, year ) :
    """
    Read files downloaded from MesoWest in specified path, return a list 
    holding 2 numpy arrays.
    
    Args:
        stn (str) : station id desired (make sure files are in rawdata dir)
        year (int): wateryear desired

    Return:
        list: [array([swe1, swe2, swe3],...), array([date object])] 
    
        array (structured) 0 holds MesoWest data in named columns
        array 1 holds date objects matching data in array 1
    """
    # a date parser for AF files
    def dparse( yr, doy, hhmm ):       
        yr = int( yr )
        # Some files have a line of zeros at the end - hack it
        if yr != year:
            yr = 1955

        hhmm = hhmm.zfill( 4 )
        doy = int( doy )
        return ( dt.datetime( yr - 1, 12, 31 ) + 
                dt.timedelta( days=doy, hours=int( hhmm[ 0:2 ] ),
                    minutes=int( hhmm[2:4] )))
        
    print 'Parsing ' + fname

    parsed_df =  pd.read_csv( fname, skiprows=( 0,1,2,4 ), header=0,
            parse_dates={ 'Date':[ 0, 1, 2 ] }, date_parser=dparse,
            na_values='-9999', index_col='Date' );

    # We will reindex to include every 30-min period during the given year,
    # from YR-01-01 00:30 to YR+1-01-01 00:30
    full_idx = pd.date_range( str( year ) + '-01-01 00:30:00',
            str( year + 1 ) + '-01-01 00:00:00', freq = '30T')

    # Remove irregular data and reindex dataframes
    idxyrs = parsed_df.index.year > 2005;
    parsed_df = parsed_df.iloc[ idxyrs, : ]
    if len( parsed_df.index ) < len( full_idx ):
        print "WARNING: some observations may be missing!"
    
    parsed_df = parsed_df.reindex( full_idx )
    
    return parsed_df

    # Test whether any of the values are -99.9 (nondaily error)
    #nondailytest = np.logical_or(swe1==-99.9, swe2==-99.9, swe3==-99.9) 
    # Stack SWE data and convert to mm
    #swe = np.column_stack((swe1, swe2, swe3))*25.4
    # Create date array using Brighton file
    
def get_multiyr_aflx( site, afpath,
                      startyear=now.year - 1, endyear=now.year - 1,
                      gapfilled=True) :
    """
    site: Site name ( Ameriflux style )
    afpath: Path to directory of ameriflux files
    gaps: Boolean, true=with_gaps, false=gapfilled
    """
    file_list = os.listdir( afpath )

    if gapfilled:
        file_gap_type = 'gapfilled'
    else:
        file_gap_type = 'with_gaps'
    
    # Create empty dataframe spanning all days in  startyear to endyear
    newidx = pd.date_range( str( startyear ) + '-01-01 00:30:00',
            str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')
    df = pd.DataFrame( index = newidx )
    
    # Get the gapfilled files for each site in the folder and an
    # indexed dataframe
    site_file_list = [ s for s in file_list if site in s ]
    site_file_list = [ s for s in site_file_list if file_gap_type in s ]
    site_df = pd.DataFrame()
    # Loop through each year and fill the dataframe
    for j in range(startyear, endyear + 1):
        fName = '{0}_{1}_{2}.txt'.format( site, j, file_gap_type )
        # If theres is a file for that year, load it
        if fName in site_file_list:
            year_df = load_aflx_file( afpath + fName, j )
            # And append to site_df
            site_df = site_df.append( year_df )

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
    Get a dataframe with one variable from multiple sites for (if desired)
    multiple years
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

    # Test whether any of the values are -99.9 (nondaily error)
    #nondailytest = np.logical_or(swe1==-99.9, swe2==-99.9, swe3==-99.9) 
    # Stack SWE data and convert to mm
    #swe = np.column_stack((swe1, swe2, swe3))*25.4
    # Create date array using Brighton file

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
