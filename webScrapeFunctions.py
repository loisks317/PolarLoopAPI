# webScrapeFunctions.py
#
# use Selenium to get the useful bits from the Polar Flow website
#
# LKS, June 2016, Part of the Inisght Data Science Program
#
import numpy as np
from selenium import webdriver
import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import datetime

# after first login this flips to True and you don't need to keep logging in 
#loginGlobal=False
ffprofile = webdriver.FirefoxProfile()
adblockfile='/Users/loisks/Desktop/Old Firefox Data/4fo05kgu.default/extensions/adblockultimate@adblockultimate.net.xpi'
ffprofile.add_extension(adblockfile)
ffprofile.set_preference("extensions.adblockplus.currentVersion", "4")
wd = webdriver.Firefox(ffprofile) #for debugging
#wd= webdriver.PhantomJS(executable_path='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs') # for silent displays

def loginOnce(username, password):      
      loginURL='https://flow.polar.com/login'
      wd.get(loginURL)
      time.sleep(2) # empricallly 2 seconds worked well, this can be adjusted
      username = wd.find_element_by_id("email")
      password = wd.find_element_by_id("password")

      #
      # put in your own login information!
      username.send_keys(username)
      password.send_keys(password)
      
      wd.find_element_by_id("login").click()
      time.sleep(2)
      loginGlobal=True # flips to true
      print( "Successful Login" ) 
      return None

def getTrackerData(inURL):
      # inURL = url with appropriate date attached
      # returns: a dictionary with Steps, ActiveTime, Distance, Calories, SleepTotal, GoodSleep
      parameters=['Steps', 'ActiveTime', 'Distance', 'Calories', 'SleepTotal', 'GoodSleep']
      dataDicts={}
      #
      # login if you haven't already
      loginOnce()

      # get the appropriate page of data    
      wd.get(inURL)
      time.sleep(2)
      #
      # we are interested in steps, total active time, distance, calories,
      # amount of sleep, and amount of good sleep (percentage)
      
      StepsElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[2]/span[1]'
      ActiveTimeElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[1]/span[1]'
      #ActivityPercentageElement='//*[@id="slider-activity-goal"]/div/div[2]/div[1]/div[2]/div/div/div[2]'
      DistanceElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[3]/span[1]'
      CaloriesElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[4]/span[1]'
      AmountSleepElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[6]/span[1]'
      AmountGoodSleepElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[7]/span[1]'
      ElementArray=[StepsElement,ActiveTimeElement,DistanceElement,CaloriesElement,AmountSleepElement, AmountGoodSleepElement]

      for iElem in range(len(parameters)):
          try:
              dataDicts[iElem]= wd.find_elements_by_xpath(ElementArray[iElem])[0].text
          except:
              if iElem==4 or iElem==1:
                  dataDicts[iElem]='0 hours 0 minutes' # a nan of sorts
              else:
                    dataDicts[iElem]=0

      # return the dictionary, which is a dictionary to account for the strings
      return dataDicts 


def getWeatherData(date, location):
    #  date = date for consideration, in python datetime
    #  location = string for location
    #
    # use weather underground for historical data
    wlink='https://www.wunderground.com/history/'
    #
    # go there 
    wd.get(wlink)
    #
    # put in the location
    #
    # select the appropriate date
    selectMonth = Select(wd.find_element_by_xpath('//*[@id="trip"]/div[3]/select[1]'))
    selectMonth.select_by_visible_text(datetime.datetime.strftime(date, '%B'))
    selectDay = Select(wd.find_element_by_xpath('//*[@id="trip"]/div[3]/select[2]'))
    selectDay.select_by_visible_text(str(date.day))
    selectYear = Select(wd.find_element_by_xpath('//*[@id="trip"]/div[3]/select[3]'))
    selectYear.select_by_visible_text(str(date.year))
    #
    #
    site = wd.find_element_by_id("histSearch")
    site.send_keys(location)

    # FIX THIS I DONT LIKE IT! 
    try:
        pleaseClick=wd.find_element_by_id("autocomplete_item_template")
        pleaseClick.click()
    except:
      try:
         pleaseClick=wd.find_element_by_id("wuSearch")
         pleaseClick.click()       
      except:
        pleaseClick=wd.find_element_by_id("history-station-search-row")
        pleaseClick.click()
        pleaseClick.click()
    
       
    wd.find_element_by_xpath('//*[@id="trip"]/input[5]').click()
    time.sleep(1)
    
    #
    # now collect the appropriate data
    # note mean Temperature is in F
    try:
          meanTemperature=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[2]/td[2]/span/span[1]').text)
    
          maxTemperature=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[3]/td[2]/span/span[1]').text)
          minTemperature=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[4]/td[2]/span/span[1]').text)
    
    except: # make sure this is always true, will manifest as 1e-31 (AKA nans)
          meanTemperature=1e-31
          maxTemperature=1e-31
          minTemperature=1e-31
    try:
          precipitation=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[13]/td[2]/span/span[1]').text)
    except:
          try: # incase it's garbage again
                precipitation=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[14]/td[2]/span/span[1]').text)
          except:
                precipitation=1e-31
    try:
          wind=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[17]/td[2]/span/span[1]').text)
    except:
          try:
                wind=float(wd.find_element_by_xpath('//*[@id="historyTable"]/tbody/tr[18]/td[2]/span/span[1]').text)
          except:
                wind=1e-31
    #
    # awesome now return the data
    return([meanTemperature, maxTemperature, minTemperature, precipitation, wind])

