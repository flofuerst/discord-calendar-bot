from cgi import test
from datetime import datetime, timedelta, timezone
from itertools import count
from traceback import print_tb
import icalendar
from dateutil.rrule import *
import math

# def parse_recurrences(recur_rule, start, exclusions):
#     #   Find all reoccuring events
#     rules = rruleset()
#     first_rule = rrulestr(recur_rule, dtstart=start)
#     rules.rrule(first_rule)
#     if not isinstance(exclusions, list):
#         exclusions = [exclusions]
#         for xdate in exclusions:
#             try:
#                 rules.exdate(xdate.dts[0].dt)
#             except AttributeError:
#                 pass

#     #   get current utc time with offset (CET Timezone) 
#     now = datetime.now(timezone.utc) + timedelta(hours=1)
#     this_year = now + timedelta(days=120)
#     dates = []
#     for rule in rules.between(now, this_year):
#         dates.append(rule.strftime("%D %H:%M"))
#     return dates

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
        # if component.get('rrule'):
        #     reoccur = component.get('rrule').to_ical().decode('utf-8')
        #     #   save reocurring dates in list
        #     for date in parse_recurrences(reoccur, startdt, exdate):
        #         savedEntries.append([date, str(summary)])
        # else:
        
        #   save other dates in list

        #   compare datetime in calender with current time (date and year) and use only upcoming event-dates
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
        #   save original Entry at index
        originalEntry = sortedEntries[count]

        #   convert string-dates into datetime-dates again
        #   'entry' is used because of iteration (datetime would be converted into datetime (with strptime)
        #   after second iteration --> error)
        #   only upcoming dates in the next <displayDays> are getting stored in entry-list
        #   .timestamp() to get unix-timestamp of date for further bot implementation
        timeLeft = datetime.strptime(originalEntry[0], "%m/%d/%y %H:%M") - datetime.today()
        timeLeftSeconds = timeLeft.total_seconds()
        days = math.ceil((timeLeftSeconds/3600)/24)
        if days <= displayDays and timeLeftSeconds>=0:
            entry.append([round(datetime.strptime(originalEntry[0], "%m/%d/%y %H:%M").timestamp()), originalEntry[1]])

        count +=1

        #   store formatted date for discord + text of event in string for easier output in main.py
        #   add newspace to text if not last element in entry
        if(count == len(sortedEntries)):
            for content in entry:
                text = '<t:'+str(content[0])+':F>' + ' ' + content[1] + ' ' + '<t:'+str(content[0])+':R>'
                output += text+'\n' if content != entry[len(entry)-1] else text
            return output