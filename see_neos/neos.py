"""
The concept of Ephemeris is central to this script
http://en.wikipedia.org/wiki/Ephemeris
"""

import sys
import heapq
import requests

from datetime import datetime
from dateutil import tz
import time

import ephem

# Ephemeris data in XEphem format from
# http://www.minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txts
# Data format
# http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId468501

AU = 149597871  # Astronomical Unit km
ABOVE_HORIZON = '45'  # 20 degrees
NUM_CLOSEST = 100


TIMEZONE_API_URL = "https://maps.googleapis.com/maps/api/timezone/json"


def load_asteroid_ephemeris(ephemiris_line):
    neo = ephem.readdb(ephemiris_line)
    return neo


def load_neos_from_file(file_name):
    neos = []
    data_file = open(file_name)
    for ephemiris_line in data_file:
        if ephemiris_line.startswith("#"):
            continue
        neos.append(load_asteroid_ephemeris(ephemiris_line))
    return neos


def compute_locations(neos, observer_func):
    observer = observer_func()
    for neo in neos:
        neo.compute(observer)


def get_n_closest(neos, num):
    h = []
    for neo in neos:
        heapq.heappush(h, (neo.earth_distance, neo))

    return heapq.nsmallest(num, h)


def get_rising(neos, observer_func, tz):
    for neo in neos:
        observer = observer_func()
        try:
            rising = observer.next_rising(neo)
            local_rising = _convert_date_to_local(rising, tz)
            print neo.name + " " + str(local_rising)
        except ephem.CircumpolarError:
            print "Never changes"


def _convert_date_to_local(date, local_timezone):
    utc_zone = tz.tzutc()
    date = date.datetime() # convert PyEphem date to Python date
    date = date.replace(tzinfo=utc_zone)

    return date.astimezone(local_timezone)


def _get_timezone(observer):
    def _parse_coordinates(str_coords):
        deg, minutes, seconds = str_coords.split(":")
        return int(deg) + float(minutes)/60 + float(seconds)/3600

    #parse Observer lat long in minutes to decimal
    lat = _parse_coordinates(str(observer.lat))
    lng = _parse_coordinates(str(observer.lon))
    
    #Make a request to get the name of the timezone in that location
    parameters_dict = {'location': "%s,%s" % (lat,lng), 'sensor': 'false',
                        'timestamp': int(time.time())}
    response = requests.get(TIMEZONE_API_URL, params=parameters_dict)
    #Get timezone object
    timezone_name = response.json()['timeZoneId']
    timezone = tz.gettz(timezone_name)

    return timezone


def define_observer_func(city, date):
    """
    This is hack to rebuild the observer object everytime. We need to extract data from the observer
    and that seems to affect things.

    TODO: Make sure that this is necessary
    """
    def wrapper():
        observer = ephem.city(city)
        observer.date = date
        observer.horizon = ABOVE_HORIZON

        return observer
    return wrapper


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("python neos.py Toronto 2013/04/22 neo_data.txt")
    city = sys.argv[1]
    date = sys.argv[2]
    file_name = sys.argv[3]

    neos = load_neos_from_file(file_name)
    observer_func = define_observer_func(city, date)
    compute_locations(neos, observer_func)
    closest_neos = get_n_closest(neos, num=NUM_CLOSEST)

    for e in closest_neos:
        print e[1].name + "is " + str(e[0]*AU) + "km"
    observer = observer_func()
    timezone = _get_timezone(observer)

    get_rising([n[1] for n in closest_neos], observer_func, tz=timezone)
