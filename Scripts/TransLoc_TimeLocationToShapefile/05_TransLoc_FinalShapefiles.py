#---------------------------------------
# TransLoc_FinalShapefiles.py
# Last Updated: 23 January 2019
# Author: Alexander Yoshizumi
#
# Script cleans merged shapefiles and prepares them for use in ArcGIS tool
#
# Written for Python 3.6.5
#---------------------------------------

import geopandas,os

# Create a new directory to hold resulting shapefile
try:
    os.makedirs(name=os.path.join('..','..','Data','FinalShapefiles'))
    print('Directory "FinalShapefiles" created')
except:
    print('Directory "FinalShapefiles" already exists')

# Specify the date of the data that you would like to iterate through using the "YYYY-MM-DD" format
date = '2018-11-01'

# Iterate through all shapefiles in the "..\\Data\\EmissionsShapefiles" directory with specified date
directory = os.path.join('..','..','Data','MergedShapefiles')
for filename in os.listdir(path = directory):
    if filename.startswith(date) and filename.endswith(".shp"):
        filepath = os.path.join(directory, filename)
        # If statement to establish geodataframe upon which new data will be appended
        gdf = geopandas.read_file(driver = 'ESRI Shapefile', filename = filepath, crs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        # Create a miles per hour data column and populate it
        gdf['mph'] = (gdf.length_mi/gdf.timedelta)*(3600/1)
        # If the average velocity of the vehicle exceeds 100 mph, delete the data residing in that row
        gdf = gdf.drop(gdf[gdf.mph > 100].index)
        gdf.reset_index(inplace=True)
    else:
        continue

# Save merged geodataframe as a shapefile
gdf = geopandas.GeoDataFrame(gdf, crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', geometry='geometry')
gdf.to_file(filename=os.path.join('..','..','Data','FinalShapefiles',date + '_Final.shp'), driver='ESRI Shapefile')