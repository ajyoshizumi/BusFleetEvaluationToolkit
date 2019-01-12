#---------------------------------------
# TransLoc_DateVehicleToShapefile.py
# Last Updated: 12 January 2019
# Author: Alexander Yoshizumi
#
# Script iterates through every CSV file in the directory "..\\Data\\Data_By_DateVehicle".
# For each CSV, the script cleans and applies geometry to the data such that each
# row corresponds to a line segment with a data column "timedelta" that details
# the amount of time that transpired between the beginning of the line segment and
# the end of the line segment.
#
# Written for Python 3.6.5
#---------------------------------------

import pandas,geopandas,os,shapely,geopy.distance

# Create a new directory to hold resulting shapefiles
try:
    os.makedirs(name=os.path.join('..','..','Data','Shapefiles'))
    print('Directory "Shapefiles" created')
except:
    print('Directory "Shapefiles" already exists')

# Specify the date of the data that you would like to iterate through using the "YYYY-MM-DD" format
date = '2018-11-01'

# Iterate through all CSV files in the "..\\Data\\DataVehicle" directory with specified date
directory = os.path.join('..','..','Data','Data_By_DateVehicle')
for filename in os.listdir(path = directory):
    if filename.startswith(date) and filename.endswith(".csv"): 
        filepath = os.path.join(directory, filename)
        
        # Read in the relevant CSV file
        df = pandas.read_csv(filepath_or_buffer = filepath)
        
        # Skip file if it only contains one line of data
        if df.index.max() == 0:
            continue
        
        else:
            # Add new column to change data into a datetime object format
            df.insert(loc=7,column='data_datetime',value='')
            df['data_datetime'] = pandas.to_datetime(df['last_updated_on'])
            
            # Add new column for calculating change in time between data entries
            df.insert(loc=8,column='timedelta',value=int)
            for i in range(1,len(df)):
                timeDelta = df.loc[i,'data_datetime']-df.loc[i-1,'data_datetime']
                df.loc[i,'timedelta'] = timeDelta.total_seconds()
            
            # Remove duplicate rows that have a 'timedelta' equal to 0
            df = df.drop(df[df.timedelta == 0].index)
            
            # Remove the column titled "Unnamed: 0" which corresponds to the index number of the primary data
            df = df.drop(columns=['Unnamed: 0'],axis=1)
            
            # Reset the index so that looping through the data still works
            df.reset_index(inplace=True)
            
            # Remove the old index numbers that got saved to a column feature after using "reset_index"
            # This operation is done for data cleanliness
            df = df.drop(columns=['index'], axis=1)
                
            # If the coordinate point in the current row is the same as in the preceding row, then offset the coordinate value
            # This is done to ensure that line features can be create, as a line cannot be one-dimensional
            # The offset corresponds to a geodesic distance of approximately 2 centimeters
            # For the purpose of calculating emissions, this offset is assumed to be neglible
            for i in range(1,len(df)):
                if df.loc[i,'long'] == df.loc[i-1,'long'] and df.loc[i,'lat'] == df.loc[i-1,'lat']:
                    df.loc[i,'long'] = df.loc[i,'long'] + 0.0000001
                    df.loc[i,'lat'] = df.loc[i,'lat'] + 0.0000001
                else:
                    df.loc[i,'long'] = df.loc[i,'long']
                    df.loc[i,'lat'] = df.loc[i,'lat']
            
            # Create a geodataframe where the geospatial object is the coordinate point for each row
            geometry = [shapely.geometry.Point(xy) for xy in zip(df.long, df.lat)]
            crs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
            gdf = geopandas.GeoDataFrame(df, crs=crs, geometry=geometry)
            
            # Create a new column to hold geospatial line data
            # Iterate through rows creating line data between coordinates in the preceding row and the current row
            gdf['line'] = ''
            for i in range(1,len(df)):
                geom0 = gdf.loc[i-1,'geometry']
                geom1 = gdf.loc[i,'geometry']
                startPoint, endPoint = [(geom0.x, geom0.y), (geom1.x, geom1.y)]
                line = shapely.geometry.LineString([startPoint,endPoint])
                gdf.loc[i,'line'] = line
            
            # Create a new column to hold data on the length of each line segment
            # Iterate through rows calculating distance between coordinates in the preceding row and the current row
            # Note that the default method for distance calculation using geopy.distance.distance() is Karney (2013)
            gdf['length_mi'] = 0.0
            for i in range(1,len(df)):
                geom0 = gdf.loc[i-1,'geometry']
                geom1 = gdf.loc[i,'geometry']
                startPoint, endPoint = [(geom0.y, geom0.x), (geom1.y, geom1.x)]
                length = geopy.distance.distance(startPoint,endPoint).miles
                gdf.loc[i,'length_mi'] = length
            
            # Apply new geometry to the geodataframe
            gdf = geopandas.GeoDataFrame(df, crs=crs, geometry='line')
            
            # Remove the "geometry" data column containing the old geometry point data
            # Remove the "data_datetime" column as datetime64[ns] is not an accepted data type in shapefiles
            gdf = gdf.drop(columns=['geometry','data_datetime'], axis=1)
            
            # Remove the first row of data from the geodataframe
            gdf = gdf.drop(index=0, axis=0)
            
            # Convert data in the "timedelta" column to a float
            # Remove rows in which the "timedelta" exceeds 5 mins
            gdf['timedelta'] = gdf.timedelta.astype(float)
            gdf = gdf[gdf['timedelta'] <= 300]
            
            # Reset the index for data cleanliness
            gdf.reset_index(inplace=True)
            
            # Remove the old index numbers that got saved to a column feature after using "reset_index"
            # This operation is done for data cleanliness
            gdf = gdf.drop(columns=['index'], axis=1)
            
            # Rename data column titles so that they will not exceed the character limit for shapefile attribute field names
            gdf = gdf.rename(columns={'generated_on':'gen_on','collection_date':'clctn_date','standing_capacity':'stand_cap','description':'desc','seating_capacity':'seat_cap','last_updated_on':'lst_update','passenger_load':'psngr_load','tracking_status':'trk_status'})
            
            # Save geodataframe out to a shapefile
            filename = str(gdf['lst_update'][0][0:10]) + '_' + str(gdf['vehicle_id'][0]) + '_Line.shp'
            gdf.to_file(driver = 'ESRI Shapefile', filename = os.path.join('..','..','Data','Shapefiles',filename))
            continue
    else:
        continue
