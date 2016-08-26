import gdal
import gdalconst
import pandas as pd
import pdb

class BilFile(object):
# This is the class used to open a .bil file and make georeferenced data
# available. Raster values for a coordinate are extracted using the 
# extract_coord_val method

    def __init__(self, bil_file):
        # Construct the BilFile object and initialize its
        # properties
        self.bil_file = bil_file
        self.hdr_file = bil_file.split('.')[0]+'.hdr'
        # Register EHdr driver needed for these files - automatic in python?
        # gdal.GetDriverByName('EHdr').Register()
        # Open the file and put in dataset
        dataset = gdal.Open(self.bil_file, gdalconst.GA_ReadOnly)
        band = dataset.GetRasterBand(1)
        self.ncol = dataset.RasterXSize
        self.nrow = dataset.RasterYSize
        # Get georeferencing information and assign to object
        # properties
        geotransform = dataset.GetGeoTransform()
        self.originX = geotransform[0]
        self.originY = geotransform[3]
        self.pixelWidth = geotransform[1]
        self.pixelHeight = geotransform[5]
        self.data = band.ReadAsArray()

    def extract_coord_val(self, lat, lon):
        # Method for extracting raster values at given coordinates
        y = int((lat - self.originY)/self.pixelHeight)
        x = int((lon - self.originX)/self.pixelWidth)
        return self.data[y, x]

# Function for extracting daily PRISM data
def getDailyPrism(year, metdata, data_path, coords_file):
    # Read in site coordinates, get date range and create a DataFrame
    #to fill
    pnts = pd.read_csv(coords_file)
    drange =  pd.date_range('1-1-{0}'.format(year),
            '12-31-{0}'.format(year), freq='D')
    df = pd.DataFrame(index=drange, columns=pnts.sitecode)
    for i in range(len(drange)):
        # Create a tuple to fill the file dates in,
        # pad month & day with zeros
        ymd_tuple = (str(drange.year[i]),
                str(drange.month[i]).zfill(2),
                str(drange.day[i]).zfill(2))
        # Create GDAL vsizip file path (read directly from zip archive)
        # See https://trac.osgeo.org/gdal/wiki/UserDocs/ReadInZip
        # If for some reason this vsizip interface won't work, extract the
        # archive and remove the 'vsizip' part of pathname
        bil_file = (r'/vsizip/' + data_path +
        r'PRISM_{0}_stable_4kmD2_{1}0101_{1}1231_bil.zip/'.format(
            metdata, year) +
        r'PRISM_{0}_stable_4kmD2_{1}{2}{3}_bil.bil'.format(metdata, *ymd_tuple))
        bil_ds = BilFile(bil_file)
        for j in range(len(pnts.index)):
            pt_val = bil_ds.extract_coord_val(pnts.lat[j], pnts.lon[j])
            df.iloc[i, j] = pt_val
    return df

# Function for extracting daily PRISM data from provisional files
def getDailyPrismProvis(year, month, metdata, data_path, bil_name, coords_file):
    # Read in site coordinates, get date range and create a DataFrame
    #to fill
    pnts = pd.read_csv(coords_file)
    drange =  pd.date_range('{0}-1-1'.format(year),
            '{0}-12-31'.format(year), freq='D')
    drange = drange[drange.month==month]
    df = pd.DataFrame(index=drange, columns=pnts.sitecode)
    for i in range(len(drange)):
        # Create a tuple to fill the file dates in,
        # pad month & day with zeros
        ymd_tuple = (str(drange.year[i]),
                str(drange.month[i]).zfill(2),
                str(drange.day[i]).zfill(2))
        # Create GDAL vsizip file path (read directly from zip archive)
        # See https://trac.osgeo.org/gdal/wiki/UserDocs/ReadInZip
        # If for some reason this vsizip interface won't work, extract the
        # archive and remove the 'vsizip' part of pathname
        bil_file = (r'/vsizip/' + data_path + bil_name + '/' +
        r'PRISM_{0}_provisional_4kmD2_{1}{2}{3}_bil.bil'.format(metdata, 
            *ymd_tuple))
        bil_ds = BilFile(bil_file)
        for j in range(len(pnts.index)):
            pt_val = bil_ds.extract_coord_val(pnts.lat[j], pnts.lon[j])
            df.iloc[i, j] = pt_val
    return df


# Function for extracting monthly PRISM data
# Note that this uses 1981-2015 files and will need to be altered if different
# files are used
def getMonthlyPrism( metdata, data_path, coords_file ):
    # Read in site coordinates, get date range and create a DataFrame
    #to fill
    pnts = pd.read_csv(coords_file)
    drange =  pd.date_range('1-1-1981', '9-30-2015', freq='M')
    df = pd.DataFrame(index=drange, columns=pnts.sitecode)
    for i in range(len(drange)):
        # Create a tuple to fill the file dates in,
        # pad month & day with zeros
        ym_tuple = (str(drange.year[i]),
                str(drange.month[i]).zfill(2))
        # Create GDAL vsizip file path (read directly from zip archive)
        # See https://trac.osgeo.org/gdal/wiki/UserDocs/ReadInZip
        # If for some reason this vsizip interface won't work, extract the
        # archive and remove the 'vsizip' part of pathname
        if metdata=='ppt':
            bil_file = (r'/vsizip/' + data_path +
                    r'PRISM_{0}_stable_4kmM3_198101_201509_bil.zip/'.format(
                        metdata) +
                    r'PRISM_{0}_stable_4kmM3_{1}{2}_bil.bil'.format(
                        metdata, *ym_tuple))
        elif metdata=='tmean':
            bil_file = (r'/vsizip/' + data_path +
                    r'PRISM_{0}_stable_4kmM2_198101_201509_bil.zip/'.format(
                        metdata) +
                    r'PRISM_{0}_stable_4kmM2_{1}{2}_bil.bil'.format(
                        metdata, *ym_tuple))

        bil_ds = BilFile(bil_file)
        for j in range(len(pnts.index)):
            pt_val = bil_ds.extract_coord_val(pnts.lat[j], pnts.lon[j])
            df.iloc[i, j] = pt_val
    return df

# Function for extracting monthly PRISM data from provisional files
def getMonthlyPrismProvis(year, metdata, data_path, bil_name, coords_file):
    # Read in site coordinates, get date range and create a DataFrame
    #to fill
    pnts = pd.read_csv(coords_file)
    drange =  pd.date_range('{0}-10-01'.format(year),
            '{0}-12-31'.format(year), freq='M')
    #drange = drange[drange.month==month]
    df = pd.DataFrame(index=drange, columns=pnts.sitecode)
    for i in range(len(drange)):
        # Create a tuple to fill the file dates in,
        # pad month & day with zeros
        ym_tuple = (str(drange.year[i]),
                str(drange.month[i]).zfill(2))
        # Create GDAL vsizip file path (read directly from zip archive)
        # See https://trac.osgeo.org/gdal/wiki/UserDocs/ReadInZip
        # If for some reason this vsizip interface won't work, extract the
        # archive and remove the 'vsizip' part of pathname
        bil_file = (r'/vsizip/' + data_path + bil_name + '/' +
        r'PRISM_{0}_provisional_4kmM2_{1}{2}_bil.bil'.format(metdata, 
            *ym_tuple))
        #pdb.set_trace()
        bil_ds = BilFile(bil_file)
        for j in range(len(pnts.index)):
            pt_val = bil_ds.extract_coord_val(pnts.lat[j], pnts.lon[j])
            df.iloc[i, j] = pt_val
    return df


# Function for extracting 30 year normal PRISM precip data
def get30yrPrismPrecip(data_path, coords_file):
    # Read in site coordinates, get date range and create a DataFrame
    #to fill
    pnts = pd.read_csv(coords_file)
    df = pd.DataFrame(index=pnts.sitecode, columns=['30yr_ppt'])

    bil_file = (data_path  +
            r'PRISM_ppt_30yr_normal_800mM2_annual_bil.bil')
    bil_ds = BilFile(bil_file)
    for j in range(len(pnts.index)):
        precip = bil_ds.extract_coord_val(pnts.lat[j], pnts.lon[j])
        df.loc[pnts.sitecode[j], '30yr_ppt'] = precip
    return df

