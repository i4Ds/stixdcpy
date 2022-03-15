#!/usr/bin/python
"""
    This module provides APIs to retrieve data from STIX data center
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""

import hashlib

import numpy as np
import pandas as pd
import pprint
from pathlib import Path, PurePath
from dateutil import parser as dtparser

import requests
from astropy.io import fits
from tqdm import tqdm

DOWNLOAD_PATH = Path.cwd() / 'downloads'
DOWNLOAD_PATH.mkdir(parents=False, exist_ok=True)
HOST = 'https://pub023.cs.technik.fhnw.ch'
#HOST='http://localhost:5000'
URLS_POST = {
    'LC': f'{HOST}/api/request/ql/lightcurves',
    'HK': f'{HOST}/api/request/housekeeping',
    'HK2': f'{HOST}/api/request/hk2',
    'ELUT': f'{HOST}/api/request/eluts',
    'EPHEMERIS': f'{HOST}/api/request/ephemeris',
    'ATTITUDE': f'{HOST}/api/request/solo/attitude',
    'SCIENCE': f'{HOST}/api/request/science-data/id',
    'TRANSMISSION': f'{HOST}/api/request/transmission',
    'FLARE_LIST': f'{HOST}/api/request/flare-list',
    'CFL_SOLVER': f'{HOST}/api/request/solve/cfl'
}

FITS_TYPES = {
    'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin', 'hkmax'
}


class FitsQueryResult(object):
    def __init__(self, resp):
        self.hdu_objects = []
        self.result = resp
        self.downloaded_fits_files = []

    def __repr__(self):
        return str(self.result)

    def __getitem__(self, index):
        return self.result[index]

    def __getattr__(self, name):
        if name in ['num', 'len']:
            return len(self.result)
        elif name == 'hduls':
            return self.hdu_objects

    def __len__(self):
        return len(self.result)

    def pprint(self):
        pprint.pprint(self.result)

    def to_pandas(self):
        return pd.DataFrame(self.result)

    def open_fits(self):
        self.hdu_objects = []
        for filename in self.downloaded_fits_files:
            self.hdu_objects.append(fits.open(filename))
        return self.hdu_objects

    def fits_info(self):
        for hdu in self.hdu_objects:
            print(hdu.info())

    def get_fits_ids(self):
        return [row['fits_id'] for row in self.result]

    def fetch(self):
        if self.result:
            self.downloaded_fits_files = FitsQuery.fetch(self.result)
            return self.downloaded_fits_files
        else:
            print('WARNING: Nothing to be downloaded from stix data center!')


class FitsQuery(object):
    """
    Request FITS format data from STIX data center
    """
    def __init__(self):
        self.fits_file_list = []

    @staticmethod
    def wget(url: str, desc: str, progress_bar=True):
        """Download a file from the link and save the file to a temporary file.
           Downloading progress will be shown in a progress bar

        Args:
            url (str): URL
            desc (str): description to be shown on the progress bar

        Returns:
            temporary filename 
        """
        stream = progress_bar
        resp = requests.get(url, stream=stream)
        content_type = resp.headers.get('content-type')
        if content_type != 'binary/x-fits':
            print('ERROR:', resp.content)
            return None

        folder = DOWNLOAD_PATH
        try:
            fname = resp.headers.get("Content-Disposition").split(
                "filename=")[1]
        except AttributeError:
            md5hex = hashlib.md5(url.encode('utf-8')).hexdigest()
            fname = f'{md5hex}.fits'
        filename = PurePath(folder, fname)
        file_path = Path(filename)
        if file_path.is_file():
            print(f'Found the data in local storage. Filename: {filename} ...')
            return str(file_path)
        f = open(filename, 'wb')
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

    @staticmethod
    def query(start_utc, stop_utc, product_type='lc'):
        if product_type not in FITS_TYPES:
            raise TypeError(
                f'Invalid product type! product_type can be one of {str(FITS_TYPES)}'
            )
        url = f'{HOST}/query/fits/{start_utc}/{stop_utc}/{product_type}'
        r = requests.get(url).json()
        res = []
        if isinstance(r, list):
            res = r
        elif 'error' in r:
            print(r['error'])
        return FitsQueryResult(res)

    @staticmethod
    def fetch_bulk_science_by_request_id(request_id):
        url = f'{HOST}/download/fits/bsd/{request_id}'
        fname = FitsQuery.wget(url, f'Downloading STIX Science data #{request_id}')
        return fname

    @staticmethod
    def fetch(query_results):
        fits_ids = []
        if isinstance(query_results, FitsQueryResult):
            fits_ids = query_results.get_fits_ids()
        elif isinstance(query_results, int):
            fits_ids = [query_results]
        elif isinstance(query_results, list):
            try:
                fits_ids = [row['fits_id'] for row in query_results]
            except Exception as e:
                pass
            if not fits_ids:
                try:
                    fits_ids = [
                        row for row in query_results if isinstance(row, int)
                    ]
                except:
                    pass
        if not fits_ids:
            raise TypeError('Invalid argument type')

        fits_filenames = []
        try:
            for file_id in fits_ids:
                fname = FitsQuery.get_fits(file_id)
                fits_filenames.append(fname)
        except Exception as e:
            raise e
        # self.fits_file_list=fits_filenames
        return fits_filenames

    @staticmethod
    def get_fits(fits_id, progress_bar=True):
        """Download FITS data products from STIX data center.
        Args:
            fits_id: FITS file ID
            progress_bar: show the progress bar if it is true


        Returns:
            A FITS hdulist object if success;  None if failed
        """
        url = f'{HOST}/download/fits/{fits_id}'
        fname = FitsQuery.wget(url, 'Downloading data', progress_bar)
        return fname

    @staticmethod
    def fetch_continuous_data(start_utc, end_utc, data_type):
        if data_type not in ['hkmax', 'lc', 'var', 'qlspec', 'bkg']:
            raise TypeError(f'Data type {data_type} not supported!')
        url = f'{HOST}/create/fits/{start_utc}/{end_utc}/{data_type}'
        fname = FitsQuery.wget(url, 'Downloading data', True)
        return fname


class JSONRequest(object):
    """Request json format data from STIX data center """
    @staticmethod
    def post(url, form):
        response = requests.post(url, data=form)
        data = response.json()

        if 'error' in data:
            if data['error']:
                return None
        return data

    @staticmethod
    def fetch_light_curves(begin_utc: str, end_utc: str, ltc: bool):
        """ Request light curve from STIX data center

        Args:
            begin_utc:  str
                Observation start time
            end_utc: str
                Observation end time
            ltc: bool, optional
                Light time correction enabling flag.   Do light time correction if True
        Returns:
            lightcurve: dict
                A python dictionary containing light curve data

        """
        form = {'begin': begin_utc, 'ltc': ltc, 'end': end_utc}
        url = URLS_POST['LC']
        return JSONRequest.post(url, form)

    @staticmethod
    def fetch_housekeeping(begin_utc: str, end_utc: str):
        """Fetch housekeeping data from STIX data center

        Args:
            begin_utc: Data start time
            end_utc: data end time

        Returns:
            result:  dict
            housekeeping data

        """
        if not begin_utc.endswith('Z'):
            begin_utc += 'Z'
        if not end_utc.endswith('Z'):
            end_utc += 'Z'
        start_unix = dtparser.parse(begin_utc).timestamp()
        end_unix = dtparser.parse(end_utc).timestamp()
        duration = int(end_unix) - int(start_unix)
        form = {
            'start_unix': start_unix,
            'duration': duration,
        }
        url = URLS_POST['HK']
        return JSONRequest.post(url, form)

    @staticmethod
    def solve_cfl(cfl_counts, cfl_counts_err, fluence, fluence_err):
        """compute flare location using the online flare location solver

        Args:
            cfl_counts: numpy array or list
                counts recorded by the 12 CFL pixels
            cfl_counts_err:  numpy array or list
                standard deviations of  the counts recorded by the 12 CFL pixels
            fluence: float
                X-ray fluence in units of  counts/mm2,  calculated using counts recorded by other detectors
            fluence_err: float
                Errors in fluence in counts/mm2 units
        Returns:
            location: dict
                CFL location, ephemeris and the chisquare map

        """
        form = {'counts': cfl_counts, 'counts_err':cfl_counts_err,
                'fluence':fluence,'fluence_err':fluence_err}
        url = URLS_POST['CFL_SOLVER']
        return JSONRequest.post(url, form)

    @staticmethod
    def fetch_elut(utc):
        """Download ELUT from STIX data center
        Args:
            utc: Time
        Returns: dict
            object: a diction string containing elut information
        """
        form = {'utc': utc}
        url = URLS_POST['ELUT']
        return JSONRequest.post(url, form)

    @staticmethod
    def request_ephemeris(start_utc: str, end_utc: str, steps=1):
        return JSONRequest.post(URLS_POST['EPHEMERIS'], {
            'start_utc': start_utc,
            'end_utc': end_utc,
            'steps': steps
        })
    @staticmethod
    def request_attitude(start_utc: str, end_utc: str,  steps=1, instrument_frame='SOLO_SRF', ref_frame='SOLO_SUN_RTN'):
        form={
            'start_utc': start_utc,
            'end_utc': end_utc,
            'steps': steps,
            'frame1':instrument_frame,
            'frame2':ref_frame
        }
        ret=JSONRequest.post(URLS_POST['ATTITUDE'], form)
        return ret
    @staticmethod
    def fetch_science_data(_id: int):
        """fetch science data from stix data center

        Args:
            _id: int
                science data unique ID, which can be found on STIX data center bulk science data web page


        Returns:
            science_data: dict
                science data received from data center if success or None if failed

        """
        return JSONRequest.post(URLS_POST['SCIENCE'], {
            'id': _id,
        })

    @staticmethod
    def fetch_flare_list(start_utc: str, end_utc: str, sort: str = 'time'):
        """ query and download flare list from stix data center

        Args:
            start_utc: str
                flare start UTC
            end_utc: str
                flare end UTC
            sort: str
                key to sort flares. It can be one of ['goes','time', 'LC0','LC1','LC2','LC3','LC4], LCi here means the i-th QL light curve


        Returns:
            flare_list: dict or None
                flare list if success or None if failed.

        """
        return JSONRequest.post(URLS_POST['FLARE_LIST'], {
            'start_utc': start_utc,
            'end_utc': end_utc,
            'sort': sort
        })
