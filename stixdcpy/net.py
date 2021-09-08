#!/usr/bin/python
'''
    This module provides APIs to retrieve data from STIX data center 
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import io
import os
import json
import hashlib
import requests
import numpy as np
from datetime import datetime
from astropy.io import fits
from tqdm import tqdm
import tempfile

DATA_DIR = None
#default directory to save files received from stix data center
#set to None to use the system temporary folder 

HOST='https://pub023.cs.technik.fhnw.ch'
#HOST='http://localhost:5000'
URLS_POST={
        'LC':f'{HOST}/api/request/ql/lightcurves',
        'ELUT':f'{HOST}/api/request/eluts',
        'EMPHERIS':f'{HOST}/api/request/ephemeris',
        'SCIENCE':f'{HOST}/api/request/science-data/id',
        'transmission':f'{HOST}/api/request/transmission'
    }


FITS_TYPES = {
    'l0', 'l1', 'l2', 'l3', 'spec', 'qlspec', 'asp', 'aspect', 'lc', 'bkg',
    'var', 'ffl', 'cal', 'hkmin', 'hkmax'
}



def download_if_not_exists(filename, url):
    """
    Download a URL to a file if the file
    does not exist already.
    Returns
    -------
    True if the file was downloaded,
    False if it already existed
    """
    if not os.path.exists(filename):
        download_file(filename, url)
        return True
    return False

class FitsProductQueryResult(object):
    def __init__(self,resp):
        self.result=resp
    def __repr__(self):
        return str(self.result)
    def __getitem__(self, index):
        return self.result[index]
    def get_fits_ids(self):
        return [row['fits_id'] for row in self.result]


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
        stream=progress_bar
        resp = requests.get(url, stream=stream)
        if filename is None:
            fname=resp.headers.get("Content-Disposition").split("filename=")[1]
            folder=tempfile.gettempdir() if DATA_DIR is None else DATA_DIR
            if not fname:
                md5hex=hashlib.md5(url.encode('utf-8')).hexdigest()
                fname=f'{md5hex}.fits'
            filename=os.path.join(folder,fname)
        if os.path.exists(filename):
            print(f'Found the data in local storage. Filename: {filename} ...')
            return filename

        f=open(filename,'wb')
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
    def query(start_utc, stop_utc, product_type='lc'):
        if product_type not in FITS_TYPES: 
            raise TypeError(f'Invalid product type! product_type can be one of {str(FITS_TYPES)}') 
        url=f'/query/fits/{start_utc}/{stop_utc}/{product_type}'
        r = requests.get(url).json()
        if isinstance(r,list):
            return FitsProductQueryResult(r)
        return []
    
    @staticmethod
    def fetch_bulk_science_by_request_id(request_id):
        url=f'{HOST}/download/fits/bsd/{request_id}'
        fname=FITSRequest.wget(url, f'Downloading BSD #{request_id}')
        return fits.open(fname),fname

    @staticmethod
    def fetch(query_results):
        fits_ids=[]
        if isinstance(query_results, FitsProductQueryResult):
            fits_ids=query_results.get_fits_ids()
        elif isinstance(query_results,int):
            fits_ids=[query_results]
        elif isinstance(query_results, list):
            try:
                fits_ids=[row['fits_id'] for row in query_results]
            except:
                pass
            if not fits_id:
                try:
                    fits_ids=[row for row in query_results if isinstance(row, int)]
                except:
                    pass
        if not fits_id:
            raise TypeError('Invalid argument type')
        
        fits_handlers=[]
        try:
            for file_id in fits_ids:
                fname=FITSRequest.get_fits(file_id)
                fits_handlers.append(fits.open(fname))
        except Exception as e:
            raise e
        return fits_handlers

    @staticmethod
    def get_fits(fits_id,  progress_bar=True, filename=None):
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
        url = f'{HOST}/download/fits/{file_id}'
        fname = FITSRequest.wget(url, 'Downloading data', progress_bar, filename)
        return fname

    @staticmethod
    def fetch_continuous_data(start_utc, end_utc, data_type):
        if data_type not in ['hkmax','lc','var','qlspec','bkg']:
            raise TypeError(f'Data type {data_type} not supported!')
        url=f'{HOST}/create/fits/{start_utc}/{end_utc}/{data_type}'
        fname = FITSRequest.wget(url, 'Downloading data', True, None)
        return fits.open(fname)

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

