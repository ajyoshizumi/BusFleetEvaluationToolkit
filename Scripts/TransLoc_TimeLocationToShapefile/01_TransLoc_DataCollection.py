#---------------------------------------
# TransLoc_DataCollection.py
# Last Updated: 12 January 2019
# Author: Alexander Yoshizumi
#
# Collects real-time time-location bus data from TransLoc's API and stores the
# data in a CSV file.
#
# Written for Python 3.6.5
#---------------------------------------

# "requests" interfaces with the API
# "time" provides a variety of time-related functions
# "os" allows for the creation of new file directories
import requests, time, os

# Create a data directory if none exists
try:
    os.makedirs(name=os.path.join('..','..','Data'))
    print('Directory "Data" created')
except:
    print('Directory "Data" already exists')
    
# Create a directory specifically for primary data collection if none exists
try:
    os.makedirs(name=os.path.join('..','..','Data','PrimaryData'))
    print('Directory "PrimaryData" created')
except:
    print('Directory "PrimaryData" already exists')

# Save API key to object
# An API key can be aquired from https://market.mashape.com/
APIkey = {'X-Mashape-Key': [API Key Goes Here]}

# Parameters for accessing the TransLoc API | https://transloc-api-1-2.p.mashape.com/vehicles.{format}
vehiclesURL = 'https://transloc-api-1-2.p.mashape.com/vehicles.json'
# 12: Triangle Transit (TTA)
agency = ('12')
# agencyParam establishes from which transportation agencies the code is pulling data
agencyParam = {'agencies':agency}
# callbackParam acts as the callback function name for JSONP
callbackParam = {'callback':'call'}

# Joining relevant parameters into single object
parameters = agencyParam.copy()
parameters.update(callbackParam)

# Establishing a cycle tracker and starting time variable
i = 0
startTime = time.time()

# Number of cycles that we want to perform
numberOfCycles = 86400
# How long in seconds each cycle lasts
cycleLength = 30
    
# Create a CSV - with today's date - that will store the data
todayDate = time.strftime('%Y-%m-%d')
f = open(file = os.path.join('..','..','Data','PrimaryData',todayDate+'_TimeLocationData.csv'),mode = 'w')
f.write('generated_on,standing_capacity,description,seating_capacity,last_updated_on,call_name,speed,vehicle_id,segment_id,passenger_load,route_id,tracking_status,lat,long,heading' + '\n')
f.close()

# Loop that will collect data at a 30-second interval
while i < numberOfCycles:
    # If the current time - the starting time are >= the cycle length * i, then store the new data
    if (time.time()-startTime) >= (cycleLength*i):
        try:
            # Pulling data from the API and converting it from the JSON format to Python script
            r = requests.get(vehiclesURL,params = parameters,headers = APIkey)
            result = r.json()
            # Collect data for each operating bus in a given agency
            for entry in result['data'][agency]:
                    dateTime = result['generated_on'] 
                    standingCapacity = entry['standing_capacity']
                    description = entry['description']
                    seatingCapacity = entry['seating_capacity']
                    lastUpdated = entry['last_updated_on']
                    callName = entry['call_name']
                    speed = entry['speed']
                    vehicleID = entry['vehicle_id']
                    segmentID = entry['segment_id']
                    passengerLoad = entry['passenger_load']
                    routeID = entry['route_id']
                    trackingStatus = entry['tracking_status']
                    lat = entry['location']['lat']
                    lng = entry['location']['lng']
                    heading = entry['heading']
                    # Concatenate data into a list
                    dataList = [dateTime,standingCapacity,description,seatingCapacity,lastUpdated,callName,speed,vehicleID,segmentID,passengerLoad,routeID,trackingStatus,lat,lng,heading]
                    # Clean list for storage in CSV file
                    dataString = str(dataList)
                    dataString = dataString.replace("[","")
                    dataString = dataString.replace("]","")
                    dataString = dataString.replace("'","")
                    dataString = dataString.replace(" ","")
                    # append data to our CSV file
                    f = open(file = os.path.join('..','..','Data','PrimaryData',todayDate + '_TimeLocationData.csv'),mode = 'a')
                    f.write(dataString + '\n')
                    f.close()
        except:
            # Print error time and store error time in the CSV file
            print('Error: ' + time.strftime('%Y-%m-%dT%H:%M:%S+00:00',time.gmtime()) + ' | ' + 'Cycle:' + str(i))
            f = open(file = os.path.join('..','..','Data','PrimaryData',todayDate + '_TimeLocationData.csv'),mode = 'a')
            f.write(time.strftime('%Y-%m-%dT%H:%M:%S+00:00',time.gmtime())+',NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData,NoData' + '\n')
            f.close()
    else:
            continue
    i += 1
print('Data acquisition complete')
