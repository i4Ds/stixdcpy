#!/usr/bin/python3

import pandas as pd
from astropy.time import Time
from datetime import datetime



def anytime(dt, fm='iso'):
    if isinstance(dt, Time):
        dt=dt.to_datetime()
    t=pd.to_datetime(dt,utc=True)
    if fm=='iso':
        return t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    elif fm=='unix':
        return t.timestamp()
    elif fm=='datetime':
        return t.to_pydatetime()
    return t



def utc2unix(dt):
    t=pd.to_datetime(dt,utc=True)
    return t.timestamp()
    

def utc2datetime(t):
    return pd.to_datetime(t, utc=True).to_pydatetime()

def datetime2unix(t):
   t=pd.to_datetime(t, utc=True)
   return t.timestamp()


def unix2utc(ts):
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')


def unix2datetime(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp)
