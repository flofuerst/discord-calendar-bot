from datetime import datetime
import getDates
from dateutil.rrule import *
import math
import pytz


def print_dates(displayDays):
    #   saving dates + recurrent dates from getDates script into sortedEntries
    sortedEntries = getDates.updateCalendar()
    count = 0
    output = ''
    entry = []

    #check if no dates to display
    if(sortedEntries == ""):
        return ""
    
    #   iterate through sortedEntries
    while True: 
        #   save originalEntry at index
        originalEntry = sortedEntries[count]

        #   convert datetime to utc datetime
        local = pytz.timezone('Europe/Vienna')
        #   converting originalEntry to string and then to date back again because weird timezone problem of new scripts
        naive = datetime.strptime(originalEntry[0].strftime("%D %H:%M"), "%m/%d/%y %H:%M")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)

        #   substracting utc datetime from utc-now-datetime to get the right 'timeLeft' even while webhosting because webhosts use utc
        timeLeft = utc_dt - datetime.now().astimezone(pytz.utc)
        timeLeftSeconds = timeLeft.total_seconds()
        days = math.ceil((timeLeftSeconds/3600)/24)
        
        

        #   .timestamp() to get unix-timestamp of utc-date for further bot implementation
        utc_timestamp = round(utc_dt.timestamp())

        #   only upcoming dates in the next <displayDays> are getting stored in entry-list
        if days <= displayDays and timeLeftSeconds>=0:
            entry.append([utc_timestamp, originalEntry[1], originalEntry[2]])

        count +=1

        #   store formatted date for discord + text of event in string for easier output in main.py
        #   add newspace to text if not last element in entry
        if(count == len(sortedEntries)):
            return entry


#method-call to test functions
print_dates(21)