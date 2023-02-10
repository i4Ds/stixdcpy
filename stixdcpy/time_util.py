#!/usr/bin/python3

from datetime import datetime
from dateutil import parser as dtparser


def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.isoformat(timespec='milliseconds')
    elif isinstance(dt, (int, float)):
        return datetime.utcfromtimestamp(dt).isoformat(timespec='milliseconds')
    elif isinstance(dt, str):
        try:
            return format_datetime(float(dt))
        except ValueError:
            return dt
    else:
        return '1970-01-01T00:00:00.000Z'


def now():
    return datetime.utcnow()

def to_iso_format(t):
    dt=utc2datetime(t)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_now(dtype='unix'):
    utc_iso = datetime.utcnow().isoformat() + 'Z'
    if dtype == 'unix':
        return dtparser.parse(utc_iso).timestamp()
    return utc_iso


def utc2unix(utc):
    if isinstance(utc, int) or isinstance(utc, float):
        return utc

    dt = utc2datetime(utc)
    return dt.timestamp()
    

def utc2datetime(utc):
    if isinstance(utc, datetime):
        return utc

    if not utc.endswith('Z'):
        utc += 'Z'
    try:
        return dtparser.parse(utc)
    except:
        return None



def datetime2unix(timestamp):
    dt = None
    if isinstance(timestamp, float):
        dt = datetime.utcfromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            ts = float(timestamp)
            dt = datetime.utcfromtimestamp(ts)
        except ValueError:
            dt = dtparser.parse(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    if dt:
        return dt.timestamp()
    return 0


def unix2utc(ts):
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')


def unix2datetime(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp)
