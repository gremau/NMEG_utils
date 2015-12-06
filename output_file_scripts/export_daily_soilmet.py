"""
    export_daily_soilmet.py
    -----------------------

    Script to create and export daily NMEG soilmet files for use in R 
    (or elsewhere). Similar to export_daily_aflx.py.
    
"""
import sys
# laptop
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
import load_nmeg as ld
import transform_nmeg as tr
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import pdb as pdb

sm_path = '/home/greg/sftp/eddyflux/Soil_files/provisional/'
outpath = '/home/greg/current/NMEG_utils/processed_data/daily_soilmet/'


# Years to load
startyr = 2007
endyr = 2014
# Sites to load
sites = ['Seg', 'Ses', 'Wjs', 'Mpj', 'Vcp', 'Vcm']
altsites = ['GLand', 'SLand', 'JSav', 'PJ', 'PPine', 'MCon']

# Fill a dict with multiyear dataframes for each site in sites
hourly = { x : 
        ld.get_multiyr_soilmet( x, sm_path, ext='qc_rbd',
            startyear=startyr, endyear=endyr) 
        for x in altsites }


# Resample to daily means
daily = { x : hourly[x].resample( '1D', how='mean' )
        for x in hourly.keys() }

# Replace alternate sitenames with ameriflux style names
for i, asite in enumerate(altsites):
    daily[sites[i]] = daily.pop(asite)

# Add a deep soil moisture column ( mean of all columns <= 20cm deep)
# Also interpolate over missing values

for i, site in enumerate(sites):
    cols = [s for s in daily[site].columns if 'SWC' in s
            and 'tcor' not in s]
    # Choose a range for deep sensors and extract deep sensor column names
    deep = list(range(20,65))
    deep = [str(i) for i in deep]
    deep_cols = list()
    for j in deep:
        j_list = [m for m in cols if j in m]
        deep_cols = j_list + deep_cols
    
    # Calculate a deep SWC mean and interpolate over gaps
    daily[site]['deep_swc'] = daily[site][deep_cols].mean(axis=1, skipna=True)
    # Remove some bad data
    if site=='Seg':
        daily[site].deep_swc[daily[site].index.year < 2010] = np.nan
    if site=='Ses':
        daily[site].deep_swc[daily[site].index==dt.datetime(2011, 5, 23)
                ] = np.nan
        idx = daily[site].index < dt.datetime(2011, 5, 23)
        daily[site].deep_swc[idx] = daily[site].deep_swc[idx] - 0.04
        
    daily[site]['deep_swc_interp'] = daily[site].deep_swc.interpolate(
            method='pchip')
    daily[site].deep_swc.plot(title=site, legend=True)
    daily[site].deep_swc_interp.plot(legend=True)
    plt.show()


# Add ET, PET and put into daily dataframes
#for i, site in enumerate(sites):
#    h = hourly[site]
    # Calculate daily ET and PET (see NMEG_utils/py_modules/transform_nmeg 
    # for documentation)
#    daily_et_pet = tr.get_daytime_et_pet( h, freq='1D')
#    daily[site][ 'ET_F_mm_daytime'] = daily_et_pet.ET_mm_daytime
#    daily[site][ 'PET_F_mm_daytime'] = daily_et_pet.PET_mm_daytime

# Write files to outpath
{ x : daily[x].to_csv(outpath + 'US-' +x + '_daily_soilmet.csv') for x in sites}

