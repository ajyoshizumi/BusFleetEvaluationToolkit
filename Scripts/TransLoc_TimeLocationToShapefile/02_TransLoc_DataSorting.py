#---------------------------------------
# TransLoc_DataSorting.py
# Last Updated: 12 January 2019
# Author: Alexander Yoshizumi
#
# Organizes data collected from TransLoc's API by bus ID and day. For example,
# if the data collected had 10 unique bus IDs and was collected across 7 days,
# this python script would reorganize the data into 70 unique CSV files. Each 
# CSV file would then correspond to a single bus ID for a given day.
#
# Written for Python 3.6.5
#---------------------------------------

# "pandas" allows for tabular data to be imported and processed as a dataframe
# "os" allows for the creation of new file directories
import pandas, os

# Create two directories to hold data organized by date and by vehicle+date
try:
    os.makedirs(name=os.path.join('..','..','Data','Data_By_Date'))
    print('Directory ','"','Data_By_Date','"',' created')
except:
    print('Directory ','"','Data_By_Date','"',' already exists')
try:
    os.makedirs(name=os.path.join('..','..','Data','Data_By_DateVehicle'))
    print('Directory ','"','Data_By_DateVehicle','"',' created')
except:
    print('Directory ','"','Data_By_DateVehicle','"',' already exists')

# Provide and save the name of the file that contains time-location data to an object
filename = '2018-10-30_TimeLocationData.csv'

# Read in the time-location data as a dataframe
df = pandas.read_csv(os.path.join('..','..','Data','PrimaryData',filename))

# Add new column for organizing by date
df.insert(loc=1,column='collection_date',value='')
df['collection_date'] = df.generated_on.str[0:10]

# Save unique dates out to an object
dateArray = df['collection_date'].unique()

# Create new csv files by filtering by date
for date in dateArray:
    dateMask = df['collection_date'] == date
    dfDate = df[dateMask]
    dfDate.to_csv(os.path.join('..','..','Data','Data_By_Date',str(date)+'_Data.csv'))

# Create new csv files by filtering by date and bus
for date in dateArray:
    dateMask = df['collection_date'] == date
    dfDate = df[dateMask]
    # For a given date, save unique vehicle IDs out to an object
    vehicleArray = dfDate['vehicle_id'].unique()
    # Now filter specifically through unique vehicle IDs
    for vehicle in vehicleArray:
        vehicleMask = dfDate['vehicle_id'] == vehicle
        dfDateVehicle = dfDate[vehicleMask]
        dfDateVehicle.to_csv(os.path.join('..','..','Data','Data_By_DateVehicle',str(date)+'_'+str(vehicle)+'_Data.csv'))