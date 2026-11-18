#!/usr/bin/python3

from datetime import datetime
import pandas as pd
from astropy.time import Time

def anytime(dt, fm='iso'):
    """Converts various date/time formats to specified format.

    Args:
        dt (str, Time, datetime, Timestamp): Input date/time.
        fm (str): Output format, 'iso' (default), 'unix', or 'datetime'.

    Returns:
        str or float or datetime: Converted date/time.

    Raises:
        ValueError: If the input format is not recognized.
    """
    if isinstance(dt, Time):
        dt = dt.to_datetime()
    t = pd.to_datetime(dt, utc=True)
    if fm == 'iso':
        return t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    elif fm == 'unix':
        return t.timestamp()
    elif fm == 'datetime':
        return t.to_pydatetime()
    else:
        raise ValueError("Invalid output format. Use 'iso', 'unix', or 'datetime'.")


def utc2unix(dt):
    """Converts UTC date/time to Unix timestamp.

    Args:
        dt (str): UTC date/time string.

    Returns:
        float: Unix timestamp.
    """
    t = pd.to_datetime(dt, utc=True)
    return t.timestamp()


def utc2datetime(t):
    """Converts UTC date/time to datetime object.

    Args:
        t (str): UTC date/time string.

    Returns:
        datetime: Datetime object in UTC.
    """
    return pd.to_datetime(t, utc=True).to_pydatetime()


def datetime2unix(t):
    """Converts datetime object to Unix timestamp.

    Args:
        t (datetime): Datetime object.

    Returns:
        float: Unix timestamp.
    """
    t = pd.to_datetime(t, utc=True)
    return t.timestamp()


def utc2filepath(t):
    """Converts UTC date/time to filepath format 'year/month/day'.

    Args:
        t (str): UTC date/time string.

    Returns:
        str: Filepath in 'year/month/day' format.
    """
    dt = utc2datetime(t)
    return dt.strftime("%Y/%m/%d")


def unix2utc(ts):
    """Converts Unix timestamp to UTC date/time string.

    Args:
        ts (float): Unix timestamp.

    Returns:
        str: UTC date/time string.
    """
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')


def unix2datetime(unix_timestamp):
    """Converts Unix timestamp to datetime object.

    Args:
        unix_timestamp (float): Unix timestamp.

    Returns:
        datetime: Datetime object in UTC.
    """
    return datetime.utcfromtimestamp(unix_timestamp)

# Example usage and testing:
# Uncomment and use the functions as needed.
# For example:
# print(anytime('2023-04-05T00:00:00', 'iso'))
# print(utc2unix('2023-04-05T00:00:00'))
# print(utc2datetime('2023-04-05T00:00:00'))
# print(datetime2unix(datetime.now()))
# print(utc2filepath('2023-04-05T00:00:00'))
# print(unix2utc(1616812800))
# print(unix2datetime(1616812800))

