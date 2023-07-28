#!/usr/bin/python
"""
    This module provides APIs to retrieve data from STIX data center
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""
import hashlib
import simplejson
import numpy as np
import pandas as pd
from pprint import pprint
from pathlib import Path, PurePath
from datetime import datetime

from collections import UserDict
import requests
from astropy.io import fits
from tqdm import tqdm
from stixdcpy.logger import logger
from stixdcpy import time_util as stu 

DOWNLOAD_LOCATION = Path.cwd() / 'downloads'

HOST = 'https://datacenter.stix.i4ds.net'
#HOST='http://localhost:5000'
ENDPOINTS = {
    'LC': f'{HOST}/api/request/ql/lightcurves',
    'HK': f'{HOST}/api/request/housekeeping',
    'HK2': f'{HOST}/api/request/hk2',
    'ELUT': f'{HOST}/api/request/eluts',
    'EPHEMERIS': f'{HOST}/api/request/ephemeris',
    'ATTITUDE': f'{HOST}/api/request/solo/attitude',
    'SCIENCE_DATA': f'{HOST}/api/request/science-data/id',
    'SCIENCE': f'{HOST}/api/query/science',
    'TRANSMISSION': f'{HOST}/api/request/transmission',
    'FLARE_LIST': f'{HOST}/api/request/flare-list',
    'FLARE_IMAGES': f'{HOST}/api/request/imaging/flare',
    'STIX_POINTING': f'{HOST}/api/request/stixfov',
    'FITS': f'{HOST}/api/query/fits',
    'FLARE_AUX': f'{HOST}/api/request/auxiliary/flare',
    'CFL_SOLVER': f'{HOST}/api/request/solve/cfl',
    'CAVEATS': f'{HOST}/api/operations/caveats',
    'SPECTROGRAMS': f'{HOST}/request/bsd/spectrograms'
}



class FitsQueryResult(object):
    """
        FITS query result manager 
    """
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

    def dataframe(self):
        """
        Convert FitsQueryResult to pandas dataframe
        Returns:
            pandas data frame
        """
        return pd.DataFrame(self.result)
    def to_pandas(self):
        """
        Convert FitsQueryResult to pandas dataframe
        Returns:
            pandas data frame
        """
        return pd.DataFrame(self.result)


    def open_fits(self):
        """
         Open all the FITS files 
        
        Returns:
            hdu_objcts:  list
                A list of HDU objects

        """
        self.hdu_objects = []
        for filename in self.downloaded_fits_files:
            self.hdu_objects.append(fits.open(filename))
        return self.hdu_objects

    def fits_info(self):
        """
        Print out information of the loaded specified FITS files
        """
        for hdu in self.hdu_objects:
            logger.info(hdu.info())

    def get_fits_file_ids(self):
        """
        Get FITS file IDs
        Return
        ids: list
            FITS file ids
        """
        return [row['fits_id'] for row in self.result]

    def fetch(self):
        """
        Download fits files from STIX data center
        FITS files will be stored in the folder download/ in the current directory
        
        Returns:

        fits_filenames:  list
            List of downloaded FITS filenames
        

        """
        if self.result:
            self.downloaded_fits_files = FitsQuery.fetch(self.result)
            return self.downloaded_fits_files
        else:
            logger.warning(
                'WARNING: Nothing to be downloaded from stix data center!')


class FitsQuery(object):
    """
    Query or Fetch FITS products from STIX data center
    """
    download_location=DOWNLOAD_LOCATION

    def __init__(self):
        self.fits_file_list = []
    
    @classmethod
    def chdir(cls, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        FitsQuery.download_location=path

    @staticmethod
    def getcwd():
        return FitsQuery.download_location
        


    @staticmethod
    def wget(url: str, desc: str, progress_bar=True):
        """Download a file from the link and save the file to a temporary file.
           Downloading progress will be shown in a progress bar

        Parameters:
            url (str): URL
            desc (str): description to be shown on the progress bar

        Returns:
            temporary filename 
        """
        stream = progress_bar
        resp = requests.get(url, stream=stream)
        content_type = resp.headers.get('content-type')
        if content_type != 'binary/x-fits':
            logger.error(resp.content)
            return None

        folder = FitsQuery.download_location
        Path(folder).mkdir(parents=True, exist_ok=True)

        try:
            fname = resp.headers.get("Content-Disposition").split(
                "filename=")[1]
        except AttributeError:
            md5hex = hashlib.md5(url.encode('utf-8')).hexdigest()
            fname = f'{md5hex}.fits'
        filename = PurePath(folder, fname)
        file_path = Path(filename)
        if file_path.is_file():
            logger.info(
                f'Found the data in the local storage. Filename: {filename} ...')
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
    def query(begin_utc, end_utc, product_type='lc', level='L1A', filter=None, path='.'):
        """Query FITS products from STIX data center

        Args:
            start_utc (str, datetime, pd.Timestamp or astropy.time.Time):
                start time
            stop_utc (str, datetime, pd.Timestamp or astropy.time.Time):
                end time
            product_type (str, optional): 
            FITS product type. Defaults to 'lc'.


        Returns:
            results: FitsQueryResult
                file result object
        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        form = {
            'start_utc': begin_utc,
            'end_utc': end_utc,
            'product_type': product_type,
            'level': level,
            'filter': str(filter)
        }
        url = ENDPOINTS['FITS']
        res = []
        r = Request.post(url, form)
        if isinstance(r, list):
            res = r
        return FitsQueryResult(res)

    @staticmethod
    def fetch_bulk_science_by_request_id(request_id, level='L1A'):
        url = f'{HOST}/download/fits/bsd/{request_id}/{level}'
        fname = FitsQuery.wget(url,
                               f'Downloading STIX Science data #{request_id}')
        return fname

    @staticmethod
    def fetch(query_results):
        """
        Download FITS files
        Arguments
        ----
        query_results: FitsQueryResult 
                FitsQueryResult object

        Returns
        -------
        filenames:  list
            A list of fits filenames 

        """
        fits_ids = []
        if isinstance(query_results, FitsQueryResult):
            fits_ids = query_results.get_fits_file_ids()
        elif isinstance(query_results, int):
            fits_ids = [query_results]
        elif isinstance(query_results, list):
            try:
                fits_ids = [row['file_id'] for row in query_results]
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
        return fits_filenames

    @staticmethod
    def get_fits(fits_id, progress_bar=True):
        """Download FITS data products from STIX data center.
        Parameters:
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

        start_utc, end_utc=stu.anytime(start_utc), stu.anytime(end_utc)
        if data_type not in ['hkmax', 'lc', 'var', 'qlspec', 'bkg']:
            raise TypeError(f'Data type {data_type} not supported!')
        url = f'{HOST}/create/fits/{start_utc}/{end_utc}/{data_type}'
        fname = FitsQuery.wget(url, 'Downloading data', True)
        return fname

class ResponseDict(dict):
    """
        Response from data center
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def dataframe(self):
        return pd.DataFrame([self])
class ResponseList(list):
    """
        Response from data center
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def dataframe(self):
        return pd.DataFrame(self)

class Request(object):
    """Request json format data from STIX data center """
    @staticmethod
    def post(url, form, result_type = 'object'):
        response = requests.post(url, data=form)
        try:
            data = response.json()
            if result_type == 'object':
                if isinstance(data,list):
                    return ResponseList(data)
                elif isinstance(data,dict):
                    return ResponseDict(data)

        except simplejson.errors.JSONDecodeError:
            logger.error("An error occurred on the server.")
            return None
        if 'error' in data:
            logger.error(data['error'])
            return None
        return data
    @staticmethod 
    def query_preview_flare_image_list(begin_utc, end_utc):
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        form = {'start_utc': begin_utc, 'end_utc':end_utc}
        url = ENDPOINTS['FLARE_IMAGES']
        return Request.post(url, form, result_type='dict')

    def query_preview_image_for_flare(flare_id:int):
        form = {'flare_id': flare_id}
        url = ENDPOINTS['FLARE_IMAGES']
        return Request.post(url, form, result_type='dict')
        





    @staticmethod
    def fetch_caveats(begin_utc, end_utc):
        """ Request light curve from STIX data center

        Parameters:
            begin_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                Observation start time
            end_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                Observation end time
            ltc: bool, optional
                Light time correction enabling flag.   Do light time correction if True
        Returns:
            lightcurve: dict
                A python dictionary containing light curve data

        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        form = {'begin': begin_utc, 'end': end_utc}
        url = ENDPOINTS['CAVEATS']
        data=Request.post(url, form, result_type='dict')
        return ResponseList(data['caveats'])

    @staticmethod
    def fetch_light_curves(begin_utc, end_utc , ltc: bool):
        """ Request light curve from STIX data center

        Parameters:
            begin_utc:   str, datetime, pandas.Timestamp or astropy.time.Time
                Observation start time
            end_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                Observation end time
            ltc: bool, optional
                Light time correction enabling flag.   Do light time correction if True
        Returns:
            lightcurve: dict
                A python dictionary containing light curve data

        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)

        form = {'begin': begin_utc, 'ltc': ltc, 'end': end_utc, 'version': 2}
        url = ENDPOINTS['LC']
        return Request.post(url, form)

    @staticmethod
    def fetch_housekeeping(begin_utc: str, end_utc: str):
        """Fetch housekeeping data from STIX data center

        Parameters:
            begin_utc :  str, datetime, pandas.Timestamp or astropy.time.Time

                Data start time
            end_utc:   str, datetime, pandas.Timestamp or astropy.time.Time
                data end time

        Returns:
            result:  dict
            housekeeping data

        """
        start_unix, end_unix=stu.anytime(begin_utc, fm='unix'), stu.anytime(end_utc, fm='unix')

        duration = int(end_unix) - int(start_unix)
        form = {
            'start_unix': start_unix,
            'duration': duration,
        }
        url = ENDPOINTS['HK']
        return Request.post(url, form)

    @staticmethod
    def solve_cfl(cfl_counts, cfl_counts_err, fluence, fluence_err):
        """compute flare location using the online flare location solver

        Parameters:
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
        form = {
            'counts': cfl_counts,
            'counts_err': cfl_counts_err,
            'fluence': fluence,
            'fluence_err': fluence_err
        }
        url = ENDPOINTS['CFL_SOLVER']
        return Request.post(url, form)

    @staticmethod
    def fetch_elut(utc):
        """Download ELUT from STIX data center
        Parameters:
            utc: Time
        Returns: dict
            object: a diction string containing elut information
        """
        form = {'utc': utc}
        url = ENDPOINTS['ELUT']
        return Request.post(url, form)

    @staticmethod
    def request_ephemeris(begin_utc, end_utc, steps=1):

        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)

        return Request.post(ENDPOINTS['EPHEMERIS'], {
            'start_utc': begin_utc,
            'end_utc': end_utc,
            'steps': steps
        })

    @staticmethod
    def request_pointing(utc):
        """
        request STIX pointing data 
        Parameters
        ----
        utc:  str, datetime, pandas.Timestamp or astropy.time.Time
            UTC time
        Returns
        ----
        data: dict
            dictionary containing pointing information
        """
        utc =stu.anytime(utc)
        return Request.post(ENDPOINTS['STIX_POINTING'], {
            'utc': utc,
        })

    @staticmethod
    def request_flare_light_time_and_angle(utc,
                                           flare_x: float,
                                           flare_y: float,
                                           observer='earth'):
        """
            calculate flare light times and relative angles 
        Parameters
        ----
            utc: str, datetime, pandas.Timestamp or astropy.time.Time
                observation time
            flare_x: float
                flare helio-projective longitude in units of arcsec as seen by the observer
            flare_y: float
                flare helio-projective latitude in units of arcsec 
            observer: str
                observer. It can be either "earth" or "stix" . Default "earth"
        Returns
        ----
            data: dict
                the light times and  angles
                'dt_flare':   difference of light time  between Flare-Earth and  Flare-STIX

                 'dt_sun_center':  difference of light time  between SunCenter-Earth and  SunCenter-STIX
                 'earth_flare_solo_deg':   Earth-Flare-SolO angle in units of degrees
                 'earth_sun_lt':  Earth-SunCenter light time
                 'flare_earth_lt':  Flare-Earth light time in units of seconds
                 'flare_norm_earth_deg': Earth-Flare-normal  angle in units of seconds
                 'flare_norm_solo_deg': SolO-Flare-normal  angle in units of seconds
                 'flare_solo_lt': Flare-SolO light time
                 'flare_solo_r': Flare-SolO distance in units of AU
                 'flare_utc': observation time, 
                 'mk': SPICE kernel version,
                 'observer': observer,
                 'sun_solo_lt':  SUN-SolO light time in units of seconds 

        """
        utc =stu.anytime(utc)
        return Request.post(ENDPOINTS['FLARE_AUX'], {
            'observer': observer,
            'sunx': flare_x,
            'suny': flare_y,
            'obstime': utc
        })

    @staticmethod
    def request_attitude(begin_utc,
                         end_utc,
                         steps=1,
                         instrument_frame='SOLO_SRF',
                         ref_frame='SOLO_SUN_RTN'):
        """
        request altitude data from stix data center

        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        form = {
            'start_utc': begin_utc,
            'end_utc': end_utc,
            'steps': steps,
            'frame1': instrument_frame,
            'frame2': ref_frame
        }
        ret = Request.post(ENDPOINTS['ATTITUDE'], form)
        return ret

    @staticmethod
    def fetch_science_data(_id: int):
        """fetch science data from stix data center

        Parameters:
            _id: int
                science data unique ID, which can be found on STIX data center bulk science data web page


        Returns:
            science_data: dict
                science data received from data center if success or None if failed

        """
        return Request.post(ENDPOINTS['SCIENCE_DATA'], {
            'id': _id,
        })

    @staticmethod
    def fetch_flare_list(begin_utc, end_utc, sort: str = 'time'):
        """ query and download flare list from stix data center

        Parameters:
        ------
            begin_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                flare start UTC
            end_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                flare end UTC
            sort: str
                key to sort flares. It can be one of ['goes','time', 'LC0','LC1','LC2','LC3','LC4], LCi here means the i-th QL light curve


        Returns:
        -----
            flare_list: dict or None
                flare list if success or None if failed.

        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        return Request.post(ENDPOINTS['FLARE_LIST'], {
            'start_utc': begin_utc,
            'end_utc': end_utc,
            'sort': sort
        })
    @staticmethod
    def fetch_spectrogram(begin_utc, end_utc):
        """ download spectrogram data from stix data center

        Parameters:
        ------
            begin_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                start UTC
            end_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
                end UTC
        Returns:
        -----
            spectrogram: dict 
                A dictionary containing spectrogram data or error message

        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        return Request.post(ENDPOINTS['SPECTROGRAMS'], {
            'begin': begin_utc,
            'end': end_utc
        })

    @staticmethod
    def query_science(begin_utc, end_utc, request_type="all", full = False):
        """ Search for science data 
        Parameters
        ----
            begin_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
              Begin time
            end_utc:  str, datetime, pandas.Timestamp or astropy.time.Time
              End time
            request_type: {'xray-rpd', 'xray-cpd', 'xray-scpd', 'xray-spec', 'all'}, optional 
              science request type. If it is not given, it returns all requests with observation time intersecting  the given time range. 
            full : boolean 
               if True,  the server will  return as much as information as possible
              
              
              
        Returns:
        -------
        dict:  A list of science request metadata 
        """
        begin_utc, end_utc=stu.anytime(begin_utc), stu.anytime(end_utc)
        return Request.post(ENDPOINTS['SCIENCE'], {
            'start': begin_utc,
            'end': end_utc,
            'more': full,
            'request_type':request_type
        })




