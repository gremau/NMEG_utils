""" 
Functions for loading various NMEG data files

 load_nmeg.py
 Greg Maurer
"""

import numpy as np
import datetime as dt
import pandas as pd
import os
import pdb as pdb

now = dt.datetime.now()


def load_aflx_file( fname, year, old_date_parse=False ) :
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
    if old_date_parse:
        # Use old date parser
        parsed_df =  pd.read_csv( fname, skiprows=( 0,1,2,4 ), header=0,
                parse_dates={ 'Date':[ 0, 1, 2 ] }, date_parser=dparse1,
                na_values='-9999', index_col='Date' )
        # Rename old columns to new format
        parsed_df.rename(columns={ 
            'FC':'FC_F', 'Rg':'SW_IN_F', 'Rg_out':'SW_OUT', 'LE':'LE_F',
            'Rlong_in':'LW_IN', 'Rlong_out':'LW_OUT', 'VPD':'VPD_F',
            'RH':'RH_F','PRECIP':'P_F', 'TA':'TA_F', 'RE':'RECO',
            'FC_flag':'FC_F_FLAG', 'H':'H_F', 'RNET':'RNET_F'}, 
            inplace=True)

    else:
        # Use ISO date parse
        parsed_df =  pd.read_csv( fname, skiprows=( 0,1,2,3,4,5,7 ), header=0,
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


def load_daily_aflx_file( fname ) :
    """
    Load a specified DAILY ameriflux file and return a pandas DataFrame
    object. DataFrame has a datetime index and has been reindexed to include
    all days in one year.

    Args:
        fname (str) : path and filename of desired AF file
        year (int)  : year of ameriflux file
 
    Return:
        parsed_df   : pandas DataFrame    
    """
    # a date parser for older AF files (2007-2008)
    def dparse1( yr, doy ):       
        yr = int( yr )
        doy = int( doy )
        return ( dt.datetime( yr - 1, 12, 31 ) + 
                dt.timedelta( days=doy, hours=0, minutes=0))
        
    print('Parsing ' + fname)
    # Parse data file 
    parsed_df =  pd.read_csv( fname, skiprows=(1,), header=0, delimiter='\t',
            parse_dates={ 'Date': [0, 1] }, date_parser=dparse1,
            na_values='-9999', index_col='Date' )


    # We will reindex to include every 30-min period during all years,
    # from YR-01-01 00:30 to YR+1-01-01 00:00
    full_idx = pd.date_range( '2007-01-01', '2016-01-01', freq = '1D')

    # Remove irregular data and reindex dataframes
    idxyrs = parsed_df.index.year > 2005;
    parsed_df = parsed_df.iloc[ idxyrs, : ]
    if len( parsed_df.index ) < len( full_idx ):
        print( "WARNING: some observations may be missing!" )
    
    parsed_df = parsed_df.reindex( full_idx )
    
    return parsed_df


def load_local_file( fname, yrtrim=None ) :
    """
    Load greg's local NMEG files and return a pandas DataFrame object.
    These files are derived from NMEG ameriflux files (or similar) on
    socorro using scripts found in "../output_file_scripts/".

    Args:
        fname (str)     : path and filename of desired file
        trim (int list) : optional list of integer years to trim data to
    Return:
        parsed_df   : pandas DataFrame    
    """        
    print('Parsing ' + fname)
    # Parse data file 
    parsed_df =  pd.read_csv( fname, skiprows=range(0,6), header=0,
            delimiter=',', index_col=0, parse_dates=True,
            na_values='NA' )
    
    # If trim years provided, reindex to include every day during the 
    # given years, from YR-01-01  to YR+1-01-01
    if yrtrim:
        full_idx = pd.date_range( str(yrtrim[0])+'-01-01',
                str(yrtrim[1])+'-12-31', freq='1D')
        # Reindex dataframe, removing data outside startyr/endyr
        parsed_df = parsed_df.reindex(full_idx)
        
    return parsed_df


def get_multiyr_aflx( site, afpath,
                      startyear=now.year - 1, endyear=now.year - 1,
                      gapfilled=True, old_dparse=False ) :
    """
    Load a list of 1-year ameriflux files, append them, and then return
    a pandas DataFrame object of AF data from startyear to endyear.

    Args:
        site        : Site name ( Ameriflux style )
        afpath      : Path to directory of ameriflux files
        startyear   : First year of data to include
        endyear     : Last year of data to include
        gapfilled   : Boolean, true=with_gaps, false=gapfilled files parsed
        old_dparse  : Boolean, true=use old AF date parsing, false=new parsing

    Return:
        site_df     : pandas DataFrame containing multiple years of AF data
                      from one site
    """
    
    if gapfilled:
        file_gap_type = 'gapfilled'
    else:
        file_gap_type = 'with_gaps'
        
    # Get a list of filenames in the directory
    file_list = os.listdir( afpath )
    # Select desired files from file_list (by site and gapfilling)
    site_file_list = [ s for s in file_list if site in s ]
    site_file_list = [ s for s in site_file_list if file_gap_type in s ]
    # Initialize DataFrame
    site_df = pd.DataFrame()
    # Loop through each year and fill the dataframe
    empty_yrs = list() # to be filled with years that have no file
    for j in range(startyear, endyear + 1):
        fName = '{0}_{1}_{2}.txt'.format( site, j, file_gap_type )
        # If theres is a file for that year, load it
        if fName in site_file_list:
            # Call load_aflx_file
            year_df = load_aflx_file( afpath + fName, j, 
                    old_date_parse=old_dparse )
            # And append to site_df
            site_df = site_df.append( year_df, verify_integrity=True  )
        else:
            # Add empty year so we can trim data
            empty_yrs.append(j)
            print( 'WARNING: ' + fName + ' is missing')
    # Get non empty years
    #pdb.set_trace()
    non_empty = [x for x in range(startyear, endyear) if x not in empty_yrs]
    if len(non_empty) > 0:
        # Create index spanning all days in min(non_empty) to endyear
        newidx = pd.date_range( str(min(non_empty)) + '-01-01 00:30:00',
                str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')
    else:
        newidx = pd.date_range( str( startyear ) + '-01-01 00:30:00',
                str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')

    # Now standardize the time period and index of site_df
    idxyrs = site_df.index.year > startyear - 1;
    site_df = site_df.iloc[ idxyrs, : ]
    site_df = site_df.reindex( newidx )

    return site_df


def load_fluxall_file( fname, year ) :
    """
    Load a specified fluxall file and return a pandas DataFrame object.
    DataFrame has a datetime index and has been reindexed to include all
    30 minute periods in one year.

    Args:
        fname (str) : path and filename of desired file
        year (int)  : year of file

    Return:
        parsed_df   : pandas DataFrame    
    """
    def dparser( y, m, d, H, M, S ):
        yr = int( y )
        mon = int( m )
        day = int( d )
        hr = int( H )
        mn =  int( M )
        sec = int( S )
        
        return ( dt.datetime( yr, mon, day, hr, mn, sec ))
    
    print('Parsing ' + fname)

    # Use date parser above
    parsed_df =  pd.read_csv(fname, delimiter='\t',
                parse_dates={'tstamp':[0, 1, 2, 3, 4, 5]},
                date_parser=dparser, index_col='tstamp')


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


def get_multiyr_fluxall( site, base_path,
                      startyear=now.year - 1, endyear=now.year - 1 ) :
    """
    Load a list of 1-year fluxall files, append them, and then return
    a pandas DataFrame object of fluxall data from startyear to endyear.

    Args:
        site        : Site name ( NMEG style )
        base_path   : Path to base directory of fluxall files (subdir for sites)
        startyear   : First year of data to include
        endyear     : Last year of data to include

    Return:
        site_df     : pandas DataFrame containing multiple years of data
                      from one site
    """
    dpath = base_path + site + '/'
  
    # Create empty dataframe spanning all days in  startyear to endyear
    newidx = pd.date_range( str( startyear ) + '-01-01 00:30:00',
            str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')
    df = pd.DataFrame( index = newidx )

    # Get a list of filenames in the directory
    file_list = os.listdir( dpath )

    # Select desired files from file_list (by site and filetype)
    site_file_list = [ s for s in file_list if site in s ]
    site_file_list = [ s for s in site_file_list if 'fluxall' in s ]
    # Initialize DataFrame
    site_df = pd.DataFrame()
    # Loop through each year and fill the dataframe
    for j in range(startyear, endyear + 1):
        fName = '{0}_{1}_fluxall.txt'.format( site, j )
        # If theres is a file for that year, load it
        if fName in site_file_list:
            # Call load_fluxall_file
            year_df = load_fluxall_file( dpath + fName, j )
            # And append to site_df
            site_df = site_df.append( year_df, verify_integrity=True  )
        else:
            print( 'WARNING: ' + fName + ' is missing')

    # Now standardize the time period and index of site_df and put
    # multiyear site flux values in measurement-specific dataframe
    idxyrs = site_df.index.year > startyear - 1;
    site_df = site_df.iloc[ idxyrs, : ]
    site_df = site_df.reindex( newidx )

    return site_df


def load_soilmet_qc(fname):
    """
    Load a specified soilmet file and return a pandas DataFrame object.
    DataFrame has a datetime index
    Args:
        fname (str) : path and filename of desired file
        year (int)  : year of file

    Return:
        parsed_df   : pandas DataFrame 
    """
    def dparser( y, m, d, H, M, S ):
        yr = int( y )
        mon = int( m )
        day = int( d )
        hr = int( H )
        mn =  int( M )
        sec = int( S )
        return ( dt.datetime( yr, mon, day, hr, mn, sec ))
    
    print('Parsing ' + fname)

    soilmet_df = pd.read_csv(fname, delimiter=',', 
                parse_dates={'tstamp':[0, 1, 2, 3, 4, 5]},
                date_parser=dparser, index_col='tstamp')

    return(soilmet_df)


def get_multiyr_soilmet(site, base_path, ext='qc',
        startyear=now.year - 1, endyear=now.year ) :
    """
    Load a list of 1-year soilmet files, append them, and then return
    a pandas DataFrame object of soilmet data from startyear to endyear.

    Args:
        site        : Site name ( NMEG style )
        base_path   : Path to base directory of fluxall files (subdir for sites)
        ext         : File type ('qc', 'qc_rbd', or 'qc_rbd_gf')
        startyear   : First year of data to include
        endyear     : Last year of data to include

    Return:
        site_df     : pandas DataFrame containing multiple years of data
                      from one site
    """

    # dpath = base_path + site + '/'
    # Create empty dataframe spanning all days in  startyear to endyear
    newidx = pd.date_range( str( startyear ) + '-01-01 00:30:00',
            str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')

    # Get a list of filenames in the directory
    file_list = os.listdir( base_path )

    # Select desired files from file_list (by site and filetype)
    site_file_list = [ s for s in file_list if site in s ]
    filetype = ext + '.txt' # qc, qc_rbd, or qc_rbd_gf
    site_file_list = [ s for s in site_file_list if filetype in s ]

    # Initialize DataFrame
    site_df = pd.DataFrame()
    # Loop through each year and fill the dataframe
    for j in range(startyear, endyear + 1):
        fName = '{0}_{1}_soilmet_{2}.txt'.format( site, j, ext )
        # If theres is a file for that year, load it
        if fName in site_file_list:
            # Call load_soilmet_file
            year_df = load_soilmet_qc( base_path + fName )
            # And append to site_df
            site_df = site_df.append( year_df, verify_integrity=True )
        else:
            print( 'WARNING: ' + fName + ' is missing')

    # Now standardize the time period and index of site_df
    idxyrs = site_df.index.year > startyear - 1;
    site_df = site_df.iloc[ idxyrs, : ]
    site_df = site_df.reindex( newidx )

    return site_df


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


def load_toa5_file(fname) :
    """
    Load a toa5 data file (raw ascii datalogger files)
    
    Args:
        fname (str) : the full file path and name

    Return:
        df : pandas data frame 
    """       
        
    return pd.read_csv(fname, skiprows=( 0,2,3 ), header=0,
            parse_dates = { 'Date': ['TIMESTAMP']}, index_col='Date',
            na_values=['NaN', 'NAN', 'INF', '-INF']);


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

def load_eddyproc_output( fname, year ) :
    """
    Load a specified eddyproc file and return a pandas DataFrame object.
    DataFrame has a datetime index and has been reindexed to include all
    30 minute periods in one year.

    Args:
        fname (str) : path and filename of desired AF file
        year (int)  : year of ameriflux file

    Return:
        parsed_df   : pandas DataFrame    
    """
    # a date parser for older AF files (2007-2008)
    def dparseMPI( d, m, y, H, M ):       
        # MPI eddyproc sends back a crazy date format. Make a dataframe
        # and then parse into a datetime
        df = pd.DataFrame( dict(y = y.astype(float).astype(int), 
                m = m.astype(float).astype(int),
                d = d.astype(float).astype(int), 
                H = H.astype(float).astype(int),
                M = M.astype(float).astype(int)))
        return pd.to_datetime( df.y*100000000 + df.m*1000000 + df.d*10000 
                + df.H*100 + df.M, format='%Y%m%d%H%M')


    print('Parsing ' + fname)
    parsed_df =  pd.read_csv( fname, skiprows=(1,), header=0,
            delim_whitespace=True,# OR sep='\s+',
            parse_dates={ 'Date': [ 0, 1, 2, 3, 4 ] }, date_parser=dparseMPI,
            na_values='-9999', index_col='Date')
    
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


def add_eddyproc_uncertainty( df, site, basepath, year, unc_vars=[] ) :
    """
    Add uncertainty columns derived from eddyproc output (these come from the
    Falge 2001 method). This can be done for hourly ameriflux data only.
    
    Args:
        df (obj)    : a pandas Data.Frame object with a timeseries index
        ndays(int)  : an integer number of days to offset wateryear by. 
                      61 days = Nov 1st, 91 days = Oct 1st wy start
    Return:
        df_unc (obj) : a copy of df with uncertainty columns added 
    """
    
    raise NotImplementedError('Not implemented yet!')

    df_unc = df.copy()
    path = basepath + site + '/' + 'DataSetafterFluxpart_' + str(year) + '.txt'


    return df_unc

def get_multiyr_eddyproc( site, base_path, GL2010=False,
                      startyear=now.year - 1, endyear=now.year - 1) :
    """
    Load a list of 1-year eddyproc output files, append them, and then return
    a pandas DataFrame object of eddyproc data from startyear to endyear.

    Args:
        site        : Site name ( Ameriflux style )
        afpath      : Path to directory of ameriflux files
        startyear   : First year of data to include
        endyear     : Last year of data to include

    Return:
        site_df     : pandas DataFrame containing multiple years of eddyproc 
                      data from one site
    """    
    # Create empty dataframe spanning all days in  startyear to endyear
    newidx = pd.date_range( str( startyear ) + '-01-01 00:30:00',
            str( endyear + 1 ) + '-01-01 00:00:00', freq = '30T')
    
    # Get a list of filenames in the directory
    file_list = os.listdir( base_path + site )
    if GL2010:
        file_list2 = [ s for s in file_list if 'GL2010' in s ]
        fName_base = 'DataSetafterFluxpartGL2010'
    else:
        file_list2 = [ s for s in file_list if 'GL2010' not in s ]
        fName_base = 'DataSetafterFluxpart'

    # Initialize DataFrame
    site_df = pd.DataFrame()
    # Loop through each year and fill the dataframe
    for j in range(startyear, endyear + 1):
        fName = fName_base + '_{0}.txt'.format( j )
        # If theres is a file for that year, load it
        if fName in file_list2:
            # Call load_eddyproc_unc
            year_df = load_eddyproc_output( base_path + site + '/' + fName, j )
            # And append to site_df
            site_df = site_df.append( year_df, verify_integrity=True  )
        else:
            print( 'WARNING: ' + fName + ' is missing')

    # Now standardize the time period and index of site_df
    idxyrs = site_df.index.year > startyear - 1;
    site_df = site_df.iloc[ idxyrs, : ]
    site_df = site_df.reindex( newidx )

    return site_df
