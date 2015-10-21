'''
    Script to create and save a bunch of datasets for use in R. Combines
    several older scripts (MultiYearFluxes, MultiYearPrecip, etc)
'''
import sys

# laptop
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
af_path = '/home/greg/sftp/eddyflux/Ameriflux_files/provisional/'
outpath = 'processed_data/'

import load_nmeg as ld
import transform_nmeg as tr


# Years to load
startyr = 2007
endyr = 2014
# Sites to load
sites = ['Seg', 'Ses', 'Wjs', 'Mpj', 'Mpg', 'Vcp', 'Vcm']

# Fill a dict with multiyear dataframes for each site in sites
hourly = { x : 
        ld.get_multiyr_aflx( 'US-' + x, af_path, gapfilled=True,
            startyear=startyr, endyear=endyr) 
        for x in sites }

{ x : hourly[x].to_csv( x + '.csv') for x in sites}

# Resample to daily sums with integration
#daily = { x : 
#        tr.resample_30min_aflx( hourly[x], freq='1D', 
#            c_fluxes=[ 'GPP', 'RECO', 'FC_F' ],
#            le_flux=[ 'LE_F' ], 
#            avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET', 'VPD_F' ],
#            precip_col='P_F' , tair_col='TA_F' ) 
#        for x in hourly.keys() }


