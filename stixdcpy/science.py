#!/usr/bin/python
"""
    This module provides APIs to retrieve Quick-look data from STIX data center , and provides tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021
"""
import datetime
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt
from stixdcpy import time as sdt
from stixdcpy.logger import logger
from stixdcpy import io as sio, net
from stixdcpy.net import FitsQuery as freq
from pathlib import PurePath


class ScienceData(sio.IO):
    """
      Retrieve science data from stix data center or load fits file from local storage

    """
    def __init__(self, request_id, fname):
        self.fname = fname
        self.request_id = request_id
        self.hdul = fits.open(fname)
        self.energies=[]
        self.load()
        if self.request_id is None:
            self.request_id = self.hdul['CONTROL'].data['request_id']
        #self.read_data()
    @property
    def url(self):
        link=f'{net.HOST}/view/list/bsd/uid/{self.request_id}'
        return f'<a href="{link}">{link}</a>'

    def is_time_bin_shifted(self, unix_time):
        """
            Time bins are shifted in the data collected before 2021-12-09 due a bug in the flight software

            Check if time bin is shifted in L1 data
            Parameters
                unix_time: float 
            Returns
                is_shifted: bool
                    True if time bin is shifted else False
        """

        return (unix_time < sdt.utc2unix('2021-12-09T14:00:00'))

    def load(self):
        '''
        load data object and extract basic information from science fits file
        Code to be executed after a science data file is being loaded.
        
        '''
        pass

    @classmethod
    def from_sdc(cls, request_id):
        '''
        download science data file from stix data center
        Parameters
        ------
        request_id :  int
            bulk science data request unique ID; Unique IDs can be found on the science data web page  at stix data center


        Returns
        ------
            science data class object

        '''
        request_id = request_id
        fname = freq.fetch_bulk_science_by_request_id(request_id)
        return cls(request_id, fname)

    @classmethod
    def from_fits(cls, filename):
        """
        factory class
        Arguments
        filename: str
            FITS filename
        """
        request_id = None
        return cls(request_id, filename)

    def get_energy_range_slicer(self, elow, ehigh):
        sel=[]
        i=0
        for a, b in zip(self.energies['e_low'], self.energies['e_high']):
            if a>=elow  and b<=ehigh:
                sel.append(i)
            i+=1
        return slice(min(sel),max(sel))



    def rebin(self, ebins, min_tbin=0):
        """
         Energy rebin and time rebin
         Arguments:
         ebins: list or numpy array
            energy bin range in units of keV
         min_tbin: float
            minimum time bin, shorter time bins are merged
         Returns:
            an object containing rebinned light curves
        """
        pass

    def save(self, filename=None):
        '''
           Save data to a fits file
           Parameters
           filename : output fits filename
           Returns
           filename if success or error message
        '''
        if not isinstance(self.hdul, fits.hdu.hdulist.HDUList):
            logger.error('The data object is a not a fits hdu object!')
            return None
        try:
            if filename is None:
                basename = self.hdul['PRIMARY'].header['FILENAME']
                filename = PurePath(net.DOWNLOAD_PATH, basename)
            self.hdul.writeto(filename)
            return filename
        except Exception as e:
            logger.error(e)

    def __getattr__(self, name):
        if name == 'data':
            return self.hdul
        elif name == 'type':
            return self.hdul.get('data_type', 'INVALID_TYPE')
        elif name == 'filename':
            return self.fname

    def get_data(self):
        return self.hdul


class ScienceL1(ScienceData):
    """
    Tools to analyze L1 science data
    """

    #duration: Union[float, Any]

    def load(self, tbin_correction='auto'):
        """
            Read data  L1 compression level  FITS files
            Parameters
                tbin_correction: str or bool
                    Correct the time bin bug in FSW with versions < v183 if it is not False

        """
        self.data = self.hdul['DATA'].data
        self.T0_utc = self.hdul['PRIMARY'].header['DATE_BEG']
        self.T0_unix = sdt.utc2unix(self.T0_utc)
        self.triggers = self.data['triggers']
        self.rcr = self.data['rcr']

        self.counts = self.data['counts']
        self.timedel = self.data['timedel']
        self.time = self.data['time']

        if tbin_correction != False and self.is_time_bin_shifted(self.T0_unix):
            self.counts = self.counts[1:, :, :, :]
            self.timedel = self.timedel[:-1]
            self.time = self.time[1:]
            print('Shifted time bins corrected')
            self.triggers = self.triggers[1:, :]
            self.rcr = self.rcr[1:]

        self.trigger_rates = self.triggers / self.timedel[:, None]

        self.datetime = [
            sdt.unix2datetime(self.T0_unix + x + y * 0.5)
            for x, y in zip(self.time, self.timedel)
        ]
        self.spectrogram = np.sum(self.counts, axis=(1, 2))
        self.count_rate_spectrogram = self.spectrogram / self.timedel[:, np.
                                                                      newaxis]

        self.energies = self.hdul['ENERGIES'].data
        #print(self.hdul['ENERGIES'].header)
        self.energy_bin_names = [
            f'{a} - {b}'
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        self.energy_bin_mask = self.hdul["CONTROL"].data["energy_bin_mask"]

        self.inverse_energy_bin_mask = 1 - self.energy_bin_mask
        ebin_nz_idx =self.energy_bin_mask.nonzero()
        self.max_ebin = np.max(ebin_nz_idx)  #indices of the non-zero elements
        self.min_ebin = np.min(ebin_nz_idx)

        self.ebins_mid = [
            (a + b) / 2.
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        self.ebins_low, self.ebins_high = self.energies[
            'e_low'], self.energies['e_high']
        self.spectrum = np.sum(self.counts, axis=(0, 1, 2))
        self.duration = self.time[-1] - self.time[0] + (self.timedel[0] +
                                                        self.timedel[-1]) / 2
        self.mean_pixel_rate_spectra = np.sum(self.counts,
                                              axis=0) / self.duration
        self.mean_pixel_rate_spectra_err = np.sqrt(
            self.mean_pixel_rate_spectra) / np.sqrt(self.duration)
        #sum over all time bins and then divide them by the duration, counts per second
    def solve_cfl(self, start_utc, end_utc, elow=0, eup=31, ax=None):
        """calculate flare location using the online flare location solver.
          
        Args:
            start_utc: str
                ROI start time
            end_utc: str
                ROI end time
            elow: int
                ROI lower energy limit (science channel). 
            eup: int
                ROI upper energy limit (science channel). 
        Returns:
            cfl_loc: dict
                containing coarse flare location as well as ephemeris and chisquare map

        """
        pass
        

    def peek(self,
             plots=['spg', 'lc', 'spec', 'tbin', 'qllc'],
             ax0=None,
             ax1=None,
             ax2=None,
             ax3=None):
        """
            Create quick-look plots for the loaded science data
        """
        if not self.hdul:
            logger.logger(f'Data not loaded. ')
            return None
        if isinstance(plots, str) and plots:
            plots = plots.split(',')
        if not self.data_loaded:
            self.load()
            self.data_loaded = True

        if 'spg' in plots:
            if not ax0:
                _, ax0 = plt.subplots()
            X, Y = np.meshgrid(self.time,
                               np.arange(self.min_ebin, self.max_ebin))
            im = ax0.pcolormesh(
                X, Y,
                np.transpose(
                    self.count_rate_spectrogram[:, self.min_ebin:self.max_ebin]
                ))  #pixel summed energy spectrum
            ax0.set_yticks(
                self.energies['channel'][self.min_ebin:self.max_ebin:2])
            ax0.set_yticklabels(
                self.energy_bin_names[self.min_ebin:self.max_ebin:2])
            fig = plt.gcf()
            cbar = fig.colorbar(im, ax=ax0)
            cbar.set_label('Counts')
            ax0.set_title('Count rate spectrogram')
            ax0.set_ylabel('Energy range(keV')
            ax0.set_xlabel(f"T0 at {self.T0_utc} ")
        if 'lc' in plots or 'qllc' in plots:
            if not ax1:
                _, ax1 = plt.subplots()
            self.count_rate_spectrogram = self.spectrogram / self.timedel[:,
                                                                          None]
            if 'qllc' in plots:
               ql_ebins=[(4, 10),(10 ,15 ),(15 ,25 ),(25 ,50), (50 ,84)]
               labels=('4 - 10 keV','10 - 15 keV','15 - 25 keV','25 - 50 keV', '50 - 84 keV')
               ql_sci_ebins=[self.get_energy_range_slicer(s[0],s[1]) for s in ql_ebins]
               for ebin_slicer,label in zip(ql_sci_ebins, labels):
                   ax1.plot(self.time,
                        np.sum(self.count_rate_spectrogram[:, ebin_slicer], axis=1),label=label) 
                   ax1.set_title(f'Detector summed count rates (L1 request #{self.request_id})')
            else:
                ax1.plot(
                    self.time,
                    self.count_rate_spectrogram[:, self.min_ebin:self.max_ebin])
            #correct
            ax1.set_ylabel('counts / sec')
            #plt.legend(self.energy_bin_names, ncol=4)
            ax1.set_yscale('log')
            ax1.set_xlabel(f"seconds since {self.T0_utc} ")
            plt.legend()
        if 'spec' in plots:
            if not ax2:
                _, ax2 = plt.subplots()
            ax2.plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
            #ax.set_xticks(self.data[3].data['channel'])
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.set_xlabel('Energy (keV)')
            ax2.set_ylabel('Counts')
        if 'tbin' in plots:
            if not ax3:
                _, ax3 = plt.subplots()
            ax3.plot(self.time, self.timedel)
            ax3.set_xlabel(f"T0 at {self.T0_utc} ")
            ax3.set_ylabel('Integration time (sec)')
            plt.suptitle(f'L1 request #{self.request_id}')

        #plt.tight_layout()
        return ax0, ax1, ax2, ax3


class Spectrogram(ScienceData):
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


    def load(self, tbin_correction='auto'):
        """
         Load data from fits file

        """
        self.data = self.hdul['DATA'].data
        self.counts = self.data['counts']
        self.time = self.data['time']
        self.timedel = self.data['timedel']

        self.T0 = self.hdul[0].header['DATE_BEG']
        self.T0_unix = sdt.utc2unix(self.T0)

        if tbin_correction != False and self.is_time_bin_shifted(self.T0_unix):
            self.counts = self.counts[1:, :]  #1st d: timebin, second: energies
            self.timedel = self.timedel[:
                                        -1]  #remove the first integration time from the time bin array
            self.time = self.time[1:]
            self.T0 = self.T0[1:]
            print('Shifted time bins corrected')
        else:
            print('No need of time-bin correction')

        self.datetime = [
            sdt.unix2datetime(self.T0_unix + x + y * 0.5)
            for x, y in zip(self.time, self.timedel)
        ]
        self.energy_bin_names = [
            f'{a} - {b}' for a, b in zip(self.hdul['ENERGIES'].data['e_low'],
                                         self.hdul['ENERGIES'].data['e_high'])
        ]
        self.ebins_mid = [(a + b) / 2.
                          for a, b in zip(self.hdul['ENERGIES'].data['e_low'],
                                          self.hdul['ENERGIES'].data['e_high'])
                          ]
        self.ebins_low, self.ebins_high = self.hdul['ENERGIES'].data[
            'e_low'], self.hdul['ENERGIES'].data['e_high']
        self.spectrum = np.sum(self.counts, axis=0)
        self.count_rate_spectrogram = self.counts / self.timedel[:, np.newaxis]

    def peek(self, ax0=None, ax1=None, ax2=None, ax3=None):
        """
            preivew Science data
        Arguments:
        ax0: matplotlib axe 
        ax0: matplotlib axe 
        """
        if not self.hdul:
            print(f'Data not loaded. ')
            return None

        #((ax0, ax1), (ax2, ax3))=axs
        if not any([ax0, ax1, ax2, ax3]):
            _, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2, figsize=(8, 6))

        if ax0:
            X, Y = np.meshgrid(self.time,
                               self.hdul['ENERGIES'].data['channel'])
            im = ax0.pcolormesh(X, Y, np.transpose(
                self.counts))  #pixel summed energy spectrum
            ax0.set_yticks(self.hdul['ENERGIES'].data['channel'][::2])
            ax0.set_yticklabels(self.energy_bin_names[::2])
            fig = plt.gcf()
            cbar = fig.colorbar(im, ax=ax0)
            cbar.set_label('Counts')
            ax0.set_title('Spectrogram')
            ax0.set_ylabel('Energy range(keV')
            ax0.set_xlabel(f"Seconds since {self.T0}s ")
        if ax1:
            #convert to 2d
            ax1.plot(self.time, self.count_rate_spectrogram)
            ax1.set_yscale('log')
            ax1.set_ylabel('Counts / sec')
            ax1.set_xlabel(f"Seconds since {self.T0}s ")
        if ax2:
            ax2.plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.set_xlabel('Energy (keV)')
            ax2.set_ylabel('Counts')
        if ax3:
            ax3.plot(self.time, self.timedel)
            ax3.set_xlabel(f"Seconds since {self.T0}s ")
            ax3.set_ylabel('Integration time (sec)')
        plt.suptitle(f'L4 request #{self.request_id}')
        plt.tight_layout()
        return fig, ((ax0, ax1), (ax2, ax3))
