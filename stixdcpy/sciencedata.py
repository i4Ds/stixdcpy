#!/usr/bin/python
'''
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
import datetime
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt
from matplotlib import patches

from stixdcpy import net
from stixdcpy import time as st
from stixdcpy import io as sio
from stixdcpy.net import FITSRequest as freq

class ScienceData(sio.IO):
    def __init__(self, request_id, data):
        self.data= data
        self.request_id=request_id
        self.preprocessing()
    def preprocessing(self):
        pass
    @classmethod
    def fetch(cls, request_id):
        request_id=request_id
        data=freq.fetch_bulk_science_by_request_id(request_id)
        return cls(request_id, data)
    @classmethod
    def from_fits(cls,filename):
        request_id=0
        data=fits.open(filename)
        return cls(request_id, data)

    def __getattr__(self, name):
        if name == 'data':
            return self.data
        elif name == 'type':
            return self.data.get('data_type','INVALID_TYPE')
    def get_data(self):
        return self.data

class SciL1(ScienceData):
    '''
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
                '''
    #def __init__(self):
    #    super().__init__(self)


    def preprocessing(self):
        self.counts_data=self.data['DATA'].data
        self.spectrogram=np.sum(self.counts_data['counts'][:,:,:,:],axis=(1,2))
        self.energy_bin_names=[f'{a} - {b}' for a, b in zip(self.data['ENERGIES'].data['e_low'] , self.data[3].data['e_high'])]
        self.ebins_mid=[(a + b)/2. for a, b in zip(self.data[3].data['e_low'] , self.data[3].data['e_high'])]
        self.ebins_low,self.ebins_high=self.data[3].data['e_low'] , self.data[3].data['e_high']
        self.spectrum=np.sum(self.counts_data['counts'][:,:,:,:],axis=(0,1,2))
        self.T0=self.data[0].header['DATE_BEG']



 
    def peek(self):
        '''
        Inputs:

        '''
        if not self.data:
            print(f'Data not loaded. ')
            return None

        fig,ax=plt.subplots(2,2)
        X,Y=np.meshgrid(self.counts_data['time'], self.data[3].data['channel'])
        im=ax[0,0].pcolormesh(X,Y, np.transpose(self.spectrogram)) #pixel summed energy spectrum 
        ax[0,0].set_yticks(self.data[3].data['channel'][::2])
        ax[0,0].set_yticklabels(self.energy_bin_names[::2])
        cbar = fig.colorbar(im,ax=ax[0,0])
        cbar.set_label('Counts')
        ax[0,0].set_title('Spectrogram')
        ax[0,0].set_ylabel('Energy range(keV')
        ax[0,0].set_xlabel(f"Seconds since {self.T0}s ")

        count_rate_spectrogram=self.spectrogram[1:, :]/self.counts_data['timedel'][:-1][:,None]
        ax[0,1].plot(self.counts_data['time'][1:], count_rate_spectrogram)
        #correct
        ax[0,1].set_ylabel('Counts / sec')
        #plt.legend(self.energy_bin_names, ncol=4)
        ax[0,1].set_xlabel(f"Seconds since {self.T0}s ")
        ax[1,0].plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
        #ax.set_xticks(self.data[3].data['channel'])
        ax[1,0].set_xscale('log')
        ax[1,0].set_yscale('log')
        ax[1,0].set_xlabel('Energy (keV)')
        ax[1,0].set_ylabel('Counts')
        ax[1,1].plot(self.counts_data['time'], self.counts_data['timedel'])
        ax[1,1].set_xlabel(f"Seconds since {self.T0}s ")
        ax[1,1].set_ylabel('Integration time (sec)')
        plt.suptitle(f'L1 request #{self.request_id}')

        return fig,ax


    '''
    @classmethod
    def request(cls, request_id:int):
        ob = cls.__new__(cls)
        ob.data=freq.fetch_bulk_science_by_request_id(request_id) 
        return ob
        '''

    @classmethod
    def from_file(cls, filename):
        ob = cls.__new__(cls)
        print('Not implemented yet')
        data=None
        ob.data=data
        return ob


class SciSpectrogram(ScienceData):
    '''
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
                '''
    #def __init__(self):
    #    super().__init__(self)


    def preprocessing(self):
        self.counts_data=self.data['DATA'].data
        self.spectrogram=self.counts_data['counts']
        self.energy_bin_names=[f'{a} - {b}' for a, b in zip(self.data['ENERGIES'].data['e_low'] , self.data[3].data['e_high'])]
        self.ebins_mid=[(a + b)/2. for a, b in zip(self.data[3].data['e_low'] , self.data[3].data['e_high'])]
        self.ebins_low,self.ebins_high=self.data[3].data['e_low'] , self.data[3].data['e_high']
        self.spectrum=np.sum(self.counts_data['counts'], axis=0)
        self.T0=self.data[0].header['DATE_BEG']
 
    def peek(self):
        '''
        Inputs:

        '''
        if not self.data:
            print(f'Data not loaded. ')
            return None

        fig,ax=plt.subplots(2,2)
        X,Y=np.meshgrid(self.counts_data['time'], self.data[3].data['channel'])
        plt.suptitle(f'L4 request #{self.request_id}')
        im=ax[0,0].pcolormesh(X,Y, np.transpose(self.spectrogram)) #pixel summed energy spectrum 
        ax[0,0].set_yticks(self.data[3].data['channel'][::2])
        ax[0,0].set_yticklabels(self.energy_bin_names[::2])
        cbar = fig.colorbar(im,ax=ax[0,0])
        cbar.set_label('Counts')
        ax[0,0].set_title('Spectrogram')
        ax[0,0].set_ylabel('Energy range(keV')
        ax[0,0].set_xlabel(f"Seconds since {self.T0}s ")

        count_rate_spectrogram=self.spectrogram[1:, :]/self.counts_data['timedel'][:-1][:,None]
        ax[0,1].plot(self.counts_data['time'][1:], count_rate_spectrogram)
        #correct
        ax[0,1].set_ylabel('Counts / sec')
        #plt.legend(self.energy_bin_names, ncol=4)
        ax[0,1].set_xlabel(f"Seconds since {self.T0}s ")
        ax[1,0].plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
        #ax.set_xticks(self.data[3].data['channel'])
        ax[1,0].set_xscale('log')
        ax[1,0].set_yscale('log')
        ax[1,0].set_xlabel('Energy (keV)')
        ax[1,0].set_ylabel('Counts')
        ax[1,1].plot(self.counts_data['time'], self.counts_data['timedel'])
        ax[1,1].set_xlabel(f"Seconds since {self.T0}s ")
        ax[1,1].set_ylabel('Integration time (sec)')

        return fig,ax


    '''
    @classmethod
    def request(cls, request_id:int):
        ob = cls.__new__(cls)
        ob.data=freq.fetch_bulk_science_by_request_id(request_id) 
        return ob
        '''

    @classmethod
    def from_file(cls, filename):
        ob = cls.__new__(cls)
        print('Not implemented yet')
        data=None
        ob.data=data
        return ob


