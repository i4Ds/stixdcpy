#!/usr/bin/python
'''
    This module provides APIs to retrieve Housekeeping data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
from matplotlib import pyplot as plt
import datetime
from stixdcpy.net import FITSRequest as freq
from stixdcpy import io as sio

class Housekeeping(sio.IO):
    def __init__(self):
        self.data = None

    @classmethod
    def request(cls, start_utc:str, end_utc:str):
        ob = cls.__new__(cls)
        ob.data=freq.fetch_continuous_data(start_utc, end_utc, 'hkmax') 
        return ob

    @classmethod
    def from_file(cls, filename):
        ob = cls.__new__(cls)
        print('Not implemented yet')
        data=None
        ob.data=data
        return ob


    def __getattr__(self, name):
        if name == 'data':
            return self.data
    def get_data(self):
        return self.data
    def peek(self, ax=None, legend_loc='upper right'):
        if not ax:
            _, ax=plt.subplots()
        dt=[datetime.datetime.utcfromtimestamp(t) for t in self.data['unix_time']]
        for i in range(5):
            plt.plot(dt, self.data['light_curves'][str(i)], label=self.data['energy_bins']['names'][i])
        dlt=self.data['light_time_diff']
        light_time_corrected=self.data['light_time_corrected']
        
        xlabel=f'UTC + {dlt:.2f} (4 sec time bins)' if light_time_corrected else 'UTC (4 sec time bins)'
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Counts')
        ax.legend(loc=legend_loc)
        ax.set_yscale('log')
        return ax
