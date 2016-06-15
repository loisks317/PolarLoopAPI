# assimilateData.py
#
# gather the Polar Loop data
# user needs to put in their own username and password
#
# LKS, June 2016, Part of the Insight Data Science Program
#
import datetime
import numpy as np
import webScrapeFunctions as WS

# login
# user needs to fill in their own username and password
username=''
password=''

# 
#
# Ann Arbor, US but fill in your own location 
startDate='20160506'
endDate='20160601'
location='48105'
# Ann Arbor, can be zipcode or city name
# weather underground will take either (i.e. Boulder, CO)


# time 
startDt=datetime.datetime.strptime(startDate,'%Y%m%d')
endDt=datetime.datetime.strptime(endDate,'%Y%m%d')
curDt=startDt

# set up data base
import psycopg2
import sys
con = None
con = psycopg2.connect(dbname='postgres', user=username, host='localhost', password=password)
# make it create individual data base
#
# I name the table later data, you may want to change that 
con2 = psycopg2.connect("dbname='activity' user="+username)  
cur=con2.cursor()
#
# set up table
# Table Items are:
# StepsElement,ActiveTimeElement,DistanceElement,\
# CaloriesElement,AmountSleepElement, AmountGoodSleep,meanTemperature, \
# maxTemperature, minTemperature, precipitation, wind
#

curDt = startDt
while curDt != endDt:
#  
    try:
        # build on the data set already there
        cur.execute("SELECT * FROM DATA") # access data currently in data base 
        prevData=cur.fetchall()        
        curDt=prevData[-1][0]+datetime.timedelta(days=1) # datetime object
        
    except: # if there is no data base 
       # cur.execute("DROP TABLE IF EXISTS DATA;")
        cur.execute(" CREATE TABLE DATA (date TIMESTAMP, steps REAL, activeTime REAL,distance REAL, calories REAL, sleep REAL, goodSleep REAL,meanTemperature REAL, maxTemperature REAL, minTemperature REAL, precipitation REAL, wind REAL); ")
        curDt=startDt

    #
    # get the Activity data first
    dateLink=datetime.datetime.strftime(curDt,'%d'+'.'+'%m'+'.'+'%Y')
    url2='https://flow.polar.com/training/day/'+dateLink
    print(curDt)
    activeData=WS.getTrackerData(url2) # returns a dictionary
    print('Acquired Activity Tracker Data')
    weatherData=WS.getWeatherData(curDt, location)  # returns a list
    print('Acquired Weather Data')
    
    #
    # fix the hours string
    temp1=activeData[1]
    tt=temp1.index('h'); mm1=temp1.index('s'); mm2=temp1.index('m')
    hours=int(temp1[0:tt-1]); minutes = int(temp1[mm1+2:mm2-1])
    activeData[1]=hours+(minutes/100.) # hour + decimal fraction

    temp2=activeData[4]
    tt=temp2.index('h'); mm1=temp2.index('s'); mm2=temp2.index('m')
    hours=int(temp2[0:tt-1]); minutes = int(temp2[mm1+2:mm2-1])
    activeData[4]=hours+(minutes/100.) # hour + decimal fraction

    # GET ACTIVITY AND PERCENT SLEEP BETTER

    
    # add directly to data base
    #dateq=datetime.datetime.strftime(curDt, '%Y%m%d')
    query = 'INSERT INTO DATA (DATE,STEPS,ACTIVETIME, DISTANCE, CALORIES, SLEEP, GOODSLEEP, MEANTEMPERATURE, \
    MAXTEMPERATURE, MINTEMPERATURE, PRECIPITATION, WIND) VALUES (%s, %s, %s, %s, \
    %s, %s, %s, %s, %s, %s, %s, %s);'
    data=( curDt, float(activeData[0]), activeData[1], float(activeData[2]), \
           int(activeData[3]), activeData[4], int(activeData[5]), weatherData[0], \
           weatherData[1], weatherData[2], weatherData[3], weatherData[4])
    print data
    cur.execute(query,data)
    con2.commit()
    curDt+=datetime.timedelta(days=1)
    
