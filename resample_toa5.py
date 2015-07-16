'''
A script for resampling 5 minute JSav TOA5 files to 30 minute files. and
have 5 minute frequency timestamps. 

This script depends on the NMEG_utils repository found on Greg Maurer's
github. You will need to ensure that this repository is accessable and the
correct path is added by python (edit line 19 of the script as appropriate).

Then:

1. Navigate to this directory in a terminal.
2. Run the 'resample_toa5'script (type 'python resample_toa5.py')
3. Copy the resampled files in ./resampled_toa5 to the parent directory
    ( /JSav/toa5 )
'''

import sys, os
# append the path to the NMEG_utils repository (greg's github)
sys.path.append(r'C:\Users\greg\Documents\GitHub\NMEG_utils\py_modules')

import load_nmeg as ld

data_path = r'C:\Research_Flux_Towers\Flux_Tower_Data_by_Site' \
        r'\JSav\toa5\5min_toa5_files'

output_path = data_path + '\\' + 'resampled_toa5'

file_list = os.listdir(data_path)
files = [ f for f in file_list if 'TOA5_' in f ]

for i, fname in enumerate(files):
    # Open the old file and create a new (resampled) file
    old_fname =  data_path + '\\' + fname
    new_fname =  output_path + '\\' + fname
    oldf = open( old_fname, 'r')
    newf = open(new_fname, 'w')
    # Copy over the first four header lines from old to new files
    for j in range(0, 4):
        line = oldf.readline()
        newf.write(line)
    # Close files
    newf.close()
    oldf.close()
    # Now load data from old file and resample columns
    data = ld.load_toa5_file( old_fname )
    rain = data.rain_Tot
    rain_T = rain.resample('30min', how='sum', label='right')
    data_T = data.resample('30min', how='mean', label='right')
    # Now replace avg rain with summed rain in the new 30min dataframe
    data_T.rain_Tot = rain_T.values
    # Append resampled data to new file
    with open( new_fname, 'a' ) as f:
        data_T.to_csv( f, header=False, index=True, na_rep='NaN', 
                date_format='"%Y-%m-%d %H:%M:%S"')
