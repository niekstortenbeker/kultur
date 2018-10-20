import CreateDatabase
import webscraping
import InputOutput
from pprint import pprint
import os

webscraping.start_driver()

ostertor = webscraping.CinemaOstertor()
program = ostertor.create_program_db()

webscraping.close_driver()


def parse_datetime(datetime_string):
    """datetime_string: 'So 08.07. 14:15'. Parse date from this, and guess the year"""
    datetime = arrow.now('Europe/Berlin')
    datetime = datetime.replace(month=int(datetime_string[6:8]),
                                day=int(datetime_string[3:5]),
                                hour=int(datetime_string[10:12]),
                                minute=int(datetime_string[13:15]),
                                second=0,
                                microsecond=0)
    if datetime < arrow.now("Europe/Berlin").shift(months=-1):
        return datetime.replace(year=datetime.year + 1)
    else:
        return datetime


def parse_datetime(self, time, day, month):
    #TODO: change filmkunst as to use this as a class method
    """get arrow object from date from this, and guess the year"""
    datetime = arrow.now('Europe/Berlin')
    datetime = datetime.replace(month=month,
                                day=int(day),
                                hour=int(time[:2]),
                                minute=int(time[3:]),
                                second=0,
                                microsecond=0)
    if datetime < arrow.now("Europe/Berlin").shift(months=-1):
        return datetime.replace(year=datetime.year + 1)
    else:
        return datetime

def parse_datetime(self, month, day, hour, minute):
    """get arrow object, guess the year"""
    datetime = arrow.now('Europe/Berlin')
    datetime = datetime.replace(month=month,
                                day=day,
                                hour=hour,
                                minute=minute,
                                second=0,
                                microsecond=0)
    if datetime < arrow.now("Europe/Berlin").shift(months=-1):
        return datetime.replace(year=datetime.year + 1)
    else:
        return datetime