'''
This script reads prism bil files in the './PRISM_daily' directory.
From each bil file it extracts a precipitation value for each
of the locations specified in 'site_coords.txt'

Currently this only works from python 3.3 environment in anaconda. So,
to run the script do 'activate py33'

Maybe this should probably be rewritten to use fiona for file loading
'''

# Import the bilParser. If it lives in another directory that directory
# must be appended first (Dylan can probably comment out 1st 2 lines here)
import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
import bilParser as bf

# import other packages
import pandas as pd
import pdb

# NOTE - Manually change the month in the PRISM_daily directory and
# date range if doing an incomplete year dataset
# (current year to 6 months after)
years = list(range(2005, 2007))
bil_path = r'/home/greg/Desktop/forDylan/daily_precip_bil/'
out_path = r'/home/greg/Desktop/forDylan/'
site_coords_file = '/home/greg/Desktop/forDylan/site_coords.txt'
make_plot=True

# First extract the daily precip data
for yr in years:
    a = bf.getDailyPrismPrecip(yr, bil_path, site_coords_file)
    if make_plot:
        import matplotlib.pyplot as plt
        a.plot()
        plt.show()

    print(a.sum())
    a.to_csv(out_path + '/PRISM_DailyPrecip_{0}.csv'.format(yr), 
            index_label='date')

# Now change bil_path and extract the 30yr normal precip
bil_path = r'/home/greg/Desktop/forDylan/Annual_Precip_30yr_nrml_800M2/'

b = bf.get30yrPrismPrecip(bil_path, site_coords_file)
b.to_csv(out_path + '/PRISM_30yrPrecip.csv', 
            index_label='date')

