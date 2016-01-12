
# Append the path where bilParser.py lives, then import
import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
import bilParser as bf
# import other packages
import matplotlib.pyplot as plt
import pandas as pd

'''
This script reads prism bil files in the './PRISM_daily' directory.
From each bil file it extracts a precipitation value for each
of the locations specified in 'site_coords.txt'

Currently this only works from python 3.3 environment in anaconda. So,
to run the script do 'activate py33'
'''

def getPrecipData(year, data_path):
    # Read in site coordinates, get date range and create a DataFrame
    #to fill
    pnts = pd.read_csv('../site_coords.txt')
    drange =  pd.date_range('1,1,{0}'.format(year),
            '12,31,{0}'.format(year), freq='D')
    df = pd.DataFrame(index=drange, columns=pnts.sitecode)
    for i in range(len(drange)):
        # Create a tuple to fill the file dates in,
        # pad month & day with zeros
        ymd_tuple = (str(drange.year[i]),
                str(drange.month[i]).zfill(2),
                str(drange.day[i]).zfill(2))
        # Create GDAL vsizip file path (read directly from zip archive)
        # Never got this to work in windows - had to extract all files.
        # bil_file = (r'/vsizip/PRISM_daily/' +
        #r'PRISM_ppt_stable_4kmD1_{0}0101_{0}1231_bil.zip/'.format(year) +
        #r'PRISM_ppt_stable_4kmD1_{0}{1}{2}_bil.bil'.format(*ymd_tuple))
        bil_file = (data_path  +
            r'PRISM_ppt_stable_4kmD2_{0}0101_{0}1231_bil/'.format(*ymd_tuple) +
            r'PRISM_ppt_stable_4kmD2_{0}{1}{2}_bil.bil'.format(*ymd_tuple))
        bil_ds = bf.BilFile(bil_file)
        for j in range(len(pnts.index)):
            precip = bil_ds.extract_coord_val(pnts.lat[j], pnts.lon[j])
            df.iloc[i, j] = precip
    return df

# NOTE - Manually change the month in the PRISM_daily directory and
# date range if doing an incomplete year dataset
# (current year to 6 months after)
years = list(range(2005, 2007))
path = r'/home/greg/data/'
make_plot=False
for i in years:
    a = getPrecipData(i, path + r'bil_files/')
    if make_plot:
        a.plot()
        plt.show()

    print(a.sum())
    a.to_csv(path + '/PRISM_DailyPrecip_{0}.csv'.format(i), index_label='date')

#bil_file = os.path.join(r'/vsizip', r'PRISM_daily',
#r'PRISM_ppt_stable_4kmD1_{0}0101_{0}1231_bil.zip/'.format(year),
#r'PRISM_ppt_stable_4kmD1_{0}{1}{2}_bil.bil'.format(*ymd_tuple))
