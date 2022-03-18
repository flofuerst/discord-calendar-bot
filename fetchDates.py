from cgi import test
from datetime import datetime, timedelta, timezone
from itertools import count
from traceback import print_tb
import icalendar
from dateutil.rrule import *
import math

if __name__ == "__main__":
    def parse_recurrences(recur_rule, start, exclusions):
        #   Find all reoccuring events
        rules = rruleset()
        first_rule = rrulestr(recur_rule, dtstart=start)
        rules.rrule(first_rule)
        if not isinstance(exclusions, list):
            exclusions = [exclusions]
            for xdate in exclusions:
                try:
                    rules.exdate(xdate.dts[0].dt)
                except AttributeError:
                    pass

        #   get current utc time with offset (CET Timezone) 
        now = datetime.now(timezone.utc) + timedelta(hours=1)
        this_year = now + timedelta(days=120)
        dates = []
        for rule in rules.between(now, this_year):
            dates.append(rule.strftime("%D %H:%M"))
        return dates

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
            if component.get('rrule'):
                reoccur = component.get('rrule').to_ical().decode('utf-8')
                #   save reocurring dates in list
                for date in parse_recurrences(reoccur, startdt, exdate):
                    savedEntries.append([date, str(summary)])
            else:
                #   save other dates in list
                if startdt.strftime("%D") >= datetime.strftime(datetime.today(),"%D") and startdt.strftime("%Y") >= datetime.strftime(datetime.today(),"%Y"):
                    savedEntries.append([startdt.strftime("%D %H:%M"), str(summary)])
    icalfile.close()
    
    #   sort dates in listX
    sortedEntries = sorted(savedEntries)
    #   iterate through list
    for x in sortedEntries:
        #   convert string-dates into datetime-dates again
        x[0] = datetime.strptime(x[0], "%m/%d/%y %H:%M")

        #   calculate timedelta and print left over time 
        
        timeLeft = x[0]- datetime.today()
        timeLeftSeconds = timeLeft.total_seconds()
        days = (timeLeftSeconds/3600)/24
        hours = (days - math.floor(days))*24
        minutes = (hours - math.floor(hours))*60
        seconds = (minutes - math.floor(minutes))*60
        print(str(x[0].day) + '.' + str(x[0].month) + '.' + str(x[0].year), str(x[0].hour) + ':' + str(x[0].minute)+ ':' + str(x[0].second), x[1], "-->",
            math.floor(days), "Tage", math.floor(hours), "Stunden", math.floor(minutes), "Minuten", math.floor(seconds), "Sekunden")