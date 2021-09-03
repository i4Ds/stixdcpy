#!/usr/bin/python
'''
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
from matplotlib import pyplot as plt
from matplotlib import patches
import datetime
from sdcpy import net
from sdcpy import time as st
from sdcpy import io as sio
from sdcpy.net import FITSRequest as freq

class ScienceData(sio.IO):
    def __init__(self, entry_id=None):
        self.data=None
        if entry_id is not None:
            self.fetch(entry_id)
    def fetch(self, entry_id):
        self.entry_id=entry_id
        self.data=net.fetch_science_data(entry_id)
    def __getattr__(self, name):
        if name == 'data':
            return self.data
        elif name == 'type':
            return self.data.get('data_type','INVALID_TYPE')
    def get_data(self):
        return self.data

class SciL1(ScienceData):
    def __init__(self, entry_id=None):
        super().__init__(entry_id)
        if self.data.get('data_type',None)!='L1':
            raise TypeError('The requested data is not L1')
    def info(self):
        return {
                'OBS_BEGIN': st.unix2utc(self.data['start_unix']),
                'OBS_END': st.unix2utc(self.data['end_unix']),
                'ID':self.entry_id,
                'URL':f'{net.HOST}/view/list/bsd/id/{entry_id}',
                }
    
    def peek(self, ax=None):
        if not self.data:
            print(f'Data not loaded. ')
            return None
        if not ax:
            _, ax=plt.subplots()
        if not data or 'error' in data:
            print(f'Data not available. ')
            return None
        return ax
