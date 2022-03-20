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

icalfile = open('calender_uni_wichtig.ics', 'rb')
gcal = icalendar.Calendar.from_ical(icalfile.read())

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
        if startdt.strftime("%D") >= datetime.strftime(datetime.today(),"%D") and startdt.strftime("%Y") >= datetime.strftime(datetime.today(),"%Y"):
            savedEntries.append([startdt.strftime("%D %H:%M"), str(summary)])
icalfile.close()

#   sort dates in listX
sortedEntries = sorted(savedEntries)
#   iterate through list

def print_dates(displayDays):
    count = 0
    outputList = []
    output = ''
    #   iterate through sortedEntries
    while True: 
        #   save original Entry at index
        originalEntry = sortedEntries[count]

        #   convert string-dates into datetime-dates again
        #   'entry' is used, because if method gets iterated (and originalEntry would be used), then (after first iteration) 
        #   strptime would convert Date into Date --> error
        entry = datetime.strptime(originalEntry[0], "%m/%d/%y %H:%M")

        #   calculate timedelta for left over time
        timeLeft = entry - datetime.today()
        timeLeftSeconds = timeLeft.total_seconds()
        days = (timeLeftSeconds/3600)/24
        hours = (days - math.floor(days))*24
        minutes = (hours - math.floor(hours))*60
        seconds = (minutes - math.floor(minutes))*60

        #   format Dates into two-digit-Dates: 1.1.2001 1:1:1 --> 01.01.2001 01:01:01
        dateDay = f'{entry.day:02d}'
        dateMonth = f'{entry.month:02d}'
        dateYear = entry.year
        dateHour = f'{entry.hour:02d}'
        dateMinute = f'{entry.minute:02d}'
        dateSecond = f'{entry.second:02d}'

        #   save dates which are in specified time span into outputList
        if days <= displayDays:
            outputList.append(str(dateDay) + '.' + str(dateMonth) + '.' + str(dateYear) + ' ' + str(dateHour) + ':' + str(dateMinute) + ':' + str(dateSecond) + ' | ' +
            originalEntry[1] + " --> " + str(math.floor(days)) + " Tage  " + str(math.floor(hours)) + " Stunden  " + str(math.floor(minutes)) + 
            " Minuten  " + str(math.floor(seconds)) + " Sekunden")
        
        count += 1

        #   save dates into output (as a string) after iteration through sortedEntries is finished
        if(count == len(sortedEntries)):
            for i in outputList:
                #   add newspace after string, if string is not last element
                output+= i+'\n' if i != outputList[len(outputList)-1] else i
            return output
print(print_dates(300))
