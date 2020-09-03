# -*- coding: utf-8 -*-
""" STIX data query APIs

    created on Sept. 2nd, 2020

"""

import io
import requests
import numpy as np
from tqdm import tqdm
from astropy.io import fits
from tempfile import NamedTemporaryFile
FITS_TYPES = {
    'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin', 'hkmax'
}


def download(url: str, desc: str):
    """Download a file from the link and save the file to a temporary file.
       Downloading progress will be shown in a progress bar

    Args:
        url (str): URL
        desc (str): description to be shown on the progress bar

    Returns:
        temporary filename 
    """    
    resp = requests.get(url, stream=True)
    f = NamedTemporaryFile(delete=False, suffix=".fits")
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


def fetch(start_utc, stop_utc, fits_type='lc'):
    """Query data from pub023 and download FITS file from the server.
    A fits file will be received for the packets which satistify the query condition.
    If no data is found on pub023, a json object will be received
    

    Args:
        start_utc (str): start UTC  in formats yyyy-dd-mmTHH:MM:SS, yyyddmmHHMMSS,  
        stop_utc ([type]): stop UTC formats the same as above
        fits_type (str, optional): 
            data product type It can be 'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin' or 'hkmax'.  Defaults to 'lc'.

    Returns:
        astropy fits object if the request is successful;  None if it is failed or no result returns
    """    
    pattern = 'http://pub023.cs.technik.fhnw.ch/create/fits/{start_utc}/{stop_utc}/{fits_type}'
    url = pattern.format(start_utc=start_utc,
                         stop_utc=stop_utc,
                         fits_type=fits_type)
    temp_file = download(url, 'Fetching data')
    try:
        return fits.open(temp_file)
    except:
        print('Invalid request or no data was found')
        return None


#search('2020-05-01T00:00:00','2020-05-01T01:00:00','hkmax')
