# -*- coding: utf-8 -*-
""" STIX data query APIs

    created on Sept. 2nd, 2020
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)

"""

import io
import requests
import numpy as np
from tqdm import tqdm
from datetime import datetime
from astropy.io import fits
from tempfile import NamedTemporaryFile
FITS_TYPES = {
    'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin', 'hkmax'
}

def download_file(url: str, desc: str, progress_bar=True,filename=None):
    """Download a file from the link and save the file to a temporary file.
       Downloading progress will be shown in a progress bar

    Args:
        url (str): URL
        desc (str): description to be shown on the progress bar

    Returns:
        temporary filename 
    """    
    if filename is None:
        f = NamedTemporaryFile(delete=False, suffix=".fits")
    else:
        f=open(filename)
    stream=progress_bar
    resp = requests.get(url, stream=stream)
    if not progress_bar:
        f.write(resp.content)
    else:
        chunk_size = 1024
        total = int(resp.headers.get('content-length', 0))
        with tqdm(
            desc=desc,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=chunk_size,
        ) as bar:
            for data in resp.iter_content(chunk_size=chunk_size):
                size = f.write(data)
                bar.update(size)
    name = f.name
    f.close()
    return name
def fetch(start_utc, stop_utc, fits_type='lc', progress_bar=True):
    temp_file=download(start_utc, stop_utc, fits_type, progress_bar)
    try:
        return fits.open(temp_file)
    except:
        print('Invalid request or no data was found')
        return None


def download(start_utc, stop_utc, fits_type='lc', progress_bar=True, filename=None):
    """Query data from pub023 and download FITS file from the server.
    A fits file will be received for the packets which satistify the query condition.
    If no data is found on pub023, a json object will be received
    

    Args:
        start_utc (str): start UTC  in formats yyyy-dd-mmTHH:MM:SS, yyyddmmHHMMSS,   or datetime 
        stop_utc ([type]): stop UTC formats the same as above
        fits_type (str, optional): 
            data product type It can be 'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin' or 'hkmax'.  Defaults to 'lc'.

    Returns:
        astropy fits object if the request is successful;  None if it is failed or no result returns
    """    
    if isinstance(start_utc, datetime):
        start_utc=start_utc.strftime("%m-%d-%YT%H:%M:%S")
    if isinstance(stop_utc, datetime):
        stop_utc=stop_utc.strftime("%m-%d-%YT%H:%M:%S")

    pattern = 'http://pub023.cs.technik.fhnw.ch/create/fits/{start_utc}/{stop_utc}/{fits_type}'
    url = pattern.format(start_utc=start_utc,
                         stop_utc=stop_utc,
                         fits_type=fits_type)
    temp_file = download_file(url, 'Fetching data', progress_bar, filename)
    return temp_file

#search('2020-05-01T00:00:00','2020-05-01T01:00:00','hkmax')
