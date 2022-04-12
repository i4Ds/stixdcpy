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
from stixdcpy import io as sio
from stixdcpy.net import FitsQuery as freq
from stixdcpy import instrument as inst
from pathlib import PurePath

FPGA_TAU=10.1e-6
ASIC_TAU=2.63e-6


class ScienceData(sio.IO):
    """
      Retrieve science data from stix data center or load fits file from local storage

    """
    def __init__(self, request_id=None, fname=None):
        self.fname = fname
        self.data_type=None
        if not fname:
            raise Exception("FITS filename not specified")
        self.request_id = request_id
        self.time_shift_applied=0
        self.hdul = fits.open(fname)
        self.energies=[]
        #self.read_data()
    @property
    def url(self):
        req_id=self.request_id if not isinstance(self.request_id, list) else self.request_id[0]
        link=f'{net.HOST}/view/list/bsd/uid/{req_id}'
        return f'<a href="{link}">{link}</a>'

    def read_fits(self, light_time_correction=True):
        """
            Read data  L1 compression level  FITS files
            Parameters
            ---------------------
            light_time_correction: boolean
                Correct light time difference
        """

        self.data = self.hdul['DATA'].data
        self.T0_utc = self.hdul['PRIMARY'].header['DATE_BEG']
        self.counts= self.data['counts']

        self.light_time_del= self.hdul['PRIMARY'].header['EAR_TDEL']
        self.light_time_corrected=light_time_correction

        self.T0_unix = sdt.utc2unix(self.T0_utc)
        self.triggers = self.data['triggers']
        self.rcr = self.data['rcr']

        self.timedel = self.data['timedel']
        self.time = self.data['time']

        if self.is_time_bin_shifted(self.T0_unix):
            self.timedel = self.timedel[:-1]
            self.time = self.time[1:]
            logger.info('Shifted time bins have been corrected automatically!')
            if self.data_type=='ScienceL1':
                self.counts= self.counts[1:, :, :, :]
                self.triggers = self.triggers[1:, :]
                self.rcr = self.rcr[1:]
            elif self.data_type=='Spectrogram':
                self.counts= self.counts[1:, :]
                self.triggers = self.triggers[1:]
                #self.rcr = self.rcr[1:]

        self.request_id = self.hdul['CONTROL'].data['request_id']
        
        self.time_shift_applied=0 if light_time_correction else self.light_time_del
        self.datetime = [
            sdt.unix2datetime(self.T0_unix + x + y * 0.5 + self.time_shift_applied)
            for x, y in zip(self.time, self.timedel)
        ]

        self.duration = self.time[-1] - self.time[0] + (self.timedel[0] +
                                                        self.timedel[-1]) / 2

        self.energies = self.hdul['ENERGIES'].data

        self.energy_bin_names = [
            f'{a} - {b}'
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        self.energy_bin_mask = self.hdul["CONTROL"].data["energy_bin_mask"]

        ebin_nz_idx =self.energy_bin_mask.nonzero()
        self.max_ebin = np.max(ebin_nz_idx)  #indices of the non-zero elements
        self.min_ebin = np.min(ebin_nz_idx)

        self.ebins_mid = [
            (a + b) / 2.
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        self.ebins_low, self.ebins_high = self.energies[
            'e_low'], self.energies['e_high']

        if self.data_type=='ScienceL1':
            self.pixel_counts=self.counts
            self.pixel_count_rates= self.pixel_counts/self.timedel[:,None,None, None]
            self.trigger_rates = self.triggers / self.timedel[:, None] 
        elif self.data_type=='Spectrogram':
            self.count_rates= self.counts/self.timedel[:,None]
            self.trigger_rates = self.triggers / self.timedel


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

    def __init__(self, reqeust_id,fname):
        super().__init__(reqeust_id, fname)
        self.data_type='ScienceL1'
        self.pixel_count_rates=None
        self.correct_pixel_count_rates=None
        self.read_fits()
        self.make_spectra()

    def make_spectra(self, pixel_counts=None):
        if pixel_counts is None:
            pixel_counts=self.pixel_counts
        self.spectrogram = np.sum(pixel_counts, axis=(1, 2))
        self.count_rate_spectrogram = self.spectrogram / self.timedel[:, np.
                                                                      newaxis]
        self.spectrum = np.sum(pixel_counts, axis=(0, 1, 2))
    
        self.mean_pixel_rate_spectra = np.sum(self.pixel_counts,
                                              axis=0) / self.duration
        self.mean_pixel_rate_spectra_err = np.sqrt(
            self.mean_pixel_rate_spectra) / np.sqrt(self.duration)
        #sum over all time bins and then divide them by the duration, counts per second

        self.pixel_total_counts=np.sum(self.pixel_counts, axis=(0,3))

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

    def correct_live_time(self, clone=False):
        """ Live time correction
        Returns:
          scienceL1 object
        """

        trig_tau = FPGA_TAU+ASIC_TAU
        time_bins = self.time_bins[:, None]
        photons_in = self.triggers/(time_bins-trig_tau*self.triggers)
        #photon rate calculated using triggers 
        cm= np.zeros((time_bins.size, 32))
        time_bins = time_bins[:, :, None, None]
        count_rates = self.pixel_counts/time_bins
        for det in range(32):
            trig_idx=inst.detector_id_to_trigger_index(det)

            cm[:,det]= 1 + self.trigger_rates[:,trig_idx]*FPGA_TAU #live time per second 
        self.correct_pixel_count_rates=count_rates*cm[:, :, None, None]/np.exp(-count_rates*ASIC_TAU)
        return self

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
            self.read_fits()
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


    def __init__(self, reqeust_id,fname):
        super().__init__(reqeust_id, fname)
        self.data_type='Spectrogram'

        self.read_fits()

        self.spectrum = np.sum(self.counts, axis=0)

    def peek(self, ax0=None, ax1=None, ax2=None, ax3=None):
        """
            preivew Science data
        Arguments:
        ax0: matplotlib axe 
        ax0: matplotlib axe 
        """
        if not self.hdul:
            logger.error(f'Data not loaded. ')
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
            ax1.plot(self.time, self.count_rates)
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
