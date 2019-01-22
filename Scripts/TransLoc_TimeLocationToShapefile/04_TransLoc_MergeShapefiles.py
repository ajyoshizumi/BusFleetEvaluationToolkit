#---------------------------------------
# TransLoc_MergeShapefiles.py
# Last Updated: 20 January 2019
# Author: Alexander Yoshizumi
#
# Script merges all of the emissions shapefiles into a single shapefile
#
# Written for Python 3.6.5
#---------------------------------------

import geopandas,os

# Create a new directory to hold resulting shapefile
try:
    os.makedirs(name=os.path.join('..','..','Data','MergedShapefiles'))
    print('Directory "MergedShapefiles" created')
except:
    print('Directory "MergedShapefiles" already exists')

# Specify the date of the data that you would like to iterate through using the "YYYY-MM-DD" format
date = '2018-11-01'

# Establish variable object "i" for use in iteration
i = 0

# Iterate through all shapefiles in the "..\\Data\\EmissionsShapefiles" directory with specified date
directory = os.path.join('..','..','Data','Shapefiles')
for filename in os.listdir(path = directory):
    if filename.startswith(date) and filename.endswith(".shp"):
        filepath = os.path.join(directory, filename)
        # If statement to establish geodataframe upon which new data will be appended
        if i == 0:
            gdf = geopandas.read_file(driver = 'ESRI Shapefile', filename = filepath, crs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
            i += 1
        # If statement to append other data to primary geodataframe
        else:
            gdf_addtn = geopandas.read_file(driver = 'ESRI Shapefile', filename = filepath)
            gdf = gdf.append(gdf_addtn,ignore_index=True,verify_integrity=True)
            i += 1
    else:
        continue

# Save merged geodataframe as a shapefile
gdf = geopandas.GeoDataFrame(gdf, crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', geometry='geometry')
gdf.to_file(filename=os.path.join('..','..','Data','MergedShapefiles',date + '_Merge.shp'), driver='ESRI Shapefile')