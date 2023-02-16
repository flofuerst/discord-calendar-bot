from datetime import datetime
import caldav
import os
import pytz

def create_event(startDate, endDate, summary):
    url = os.getenv('MODIFY_URL')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    with caldav.DAVClient(
        url=url, username=username, password=password
    ) as client:

        # fetch a principal object
        # this will cause communication with the server
        my_principal = client.principal()

        # fetch principal calendars
        calendars = my_principal.calendars()

        for cal in calendars:
            # check for right calendar
            if("TUW (Patrick)" in cal.name):
                # convert datetime to local datetime based on utc
                local = pytz.timezone('Europe/Vienna')
                naiveStartDate = datetime.strptime(startDate.strftime("%D %H:%M"), "%m/%d/%y %H:%M")
                localStartDate = local.localize(naiveStartDate, is_dst=None)
                naiveEndDate = datetime.strptime(endDate.strftime("%D %H:%M"), "%m/%d/%y %H:%M")
                localEndDate = local.localize(naiveEndDate, is_dst=None)

                may_event = cal.save_event(
                dtstart=localStartDate,
                dtend=localEndDate,
                summary=summary,
                # rrule={"FREQ": "YEARLY"},
                )