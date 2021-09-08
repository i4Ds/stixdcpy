#!/usr/bin/python
'''
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
import datetime
from matplotlib import pyplot as plt
from astropy.io import fits
from stixdcpy.net import JSONRequest as jreq
from stixdcpy.net import FitsProduct as freq
from stixdcpy import io as sio

class QuickLook(sio.IO):
    def __init__(self):
        pass
    #def save_fits(self,fname):
    #    self.data.writeto(fname)

class LightCurves(QuickLook):
    def __init__(self, data):
        self.data=data

    @classmethod
    def fetch(cls, start_utc:str, end_utc:str, ltc=False):
        data=jreq.fetch_light_curves(start_utc, end_utc, ltc) 
        return cls(data)

    #@classmethod
    #def from_file(cls, filename):
    #    return cls(filename)

    def __getattr__(self, name):
        if name == 'data':
            return self.data
        #elif name == 'filename':
        #    return self.fname

    def get_data(self):
        return self.data

    def peek(self, ax=None, legend_loc='upper right'):
        '''
        Plot light curves
        Parameters:
            ltc: light time correction flag. The default value is False. Do light time correction if ltc=True
        '''

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
