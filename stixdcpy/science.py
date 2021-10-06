#!/usr/bin/python
"""
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""
from typing import Union, Any

import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt
from stixdcpy import time as sdt
from stixdcpy.logger import logger
from stixdcpy import io as sio, net
from stixdcpy.net import FitsProduct as freq
from pathlib import  PurePath


class ScienceData(sio.IO):
    """
      Retrieve science data from stix data center or load fits file from local storage

    """
    def __init__(self, request_id, fname):
        self.fname=fname
        self.request_id=request_id
        self.data= fits.open(fname)
        if self.request_id is None:
            try:
                self.request_id=self.data['CONTROL'].data['request_id']
            except :
                pass
        self.read_data()
    
    def read_data(self):
        '''
        Read data object and extract basic information from science fits file
        Code to be executed after a science data file is being loaded.
        
        '''
        pass
    @classmethod
    def fetch(cls, request_id):
        '''
        Fetch science data file from stix data center
        Parameters
        ------
        request_id : bulk science data request unique ID; Unique IDs can be found on the science data web page  at stix data center


        Returns
        ------
        FITS file object

        '''
        request_id=request_id
        fname=freq.fetch_bulk_science_by_request_id(request_id)
        return cls(request_id, fname)
    @classmethod
    def from_fits(cls,filename):
        request_id= None
        return cls(request_id, filename)

    def save(self, filename=None):
        '''
           Save data to a fits file
           Parameters
           filename : output fits filename
           Returns
           filename if success or error message
        '''
        if not isinstance(self.data, fits.hdu.hdulist.HDUList):
            logger.error('The data object is a not a fits hdu object!')
            return None
        try:
            if filename is None:
                basename=self.data['PRIMARY'].header['FILENAME']
                filename=PurePath(net.DOWNLOAD_PATH, basename)
            self.data.writeto(filename)
            return filename
        except Exception as e:
            logger.error(e)



    def __getattr__(self, name):
        if name == 'data':
            return self.data
        elif name == 'type':
            return self.data.get('data_type','INVALID_TYPE')
        elif name == 'filename':
            return self.fname

    def get_data(self):
        return self.data

class L1Product(ScienceData):
    """
    Tools to analyze L1 science data
    """
    #duration: Union[float, Any]

    def read_data(self):
        self.data_frame=self.data['DATA'].data
        self.counts = self.data_frame['counts']
        self.timedel=self.data_frame['timedel']
        self.time=self.data_frame['time']
        self.spectrogram = np.sum(self.counts, axis=(1, 2))
        self.count_rate_spectrogram = self.spectrogram / self.timedel[:, None]
        self.energies = self.data['ENERGIES'].data
        #print(self.data['ENERGIES'].header)
        self.energy_bin_names=[f'{a} - {b}' for a, b in zip(self.energies['e_low'] , 
                                                            self.energies['e_high'])]
        self.energy_bin_mask=self.data["CONTROL"].data["energy_bin_mask"]
        
        self.inverse_energy_bin_mask=1-self.energy_bin_mask
        self.max_ebin = np.max(ebin_nz_idx := self.energy_bin_mask.nonzero()) #indices of the non-zero elements
        self.min_ebin = np.min(ebin_nz_idx)

        self.ebins_mid=[(a + b)/2. for a, b in zip(self.energies['e_low'] , self.energies['e_high'])]
        self.ebins_low,self.ebins_high=self.energies['e_low'] , self.energies['e_high']
        self.spectrum=np.sum(self.counts,axis=(0,1,2))
        self.T0_utc=self.data['PRIMARY'].header['DATE_BEG']
        self.T0_unix=sdt.utc2unix(self.T0_utc)
        self.duration=self.time[-1]-self.time[0]+(self.timedel[0]+self.timedel[-1])/2
        self.mean_pixel_rate_spectra=np.sum(self.counts,axis=0)/self.duration
        self.mean_pixel_rate_spectra_err=np.sqrt(self.mean_pixel_rate_spectra)/np.sqrt(self.duration)
        #sum over all time bins and then divide them by the duration, counts per second 


    def peek(self, ax0=None, ax1=None, ax2=None, ax3=None):
        """
            Create quick-look plots for the loaded science data
        """
        if not self.data:
            logger.logger(f'Data not loaded. ')
            return None

        if not any([ax0, ax1, ax2,ax3]):
            _,((ax0,ax1),(ax2,ax3))=plt.subplots(2,2)

        print(self.min_ebin,self.max_ebin)
        print(self.min_ebin,self.max_ebin)

        if ax0:
            X, Y = np.meshgrid(self.time, np.arange(self.min_ebin, self.max_ebin))
            im=ax0.pcolormesh(X,Y, np.transpose(self.count_rate_spectrogram[:,self.min_ebin:self.max_ebin])) #pixel summed energy spectrum
            ax0.set_yticks(self.energies['channel'][self.min_ebin:self.max_ebin:2])
            ax0.set_yticklabels(self.energy_bin_names[self.min_ebin:self.max_ebin:2])
            fig=plt.gcf()
            cbar = fig.colorbar(im,ax=ax0)
            cbar.set_label('Counts')
            ax0.set_title('Count rate spectrogram')
            ax0.set_ylabel('Energy range(keV')
            ax0.set_xlabel(f"Seconds since {self.T0}s ")
        if ax1:
            self.count_rate_spectrogram=self.spectrogram/self.timedel[:,None]
            ax1.plot(self.time, self.count_rate_spectrogram[:,self.min_ebin:self.max_ebin])
            #correct
            ax1.set_ylabel('Counts / sec')
            #plt.legend(self.energy_bin_names, ncol=4)
            ax1.set_xlabel(f"Seconds since {self.T0}s ")
        if ax2:
            ax2.plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
            #ax.set_xticks(self.data[3].data['channel'])
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.set_xlabel('Energy (keV)')
            ax2.set_ylabel('Counts')
        if ax3:
            ax3.plot(self.time, self.timedel)
            ax3.set_xlabel(f"Seconds since {self.T0}s ")
            ax3.set_ylabel('Integration time (sec)')
            plt.suptitle(f'L1 request #{self.request_id}')

        return fig,((ax0,ax1),(ax2,ax3))

class SpectrogramProduct(ScienceData):
    """
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
                """
    #def __init__(self):
    #    super().__init__(self)


    def read_data(self):
        self.data_frame=self.data['DATA'].data
        self.spectrogram=self.data_frame['counts']
        self.energy_bin_names=[f'{a} - {b}' for a, b in zip(self.data['ENERGIES'].data['e_low'] , self.data[3].data['e_high'])]
        self.ebins_mid=[(a + b)/2. for a, b in zip(self.data[3].data['e_low'] , self.data[3].data['e_high'])]
        self.ebins_low,self.ebins_high=self.data[3].data['e_low'] , self.data[3].data['e_high']
        self.spectrum=np.sum(self.data_frame['counts'], axis=0)
        self.T0=self.data[0].header['DATE_BEG']
 
    def peek(self, ax0=None, ax1=None, ax2=None, ax3=None):
        """
        Create quicklook plots for the loaded science data
        """
        if not self.data:
            print(f'Data not loaded. ')
            return None
        #((ax0, ax1), (ax2, ax3))=axs
        if not any([ax0, ax1, ax2,ax3]):
            _,((ax0,ax1),(ax2,ax3))=plt.subplots(2,2)


        if ax0:
            X, Y = np.meshgrid(self.data_frame['time'], self.data[3].data['channel'])
            im=ax0.pcolormesh(X,Y, np.transpose(self.spectrogram)) #pixel summed energy spectrum
            ax0.set_yticks(self.data[3].data['channel'][::2])
            ax0.set_yticklabels(self.energy_bin_names[::2])
            fig=plt.gcf()
            cbar = fig.colorbar(im,ax=ax0)
            cbar.set_label('Counts')
            ax0.set_title('Spectrogram')
            ax0.set_ylabel('Energy range(keV')
            ax0.set_xlabel(f"Seconds since {self.T0}s ")
        if ax1:
            count_rate_spectrogram=self.spectrogram[1:, :]/self.data_frame['timedel'][:-1][:,None]
            ax1.plot(self.data_frame['time'][1:], count_rate_spectrogram)
            ax1.set_ylabel('Counts / sec')
            ax1.set_xlabel(f"Seconds since {self.T0}s ")
        if ax2:
            ax2.plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.set_xlabel('Energy (keV)')
            ax2.set_ylabel('Counts')
        if ax3:
            ax3.plot(self.data_frame['time'], self.data_frame['timedel'])
            ax3.set_xlabel(f"Seconds since {self.T0}s ")
            ax3.set_ylabel('Integration time (sec)')
        plt.suptitle(f'L4 request #{self.request_id}')
        return fig,((ax0,ax1),(ax2,ax3))

