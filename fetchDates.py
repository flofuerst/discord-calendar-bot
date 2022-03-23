from cgi import test
from datetime import datetime, timedelta, timezone
from itertools import count
from lib2to3.pytree import convert
from traceback import print_tb
import icalendar
from dateutil.rrule import *
import math

import pytz

icalfile = open('calendar_uni_wichtig.ics', 'rb')
gcal = icalendar.Calendar.from_ical(icalfile.read())
icalfile.close()

savedEntries = []
for component in gcal.walk():
    if component.name == "VEVENT":
        
        summary = component.get('summary')
        description = component.get('description')
        location = component.get('location')
        startdt = component.get('dtstart').dt
        enddt = component.get('dtend').dt
        exdate = component.get('exdate')

        #   compare datetime in calender with current time (date and year) and use only upcoming event-dates
        # print(summary)
        if startdt.strftime("%D") >= datetime.strftime(datetime.today(),"%D") and startdt.strftime("%Y") >= datetime.strftime(datetime.today(),"%Y"): 
            savedEntries.append([startdt.strftime("%D %H:%M"), str(summary)])

#   sort dates
sortedEntries = sorted(savedEntries)

def print_dates(displayDays):
    count = 0
    output = ''
    entry = []
    
    #   iterate through sortedEntries
    while True: 
        #   save originalEntry at index
        originalEntry = sortedEntries[count]

        #   convert string-dates into datetime-dates again
        #   'entry' is used because of iteration (datetime would be converted into datetime (with strptime)
        #   after second iteration --> error)
        timeLeft = datetime.strptime(originalEntry[0], "%m/%d/%y %H:%M") - datetime.today()
        timeLeftSeconds = timeLeft.total_seconds()
        days = math.ceil((timeLeftSeconds/3600)/24)
        
        #   convert datetime to utc timestamp
        local = pytz.timezone('Europe/Vienna')
        naive = datetime.strptime(originalEntry[0], "%m/%d/%y %H:%M")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)

        #   .timestamp() to get unix-timestamp of utc-date for further bot implementation
        utc_timestamp = round(utc_dt.timestamp())

        #   only upcoming dates in the next <displayDays> are getting stored in entry-list
        if days <= displayDays and timeLeftSeconds>=0:
            entry.append([utc_timestamp, originalEntry[1]])

        count +=1

        #   store formatted date for discord + text of event in string for easier output in main.py
        #   add newspace to text if not last element in entry
        if(count == len(sortedEntries)):
            for content in entry:
                text = '<t:'+str(content[0])+':F>' + ' ' + content[1] + ' ' + '<t:'+str(content[0])+':R>'
                output += text+'\n' if content != entry[len(entry)-1] else text
            return output

#   TODO: weekly frequency is not recognized

print_dates(21)