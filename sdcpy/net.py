import io
import json
import requests
import numpy as np
from datetime import datetime
from astropy.io import fits
from tqdm import tqdm
from tempfile import NamedTemporaryFile

HOST='https://pub023.cs.technik.fhnw.ch'
#HOST='http://localhost:5000'
URLS_POST={
        'LC':f'{HOST}/api/request/ql/lightcurves',
        'ELUT':f'{HOST}/api/request/eluts',
        'EMPHERIS':f'{HOST}/api/request/ephemeris',
        'SCIENCE':f'{HOST}/api/request/science-data/id',
    }


FITS_TYPES = {
    'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin', 'hkmax'
}

class FITSRequest(object):
    '''Request FITS format data from STIX data center '''
    @staticmethod
    def wget(url: str, desc: str, progress_bar=True,filename=None):
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

    @staticmethod
    def fetch(start_utc, stop_utc, fits_type='lc', progress_bar=True):
        temp_file=FITSRequest.get_fits(start_utc, stop_utc, fits_type, progress_bar)
        try:
            return fits.open(temp_file)
        except:
            print('Invalid request or no data was found')
            return None


    @staticmethod
    def get_fits(start_utc, stop_utc, fits_type='lc', progress_bar=True, filename=None):
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
        temp_file = FITSRequest.wget(url, 'Downloading data', progress_bar, filename)
        return temp_file


class JSONRequest(object):
    '''Request json format data from STIX data center '''
    @staticmethod
    def post(url, form):
        response = requests.post(url, data = form)

        data=response.json()
        if 'error' in data:
            print(data['error'])
            return None
        return data

    @staticmethod
    def fetch_light_curves(begin_utc:str, end_utc:str, ltc:bool):
        form = {
             'begin': begin_utc,
             'ltc':ltc,
             'end':end_utc
            }
        url=URLS_POST['LC']
        return JSONRequest.post(url,form)
    def fetch_onboard_and_true_eluts(utc):
        form = {
             'utc': utc
            }
        url=URLS_POST['ELUT']
        return JSONRequest.post(url,form)

    @staticmethod
    def fetch_empheris(start_utc:str, end_utc:str, steps=1):
        return JSONRequest.post(URLS_POST['EMPHERIS'],{
             'start_utc': start_utc,
             'end_utc': end_utc,
             'steps':steps
            })

    @staticmethod
    def fetch_science_data(_id:int):
        return JSONRequest.post(URLS_POST['SCIENCE'],{
             'id': _id,
            })

