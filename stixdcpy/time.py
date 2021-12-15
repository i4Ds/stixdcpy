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


def get_now(dtype='unix'):
    utc_iso = datetime.utcnow().isoformat() + 'Z'
    if dtype == 'unix':
        return dtparser.parse(utc_iso).timestamp()
    return utc_iso


def utc2unix(utc):
    if isinstance(utc, str):
        if not utc.endswith('Z'):
            utc += 'Z'
        try:
            return dtparser.parse(utc).timestamp()
        except:
            return 0
    elif isinstance(utc, int) or isinstance(utc, float):
        return utc
    else:
        return 0


def utc2datetime(utc):
    if not utc.endswith('Z'):
        utc += 'Z'
    try:
        return dtparser.parse(utc)
    except:
        return None


def unix2datetime(timestamp):
    dt = None
    if isinstance(timestamp, float):
        dt = datetime.utcfromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            ts = float(timestamp)
            dt = datetime.utcfromtimestamp(ts)
        except ValueError:
            dt = dtparser.parse(timestamp)
    elif isinstance(timestamp, datetime.datetime):
        dt = timestamp
    return dt


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
    elif isinstance(timestamp, datetime.datetime):
        dt = timestamp
    if dt:
        return dt.timestamp()
    return 0


def unix2utc(ts):
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')


def unix2datetime(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp)
