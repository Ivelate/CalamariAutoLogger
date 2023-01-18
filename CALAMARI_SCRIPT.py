from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np 
from datetime import datetime
from tqdm import tqdm
from enum import Enum

class Browser(Enum):
    FIREFOX = 1
    CHROME = 2

########################################################### START OF ARGS, EDIT THIS ###########################################################

EMPLOYEE_ID = None # Get your employee id - its at the end of the calamari timesheet URL. Click on any day of the calamari timesheet and the URL will change, check at the number after the "selemplo" field

startingHour = 10 # AM hour in which you start working
workingHours = 8 # Hours you work
workingMins = 0 # And mins you work

YEAR = 2022 # Year being edited

FILL_PROJECT = False # Also fills the default project you have worked on |TODO if you have more than one project, this might not work

SLEEP_TIME = 5.0 # Seconds waited before each edition, 5 is safe. Don't edit this if you don't know what you're doing

#Put your browser here. For Chrome, that would be webdriver.Chrome() |TODO Chrome doesn't currently work!
browser = Browser.FIREFOX

######################################################### END OF ARGS, DONT TOUCH THIS #########################################################

if EMPLOYEE_ID is None:
	raise RuntimeError("Employee ID needs to be set!")

input("Pressing ENTER will start a puppet browser with Calamari open. Please log in and set your range of timesheet days to \"current year\", then navigate to the year selected in this script YEAR variable, which you can modify as desired. Then come back to this prompt :)")
print("")

if browser == Browser.FIREFOX:
	browser = webdriver.Firefox()
elif browser == Browser.CHROME:
	browser = webdriver.Chrome()
else:
	raise NotImplementedError("Unsupported browser")

browser.get('https://app-new.calamari.io/clockin/timesheet')

input("Press Enter when everything detailed above is done")

browser.get('https://app-new.calamari.io/clockin/timesheet')
time.sleep(SLEEP_TIME)
iframes = browser.find_elements(By.TAG_NAME,'iframe')
browser.switch_to.frame(iframes[0])
days = browser.find_elements("class name",'SmartTable-Content-Row-0')[2].find_elements(By.XPATH, "./*")

days_failed = []
def parse_day(day_num):
	# adjusting day num
	day_num.rjust(3 + len(day_num), '0')
	  
	# Initialize year
	year = str(YEAR)
	  
	# converting to date
	res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%d-%m-%Y")
	return res

for i,d in enumerate(days):
	if "TimesheetTable-div-cell-fail" in d.get_attribute("class").split(" "):
		days_failed.append(parse_day(str(i+1)))

print(days_failed)

def getHourApprox(hour,mins,dev):
    mins = int(hour*60 + mins + np.random.normal(loc = 0.0 , scale= dev))
    hours = mins // 60
    mins = str(mins - hours*60)
    while len(mins) < 2:
    	mins = "0"+mins
    return str(hours)+":"+mins

# Filling all failed days
pbar = tqdm(days_failed)

for date in pbar:

	pbar.set_description(date)

	dates=date.split("-")
	browser.get("https://app-new.calamari.io/clockin/timesheet/create-entry#{%22date%22:%22"+dates[2]+"-"+dates[1]+"-"+dates[0]+"%22,%22employeeId%22:"+str(EMPLOYEE_ID)+"}")
	time.sleep(SLEEP_TIME)

	iframes = browser.find_elements(By.TAG_NAME,'iframe')
	browser.switch_to.frame(iframes[0])

	timeFrom = browser.find_element(By.ID,'timeFromField')
	timeTo = browser.find_element(By.ID,'timeToField')

	if FILL_PROJECT:
		projectButton = browser.find_element("id",'addWorklogEntryButton').click()
		time.sleep(SLEEP_TIME/10)

		timeFrom_2 = browser.find_element(By.ID,'break_fromField_1')
		timeTo_2 = browser.find_element(By.ID,'break_toField_1')

	start_hour = getHourApprox(startingHour,0,5); 
	end_hour = getHourApprox(startingHour+workingHours,workingMins,5)

	timeFrom.send_keys(start_hour)
	timeTo.send_keys(end_hour)
	
	if FILL_PROJECT:
		timeFrom_2.send_keys(start_hour)
		timeTo_2.send_keys(end_hour)

	#Save
	browser.find_element("id",'contextMenu_save').click()
	




	