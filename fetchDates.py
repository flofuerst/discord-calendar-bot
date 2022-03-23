from datetime import datetime, timedelta, timezone
import icalendar
import getDates
from dateutil.rrule import *
import math
import pytz

#   saving dates + recurrent dates from getDates script into sortedEntries
sortedEntries = getDates.recurrent_dates

def print_dates(displayDays):
    count = 0
    output = ''
    entry = []
    
    #   iterate through sortedEntries
    while True: 
        #   save originalEntry at index
        originalEntry = sortedEntries[count]

        #   convert datetime to utc datetime
        local = pytz.timezone('Europe/Vienna')
        naive = datetime.strptime(originalEntry[0].strftime("%D %H:%M"), "%m/%d/%y %H:%M")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        #   converting originalEntry to string and then to date back again because weird timezone problem of new scripts
        #   using .astimezone to convert both dates to Europe/Vienna timezone and therefore to be able to use datetime.now() on webhost, which uses utc timezone
        timeLeft = utc_dt - datetime.now().astimezone(pytz.utc)
        print(datetime.strptime(originalEntry[0].strftime("%D %H:%M"), "%m/%d/%y %H:%M").astimezone(pytz.timezone('Europe/Vienna')), datetime.now().astimezone(pytz.utc))
        print(timeLeft)
        timeLeftSeconds = timeLeft.total_seconds()
        days = math.ceil((timeLeftSeconds/3600)/24)
        
        

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
print_dates(21)