'''
This script reads prism bil files in given directories
From each bil file it extracts a met value (ppt, tmean, etc) for each
of the locations specified in 'site_coords.txt'

Currently this only works from python 3 environment in anaconda. It may not
work in windows

Maybe this should be rewritten to use fiona for file loading
'''

# Import the bilParser. If it lives in another directory that directory
# must be appended first

import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
import bilParser as bf

# import other packages
import pandas as pd
import pdb

# NOTE - Manually change the month in the PRISM_daily directory and
# date range if doing an incomplete year dataset
# (current year to 6 months after)
years = list(range(2007, 2017))
site_coords_file = '/home/greg/current/NMEG_utils/site_coords.txt'
make_plot=False


# First extract the daily precip data
out_path = r'/home/greg/sftp/eddyflux/Ancillary_met_data/PRISM_daily/'
bil_path = out_path + 'raw_bil/'
for yr in years:
    a = bf.getDailyPrism(yr, 'ppt', bil_path, site_coords_file)
    if make_plot:
        import matplotlib.pyplot as plt
        a.plot()
        plt.show()

    print(a.sum())
    a.to_csv(out_path + 'PRISM_Daily_ppt_{0}.csv'.format(yr), 
            index_label='date')
pdb.set_trace()
# Code for making provisional files (can be appended to incomplete year data)
#bil_name = 'PRISM_ppt_provisional_4kmD2_20151201_20151231_bil.zip'
#prov = bf.getDailyPrismProvis(2015, 12, 'ppt', bil_path, bil_name, 
#        site_coords_file) 
#prov.to_csv(out_path + 'PRISM_DailyProvis_ppt_Dec2015.csv')


# Then monthly precip and temperature data
out_path = r'/home/greg/sftp/eddyflux/Ancillary_met_data/PRISM_monthly/'
bil_path = out_path + 'raw_bil/'
met_types = ['ppt', 'tmean']
for t in met_types:
    a = bf.getMonthlyPrism( t, bil_path, site_coords_file)
    if make_plot:
        import matplotlib.pyplot as plt
        a.plot()
        plt.show()
    print(a.sum())
    a.to_csv(out_path + 'PRISM_Monthly_{0}_1981_2015.csv'.format(t), 
            index_label='date')


#Code for making provisional files (can be appended to incomplete year data)
bil_name = 'PRISM_tmean_provisional_4kmM2_201510_201603_bil.zip'
prov = bf.getMonthlyPrismProvis(2015, 'tmean', bil_path, bil_name, 
        site_coords_file) 
prov.to_csv(out_path + 'PRISM_MonthlyProvis_tmean_2015.csv')


# Now change bil_path and extract the 30yr normal precip
#bil_path = r'/home/greg/Desktop/forDylan/Annual_Precip_30yr_nrml_800M2/'
#
#b = bf.get30yrPrismPrecip(bil_path, site_coords_file)
#b.to_csv(out_path + '/PRISM_30yrPrecip.csv', 
#            index_label='date')

