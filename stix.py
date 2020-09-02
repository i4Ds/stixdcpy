# -*- coding: utf-8 -*-
""" STIX data query APIs
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


def search(start_utc, stop_utc, fits_type='lc'):
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
