from datetime import datetime, timedelta, timezone
import icalendar
import os

def create_event():
    url = os.getenv('URL')
    #TODO: implement event creation