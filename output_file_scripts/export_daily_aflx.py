"""
    export_daily_aflx.py
    --------------------
    
    Script to create and export daily NMEG datasets for use in R (or elsewhere).
    Combines several older scripts (MultiYearFluxes, MultiYearPrecip, etc)

"""
import sys
# laptop
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
import load_nmeg as ld
import transform_nmeg as tr

af_path = '/home/greg/sftp/eddyflux/Ameriflux_files/provisional/'
outpath = '/home/greg/current/NMEG_utils/processed_data/daily_aflx/'

# Years to load
startyr = 2007
endyr = 2014
# Sites to load
sites = ['Seg', 'Ses', 'Wjs', 'Mpj', 'Vcp', 'Vcm']
# Fill a dict with multiyear dataframes for each site in sites
hourly = { x : 
        ld.get_multiyr_aflx( 'US-' + x, af_path, gapfilled=True,
            startyear=startyr, endyear=endyr) 
        for x in sites }


# Resample to daily sums with integration
daily = { x : 
        tr.resample_30min_aflx( hourly[x], freq='1D', 
            c_fluxes=[ 'GPP', 'RECO', 'FC_F' ],
            le_flux=[ 'LE_F' ], 
            avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET_F', 'VPD_F' ],
            sum_cols=['P_F'] , tair_col='TA_F' ) 
        for x in hourly.keys() }

# Add ET, PET and put into daily dataframes
for i, site in enumerate(sites):
    h = hourly[site]
    # Calculate daily ET and PET (see NMEG_utils/py_modules/transform_nmeg 
    # for documentation)
    daily_et_pet = tr.get_daytime_et_pet( h, freq='1D')
    daily[site][ 'ET_mm_dayint'] = daily_et_pet.ET_mm_dayint
    daily[site][ 'PET_mm_dayint'] = daily_et_pet.PET_mm_dayint

# Write files to outpath
{ x : daily[x].to_csv(outpath + 'US-' +x + '_daily_aflx.csv') for x in sites}

