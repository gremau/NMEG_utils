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
import pandas as pd
import datetime as dt

# Name of the data release, set paths
drelease = 'FLUXNET2015_a'

af_path = '/home/greg/sftp/eddyflux/Ameriflux_files/' + drelease + '/'
outpath = '/home/greg/current/NMEG_utils/processed_data/daily_aflx/' + drelease + '/'

# Years to load
startyr = 2007
endyr = 2015
# Sites to load
sites = ['Seg', 'Ses', 'Sen', 'Wjs', 'Mpj', 'Mpg', 'Vcp', 'Vcm']
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
            avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET_F', 'VPD_F', 'PAR',
                'LE_F', 'H_F' ],
            int_cols=['LE_F', 'H_F' ],
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

import subprocess as sp
git_sha = sp.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

for site in sites:
    meta_data = pd.Series([('site: {0}'.format(site)),
        ('date generated: {0}'.format(str(dt.datetime.now()))),
        ('script: export_daily_aflx.py'),
        ('git HEAD SHA: {0}'.format(git_sha)),('--------')])
    with open(outpath + 'US-' + site +
            '_daily_aflx.csv', 'w') as fout:
        fout.write('---file metadata---\n')
        meta_data.to_csv(fout, index=False)
        daily[site].to_csv(fout, na_rep='NA')
