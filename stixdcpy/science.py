#!/usr/bin/python
"""
    This module provides APIs to retrieve Quick-look data from STIX data center , and provides tools to display the data

"""
import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.table import Table
import warnings
from matplotlib import pyplot as plt
from stixdcpy import time_util as sdt
from stixdcpy.logger import logger
from stixdcpy import io as sio
from stixdcpy.net import FitsQuery as freq
from stixdcpy import net as net
from stixdcpy import instrument as inst
from pathlib import PurePath
from datetime import datetime as dt
from datetime import timedelta as td

BETA = 0.94
FPGA_TAU = 10.04e-6
ASIC_TAU = 2.58e-6 # 20 ns uncertainty in FPGA
#updated on July 4, 2023, based on measurements with the ground unit by Olivier, Hualin, Stefan and Sam
TRIG_TAU = FPGA_TAU + ASIC_TAU
# STIX detector parameters


class ScienceData(sio.IO):
    """
      Retrieve science data from stix data center or load fits file from local storage

    """

    def __init__(self, fname=None, request_id=None):
        self.fname = fname
        self.data_type = None
        if not fname:
            raise Exception("FITS filename not specified")
        self.request_id = request_id
        self.time_shift_applied = 0
        self.hdul = fits.open(fname)
        self.energies = []
        self.corrected = None
        # self.read_data()
        self.skm = {}

    @property
    def url(self):
        req_id = self.request_id if not isinstance(
            self.request_id, list) else self.request_id[0]
        link = f'{net.HOST}/view/list/bsd/uid/{req_id}'
        return f'<a href="{link}">{link}</a>'

    
    @property
    def trigger_error(self):
        try:
            trig_err=self.hdul['data'].data['triggers_comp_err']
        except KeyError:
            trig_err=self.hdul['data'].data['triggers_err']

        return error_computation(trig_err,
                                 self.triggers)

    @property
    def filename(self):
        return self.fname


    def init_skm(self):
        try:
            self.skm={'counts':self.hdul['CONTROL'].data['compression_scheme_counts_skm'],
                    'triggers':self.hdul['CONTROL'].data['compression_scheme_triggers_skm']
                    }
        except (KeyError,TypeError, ValueError):
            pass


    def read_fits(self, light_time_correction=True):
        """
            Read data  L1 compression level  FITS files
            Parameters
            ---------------------
            light_time_correction: boolean
                Correct light time difference
        """

        self.data = self.hdul['DATA'].data
        try:
            # L1
            self.T0_utc = self.hdul['PRIMARY'].header['DATE-BEG']
        except KeyError:
            self.T0_utc = self.hdul['PRIMARY'].header['DATE_BEG']
        self.counts = self.data['counts']
        # counts is a 4d array:  time_bin_index, detector, pixel, energy

        self.light_time_del = self.hdul['PRIMARY'].header['EAR_TDEL']
        self.light_time_corrected = light_time_correction

        self.T0_unix = sdt.utc2unix(self.T0_utc)
        self.triggers = self.data['triggers']
        self.rcr = self.data['rcr']

        self.timedel = self.data['timedel']
        self.time = self.data['time']

        if self.is_time_bin_shifted(self.T0_unix) and len(self.timedel) > 1:
            self.timedel = self.timedel[:-1]
            self.time = self.time[1:]
            logger.info('Shifted time bins have been corrected automatically!')
            if self.data_type == 'PixelData':
                self.counts = self.counts[1:, :, :, :]
                self.triggers = self.triggers[1:, :]
                self.rcr = self.rcr[1:]
            elif self.data_type == 'Spectrogram':
                self.counts = self.counts[1:, :]
                self.triggers = self.triggers[1:]
                # self.rcr = self.rcr[1:]

        self.request_id = self.hdul['CONTROL'].data['request_id']

        self.time_shift_applied = 0 if light_time_correction else self.light_time_del
        self.datetime = [
            sdt.unix2datetime(self.T0_unix + x + y * 0.5 +
                              self.time_shift_applied)
            for x, y in zip(self.time, self.timedel)
        ]

        self.duration = self.time[-1] - self.time[0] + (self.timedel[0] +
                                                        self.timedel[-1]) / 2

        self.energies = self.hdul['ENERGIES'].data

        self.energy_bin_names = [
            f'{a} - {b}'
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        try:
            self.energy_bin_mask = self.hdul["CONTROL"].data["energy_bin_edge_mask"]
        except KeyError:
            self.energy_bin_mask = self.hdul["CONTROL"].data["energy_bin_mask"]

        self.inversed_energy_bin_mask = 1 - self.energy_bin_mask

        ebin_nz_idx = self.energy_bin_mask.nonzero()
        self.max_ebin = np.max(ebin_nz_idx)  # indices of the non-zero elements
        self.min_ebin = np.min(ebin_nz_idx)

        self.ebins_mid = [
            (a + b) / 2.
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        self.ebins_low, self.ebins_high = self.energies[
            'e_low'], self.energies['e_high']

        if self.data_type == 'PixelData':
            self.pixel_counts = self.counts
            self.pixel_count_rates = self.pixel_counts / self.timedel[:, None,
                                                                      None,
                                                                      None]
            self.trigger_rates = self.triggers / self.timedel[:, None]
        elif self.data_type == 'Spectrogram':
            self.count_rates = self.counts / self.timedel[:, None]
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
    def from_sdc(cls, request_id, level='L1'):
        '''
        download science data file from stix data center
        Parameters
        ------
        request_id :  int
            bulk science data request unique ID; Unique IDs can be found on the science data web page  at stix data center
        level:  str
            ground processing level. Options: L1, L1A, L2 or any. Default value is L1A


        Returns
        ------
            science data class object
        '''
        # request_id = request_id
        fname = freq.fetch_bulk_science_by_request_id(request_id, level)
        return cls(fname, request_id)

    @classmethod
    def from_fits(cls, filename):
        """
        factory class
        Arguments:
        filename: str
            FITS filename
        """
        request_id = None
        return cls(filename, request_id)

    def get_energy_range_slicer(self, elow, ehigh):
        sel = []
        i = 0
        for a, b in zip(self.energies['e_low'], self.energies['e_high']):
            if a >= elow and b <= ehigh:
                sel.append(i)
            i += 1
        return slice(min(sel), max(sel))

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
            self.hdul.writeto(filename, overwrite=True)
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


class PixelData(ScienceData):
    """
    Tools to analyze STIX pixel data
    """

    def __init__(self, fname, request_id, ltc=False):
        super().__init__(fname, request_id)
        self.data_type = 'PixelData'
        self.pixel_count_rates = None
        self.correct_pixel_count_rates = None
        self.read_fits(light_time_correction=ltc)
        self.make_spectra()
    

    def make_spectra(self, pixel_counts=None):
        if pixel_counts is None:
            pixel_counts = self.pixel_counts
        # integrate detector and pixel
        self.spectrogram = np.sum(pixel_counts, axis=(1, 2))
        self.count_rate_spectrogram = self.spectrogram / self.timedel[:, np.
                                                                      newaxis]
        self.spectrum = np.sum(pixel_counts, axis=(0, 1, 2))

        self.mean_pixel_rate_spectra = np.sum(self.pixel_counts,
                                              axis=0) / self.duration
        self.mean_pixel_rate_spectra_err = np.sqrt(
            self.mean_pixel_rate_spectra) / np.sqrt(self.duration)
        # sum over all time bins and then divide them by the duration, counts per second

        self.pixel_total_counts = np.sum(self.pixel_counts, axis=(0, 3))

    @property
    def pixel_counts_error(self):
        try:
            counts_err=self.hdul['data'].data['counts_err']
        except KeyError:
            counts_err=self.hdul['data'].data['counts_comp_err']
        return error_computation(counts_err,
                                 self.pixel_counts)

    

    def correct_dead_time(self):
        """ dead time correction
        Returns:
          corrected_counts: tuple
          the tuple has four elements:
              corrected_rate: np.array
              count_rates:  np.array
              photon_in: np.array
              live_ratio: np.array
        """

        def correct(triggers, counts_arr, counts_err_arr, time_bins):
            """ Live time correction
            Args
                triggers: ndarray
                    triggers in the spectrogram
                counts_arr:ndarray
                    counts in the spectrogram
                counts_err_arr:ndarray
                    counts error in the spectrogram
                time_bins: ndarray
                    time_bins in the spectrogram
            Returns
            live_time_ratio: ndarray
                live time ratio of detectors
            corrected_rates:
                corrected count rate
            count_rate:
                count rate before dead time correction
            time:
                timestamp
            photons_in:
                rate of photons illuminating the detector group
            corrected_counts:
                dead-time corrected counts 
            """

            time_bins = time_bins[:, None]
            photons_in = triggers / (time_bins - TRIG_TAU * triggers)
            # photon rate calculated using triggers

            live_ratio = np.zeros((time_bins.size, 32))
            time_bins = time_bins[:, :, None, None]

            count_rate = counts_arr / time_bins
            count_rate_err = counts_err_arr / time_bins
            # print(counts_arr.shape)
            for det in range(32):
                trig_idx = inst.detector_id_to_trigger_index(det)
                nin = photons_in[:, trig_idx]
                live_ratio[:, det] = np.exp(
                    -BETA * nin * ASIC_TAU) / (1 + nin * TRIG_TAU)



            #live_ratio=np.zeros_like(live_ratio)+1
            #disable live time correction

            corrected_rate = count_rate / live_ratio[:, :, None, None]

            corrected_rate_err = count_rate_err / live_ratio[:, :, None, None]

            corrected_counts = corrected_rate * time_bins
            corrected_counts_err = corrected_rate_err * time_bins

            return {
                'corrected_rates': corrected_rate,
                'corrected_rate_err': corrected_rate_err,
                'count_rate': count_rate,
                'photons_in': photons_in,
                'corrected_counts':corrected_counts,
                'corrected_counts_err':corrected_counts_err,
                'time': self.datetime, 
                'time_bins': time_bins.flatten(), 
                'live_ratio': live_ratio
            }

        self.corrected = correct(self.triggers, self.pixel_counts, self.pixel_counts_error,
                                 self.timedel)

        # approximate the live ratio error like Ewan does
        above = correct(self.triggers + self.trigger_error, self.pixel_counts,self.pixel_counts_error,
                        self.timedel)
        below = correct(self.triggers - self.trigger_error, self.pixel_counts,self.pixel_counts_error,
                        self.timedel)
        self.corrected['live_error'] = np.abs(above['live_ratio'] -
                                              below['live_ratio']) / 2
        return self.corrected
    def get_sum_counts(self, start_utc=None, end_utc=None) :
        """
        Calculate the total counts in different regions of a pixel data file within a specified time range.

        Parameters:
        - start_utc (str or None, optional): The start time in UTC format. If not provided, the beginning of the observation is used.
        - end_utc (str or None, optional): The end time in UTC format. If not provided, the end of the observation is used.

        Returns:
        - dict: A dictionary containing total counts in different regions:
            - 'top': Total counts in the top row(channels 1-4).
            - 'bottom': Total counts in the bottom row(channels 5-8).
            - 'small': Total counts in the small pixels.
            - 'total': Total counts, sum of 'top' and 'bottom'.
        Note:
        - The function relies on external modules 'sci' and 'st' for pixel data manipulation and time conversions.
        - The time range for counts calculation is determined by start_utc and end_utc. 
            If these are not provided, the entire observation duration is considered.
        """
        cl1=self.correct_dead_time()
        data_start=self.T0_unix
        data_end=self.T0_unix+self.duration
        pixel_counts=cl1['corrected_counts']
        pixel_counts_err=cl1['corrected_counts_err']

        if start_utc is None and end_utc is None:
            start_i_tbin, end_i_tbin=0, pixel_counts.shape[0]-1
            duration = self.duration

        else:
            start_unix=sdt.utc2unix(start_utc) 
            end_unix=sdt.utc2unix(end_utc) 
            if start_unix > data_end or end_unix < data_start:
                return None

            start_unix=max(data_start, start_unix)
            end_unix=min(data_end, end_unix)

            

            #duration=end_unix-start_unix

            start_time = start_unix - self.T0_unix #relative start time
            end_time = end_unix - self.T0_unix

            start_i_tbin=np.argmax(
                    self.time - 0.5 * self.timedel >= start_time) if (
                        0 <= start_time <= self.duration) else 0
            end_i_tbin=np.argmin(
                    self.time + 0.5 * self.timedel <= end_time) if (
                        start_time <= end_time <= self.duration)+1 else len(
                            self.time)

        duration=np.sum(self.timedel[start_i_tbin:end_i_tbin])
            
        
       
        sum_counts = {'top': np.sum(pixel_counts[start_i_tbin:end_i_tbin, :,0:4,:], axis=(0,1,2) ),
                'bottom': np.sum(pixel_counts[start_i_tbin:end_i_tbin, :,4:8,:],axis=(0,1,2) ),
                'small': np.sum(pixel_counts[start_i_tbin:end_i_tbin, :,8:,:],axis=(0,1,2) ),
                'duration':duration,

                'top_err': np.sqrt(np.sum(pixel_counts_err[start_i_tbin:end_i_tbin, :,0:4,:]**2, axis=(0,1,2) )),
                'bottom_err': np.sqrt(np.sum(pixel_counts_err[start_i_tbin:end_i_tbin, :,4:8,:]**2,axis=(0,1,2) )),
                'small_err': np.sqrt(np.sum(pixel_counts_err[start_i_tbin:end_i_tbin, :,8:,:]**2,axis=(0,1,2) ))
                }

        sum_counts['big'] = sum_counts['top']+sum_counts['bottom']
        sum_counts['big_err'] = np.sqrt(sum_counts['top_err']**2 
                + sum_counts['bottom_err']**2 )

        sum_counts['total'] = sum_counts['top']+sum_counts['bottom']+sum_counts['small']
        sum_counts['total_err'] = np.sqrt(sum_counts['top_err']**2 
                + sum_counts['bottom_err']**2 + sum_counts['small_err']**2)

        return sum_counts


    def get_mean_rate(self,start_utc =None, end_utc=None):
        """
        Calculate the mean count rate in different regions of a pixel data file within a specified time range.

        Parameters:
        - start_utc (str or None, optional): The start time in UTC format. If not provided, the beginning of the observation is used.
        - end_utc (str or None, optional): The end time in UTC format. If not provided, the end of the observation is used.

        Returns:
        - dict: A dictionary containing total counts in different regions:
            - 'top': mean count rate in the top row(channels 1-4).
            - 'bottom': mean count rate in the bottom row(channels 5-8).
            - 'small': mean count rate in the small pixels.
            - 'total': mean rate of all pixels 'top' and 'bottom'.
        Note:
        - The function relies on external modules 'sci' and 'st' for pixel data manipulation and time conversions.
        - The time range for counts calculation is determined by start_utc and end_utc. If these are not provided, the entire observation duration is considered.
        """ 

        cnts=get_sum_counts(start_utc , end_utc)
        result={}
        for key,val in cnts.items():
            norm = cnts['duration'] if key !='duration' else 1
            result[key]=val/norm
        return result
    


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
                ))  # pixel summed energy spectrum
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
                ql_ebins = [(4, 10), (10, 15), (15, 25), (25, 50), (50, 84)]
                labels = ('4 - 10 keV', '10 - 15 keV', '15 - 25 keV',
                          '25 - 50 keV', '50 - 84 keV')
                ql_sci_ebins = [
                    self.get_energy_range_slicer(s[0], s[1]) for s in ql_ebins
                ]
                for ebin_slicer, label in zip(ql_sci_ebins, labels):
                    ax1.plot(self.time,
                             np.sum(self.count_rate_spectrogram[:,
                                                                ebin_slicer],
                                    axis=1),
                             label=label)
                    ax1.set_title(
                        f'Detector summed count rates (L1 request #{self.request_id})'
                    )
            else:
                ax1.plot(
                    self.time,
                    self.count_rate_spectrogram[:,
                                                self.min_ebin:self.max_ebin])
            # correct
            ax1.set_ylabel('counts / sec')
            # plt.legend(self.energy_bin_names, ncol=4)
            ax1.set_yscale('log')
            ax1.set_xlabel(f"seconds since {self.T0_utc} ")
            plt.legend()
        if 'spec' in plots:
            if not ax2:
                _, ax2 = plt.subplots()
            ax2.plot(self.ebins_low, self.spectrum, drawstyle='steps-post')
            # ax.set_xticks(self.data[3].data['channel'])
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

        # plt.tight_layout()
        return ax0, ax1, ax2, ax3


class BackgroundSubtraction(object):

    def __init__(self, l1sig: PixelData, l1bkg: PixelData):
        """
                   do background subtraction
                Arguments
                l1sig: a L1product instance containing the signal
                l1bkg: a L1Product instance containing the background

                """
        self.l1sig = l1sig
        self.l1bkg = l1bkg
        #print(self.l1sig.energy_bin_mask)

        dmask = self.l1bkg.energy_bin_mask - self.l1sig.energy_bin_mask
        if np.any(dmask < 0):
            ValueError('Inconsistent energy bins')
            return

        # mean_pixel_rate_clip = self.l1bkg.mean_pixel_rate_spectra * self.l1sig.inversed_energy_bin_mask

        self.pixel_bkg_counts = np.array([
            int_time * self.l1bkg.mean_pixel_rate_spectra
            for int_time in self.l1sig.timedel
        ])
        # set counts beyond the signal energy range to 0
        self.subtracted_counts = (self.l1sig.counts - self.pixel_bkg_counts)
        #print(self.l1sig.inversed_energy_bin_mask)
        self.subtracted_counts *= self.l1sig.energy_bin_mask

        # Dead time correction needs to be included in the future
        self.subtracted_counts_err = np.sqrt(
            self.l1sig.counts + np.array([int_time * self.l1bkg.mean_pixel_rate_spectra_err ** 2 for int_time in self.l1sig.timedel])) * \
            self.l1sig.inversed_energy_bin_mask
        self.bkg_subtracted_spectrogram = np.sum(self.subtracted_counts,
                                                 axis=(1, 2))

    def peek(self):
        fig, axs = plt.subplots(2, 2)
        self.l1sig.peek(ax0=axs[0, 0])
        self.l1bkg.peek(ax0=axs[0, 1])
        X, Y = np.meshgrid(self.l1sig.time,
                           np.arange(self.l1sig.min_ebin, self.l1sig.max_ebin))
        im = axs[1, 0].pcolormesh(
            X, Y,
            np.transpose(
                self.bkg_subtracted_spectrogram[:, self.l1sig.min_ebin:self.
                                                l1sig.max_ebin]))
        axs[1, 0].set_yticks(self.l1sig.energies['channel']
                             [self.l1sig.min_ebin:self.l1sig.max_ebin:2])
        axs[1, 0].set_yticklabels(
            self.l1sig.energy_bin_names[self.l1sig.min_ebin:self.l1sig.
                                        max_ebin:2])
        fig = plt.gcf()
        cbar = fig.colorbar(im, ax=axs[1, 0])
        cbar.set_label('Counts')
        axs[1, 0].set_title('Bkg sub. counts')
        axs[1, 0].set_ylabel('Energy range(keV')
        axs[1, 0].set_xlabel(f"Seconds since {self.l1sig.T0}s ")
        axs[1, 1].plot(np.sum(self.l1sig.spectrogram, axis=0),
                       drawstyle='steps-mid',
                       label='Before subtraction')
        axs[1, 1].plot(np.sum(self.bkg_subtracted_spectrogram, axis=0),
                       drawstyle="steps-mid",
                       label='After subtraction')
        axs[1, 1].plot(np.sum(self.pixel_bkg_counts, axis=(0, 1, 2)),
                       drawstyle="steps-mid",
                       label='background')
        axs[1, 1].legend()

    def get_background_subtracted_spectrum(self, start_utc=None, end_utc=None,
                                           detector_slice = slice(
                                               None, None),
                                           pixel_slice =slice(None, None)):
        """
        Get signal background subtracted spectrum
        Arguments:
        start_utc:  str, datetime, astropy.time.Time or pandas.Timestamp
             Start time of the signal data to be selected, all counts will be selected if not specified
        end_utc:  str, datetime, astropy.time.Time or pandas.Timestamp
             end time of the signal data to be selected, all counts will be selected if not specified
        detector_slice: slice
           slicing detectors for integrating counts. Counts of all detectors are selected by default
        pixel_slice: slice
           slicing pixel for integrating counts. All pixels are selected by default
         Returns:
            bkg_sub_spectra: a numpy array, background-subtracted spectra for the given time range.
            bkg_sub_spectra_err: a numpy array, the errors in the background-subtracted spectra.
        """
        if start_utc is None and end_utc is None:

            start_i_tbin, end_i_tbin=0, self.l1sig.pixel_counts.shape[0]-1

        else:

            start_unix=sdt.utc2unix(
                start_utc) if start_utc else self.l1sig.T0_unix
            end_unix=sdt.utc2unix(
                end_utc) if end_utc else self.l1sig.T0_unix+self.l1sig.duration

            start_time=start_unix - self.l1sig.T0_unix
            end_time=end_unix - self.l1sig.T0_unix

            start_i_tbin=np.argmax(
                self.l1sig.time - 0.5 * self.l1sig.timedel >= start_time) if (
                    0 <= start_time <= self.l1sig.duration) else 0

            end_i_tbin=np.argmin(
                self.l1sig.time + 0.5 * self.l1sig.timedel <= end_time) if (
                    start_time <= end_time <= self.l1sig.duration) else len(
                        self.l1sig.time)-1

        time_span=self.l1sig.time[end_i_tbin] - self.l1sig.time[
                start_i_tbin] + 0.5 * self.l1sig.timedel[
                    start_i_tbin] + 0.5 * self.l1sig.timedel[end_i_tbin]
        bkg_sub_spectra = np.sum(self.subtracted_counts[start_i_tbin: end_i_tbin,
                                                        detector_slice, pixel_slice, : ],
            axis=(0, 1, 2)) / time_span
        
        bkg_sub_spectra_err = np.sqrt(np.sum(self.subtracted_counts_err[start_i_tbin:end_i_tbin, detector_slice, pixel_slice, :]
                   ** 2, axis=(0, 1, 2))) / time_span
        
        return bkg_sub_spectra, bkg_sub_spectra_err                


class Spectrogram(ScienceData):

    def __init__(self, fname, request_id, ltc=False):
        super().__init__(fname, request_id)
        self.data_type = 'Spectrogram'
        self.read_fits(light_time_correction=ltc)
        self.spectrum = np.sum(self.counts, axis=0)

    @property
    def counts_error(self):
        return error_computation(self.hdul['data'].data['counts_comp_err'],
                                 self.counts)

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

        # ((ax0, ax1), (ax2, ax3))=axs
        if not any([ax0, ax1, ax2, ax3]):
            _, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2, figsize=(8, 6))

        if ax0:
            X, Y = np.meshgrid(self.time,
                               self.hdul['ENERGIES'].data['channel'])
            im = ax0.pcolormesh(X, Y, np.transpose(
                self.counts))  # pixel summed energy spectrum
            ax0.set_yticks(self.hdul['ENERGIES'].data['channel'][::2])
            ax0.set_yticklabels(self.energy_bin_names[::2])
            fig = plt.gcf()
            cbar = fig.colorbar(im, ax=ax0)
            cbar.set_label('Counts')
            ax0.set_title('Spectrogram')
            ax0.set_ylabel('Energy range(keV')
            ax0.set_xlabel(f"Seconds since {self.T0}s ")
        if ax1:
            # convert to 2d
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

    def correct_dead_time(self) -> dict:
        """ dead time correction
            returns dict, where
                count_rate --> counts / timedel
                corrected_rate --> count_rate / live_time_ratios
                photons_in --> estimate of photons incident on detector, calculated from triggers
                live_ratio --> livetime at each time bin
                live_error --> estimate of error on live_ratio
        """

        def correct(triggers, counts_arr, time_bins, num_detectors):
            ''' correct dead time using triggers '''
            tau_conv_const = 1e-6

            photons_in = triggers / (time_bins * num_detectors -
                                     TRIG_TAU * triggers)
            # photon rate approximated using triggers

            count_rate = counts_arr / time_bins[:, None]
            nin = photons_in

            live_ratio = np.exp(-BETA * nin * ASIC_TAU * tau_conv_const)
            live_ratio /= (1 + nin * TRIG_TAU)
            corrected_rate = count_rate / live_ratio[:, None]
            return {
                'corrected_rate': corrected_rate,
                'count_rate': count_rate,
                'photons_in': photons_in,
                'live_ratio': live_ratio
            }

        try:
            num_detectors = self.hdul[1].data['detector_masks'].sum()
        except KeyError:
            num_detectors = self.hdul[1].data['detector_mask'].sum()

        self.corrected = correct(self.triggers, self.counts,  self.timedel,
                                 num_detectors)

        # approximate the live ratio error like Ewan does
        above = correct(self.triggers + self.trigger_error, self.counts,
                        self.timedel, num_detectors)
        below = correct(self.triggers - self.trigger_error, self.counts,
                        self.timedel, num_detectors)
        self.corrected['live_error'] = np.abs(above['live_ratio'] -
                                              below['live_ratio']) / 2

        return self.corrected


def error_computation(given_error: np.ndarray,
                      quantity: np.ndarray) -> np.ndarray:
    ''' combine the error from the FITS and Poisson as in IDL '''
    # try/except handles time bin shift
    try:
        return np.sqrt(given_error**2 + quantity)
    except ValueError:
        return np.sqrt(given_error[1:]**2 + quantity)


def fits_time_corrections(primary_header, tstart, tend):
    """Calculates the correct values for the FITS header keywords that deal with times

    Inputs:
    primary_header : astropy.io.fits.primary_HDU.header
        The header to be modified

    tstart : format recognizable by astropy.time.Time (for example, a string)
        Start time of new FITS file
    tend : format recognizable by astropy.time.Time (for example, a string)
        End time of new FITS file

    Returns:
    primary_header : astropy.io.fits.primary_HDU.header
            The modified header
    """
    creation_date = Time(dt.now()).isot
    date_obs = Time(tstart).isot
    date_beg = date_obs
    date_end = Time(tend).isot
    date_avg = Time(Time(tstart).mjd +
                    (Time(tend).mjd - Time(tstart).mjd) / 2.,
                    format='mjd').isot  # average the date
    dateref = date_obs

    date_ear = Time(
        Time(tstart).datetime + td(seconds=primary_header['EAR_TDEL'])).isot
    date_sun = Time(
        Time(tstart).datetime - td(seconds=primary_header['SUN_TIME'])).isot

    # OBT_BEG =
    # OBT_END = #what are these?

    # OBT_BEG = '0703714990:39319'
    # OBT_END = '0703736898:43389'
    primary_header.set('DATE', creation_date)
    primary_header.set('DATE_OBS', date_obs)
    primary_header.set('DATE_BEG', date_beg)
    primary_header.set('DATE_END', date_end)
    primary_header.set('DATE_AVG', date_avg)
    primary_header.set('DATEREF', dateref)
    primary_header.set('DATE_EAR', date_ear)
    primary_header.set('DATE_SUN', date_sun)
    primary_header.set('MJDREF', Time(tstart).mjd)
    # Note that MJDREF in these files is NOT 1979-01-01 but rather the observation start time! Affects time calculation later, but further processing of the file corrects this

    return primary_header


def open_spec_fits(filename):
    """Open a L1, L1A, or L4 FITS file and return the HDUs"""
    with fits.open(filename) as hdul:
        primary_header = hdul[0].header.copy()
        control = hdul[1].copy()
        data = hdul[2].copy()
        energy = hdul[3].copy(
        ) if hdul[3].name == 'ENERGIES' else hdul[4].copy()
    return primary_header, control, data, energy


def fits_time_to_datetime(*args, factor=1):
    """Convert times as stored in FITS files into datetimes
    Inputs (either the filename or the header and data table are accepted):

    fitsfilename : str
        The FITS file whose times to convert

    primary_header : astropy.io.fits.primary_HDU.header
        The header to be modified

    data_table : astropy.table.Table
        Data table containing time information

    factor : int, default = 1
        factor by which to convert data to seconds. In some cases might need to use factor = 100 to account for units of cs being used in place of s

    Returns:
        spectime: astropy.time.Time
    """
    if isinstance(args[0], str):
        primary_header, _, data, _ = open_spec_fits(args[0])
        data_table = data.data
    else:
        primary_header, data_table = args
    time_bin_center = data_table['time']
    duration = data_table['timedel']
    try:
        start_time = dt.strptime(primary_header['DATE_BEG'],
                             "%Y-%m-%dT%H:%M:%S.%f")
    except KeyError:
        start_time = dt.strptime(primary_header['DATE-BEG'],
                             "%Y-%m-%dT%H:%M:%S.%f")

    spectime = Time([
        start_time + td(seconds=bc / factor - d / (2. * factor))
        for bc, d in zip(time_bin_center, duration)
    ])
    return spectime


def time_select_indices(tstart, tend, primary_header, data_table, factor=1.):
    """Find the indices to use in order to select data between a certain start and end time

    Inputs:
    tstart : format recognizable by astropy.time.Time (for example, a string)
        Start time of new FITS file

    tend : format recognizable by astropy.time.Time (for example, a string)
        End time of new FITS file

    primary_header : astropy.io.fits.primary_HDU.header
        The header to be modified

    data_table : astropy.table.Table
        Data table containing time information

    factor : int, default = 1
        factor by which to convert data to seconds. In some cases might need to use factor = 100 to account for units of cs being used in place of s

    Returns:
    idx0 : int
        Start index of time interval
    idx1 : int
        End index of time interval
    """

    spectime = fits_time_to_datetime(primary_header, data_table,
                                     factor=factor).mjd

    if tstart:
        tstart_mjd = Time(tstart).mjd
    else:
        tstart_mjd = spectime[0]
    if tend:
        tend_mjd = Time(tend).mjd
    else:
        tend_mjd = spectime[-1]

    # get indices for tstart and tend
    tselect = np.where(
        np.logical_and(spectime > tstart_mjd, spectime <= tend_mjd))[0]
    idx0, idx1 = tselect[0], tselect[-1]  # first and last indices
    return idx0, idx1


def spec_fits_crop(fitsfile, tstart, tend, outfilename=None):
    """ Crop a STIX science data product (L1A, L1, or L4) to contain only the data within a given time interval. Create a new FITS file containing this data. The new file will be of the same processing level as the input file.

    Inputs:
    fitsfile : str
        Name of input FITS file

    tstart : format recognizable by astropy.time.Time (for example, a string)
        Start time of new FITS file

    tend : format recognizable by astropy.time.Time (for example, a string)
        End time of new FITS file

    outfilename : str, default = None
        Name of output FITS file

    Returns:
        outfilename : str
        Name of output FITS file"""

    primary_header, control, data, energy = open_spec_fits(fitsfile)

    # get indices for tstart and tend
    idx0, idx1 = time_select_indices(tstart, tend, primary_header,
                                     data.data)  # first and last indices

    # crop data table
    count_names = data.data.names
    table_data = []
    for n in count_names:
        if data.data[n].ndim > 1:
            new_data = data.data[n][idx0:idx1, :]
        else:
            if n == 'time':  # this has to be done differently since it is relative to timezero
                timevec = fits_time_to_datetime(
                    primary_header,
                    data.data).mjd  # - Time(primary_header['DATE_BEG']).mjd
                timevec -= timevec[idx0]  # relative to new start time
                new_data = timevec[idx0:idx1] * 86400
            else:
                new_data = data.data[n][idx0:idx1]
        table_data.append(new_data)
    # count_table = Table([data.data[n][idx0:idx1,:] if data.data[n].ndim >1 else data.data[n][idx0:idx1] for n in count_names], names = count_names)
    count_HDU = fits.BinTableHDU(data=Table(table_data, names=count_names))

    # insert other keywords into counts header (do datasum and checksum later)
    count_HDU.header.set('EXTNAME', 'DATA', 'extension name')

    # correct keywords in primary header
    primary_header = fits_time_corrections(primary_header, tstart, tend)
    if not outfilename:
        outfilename = f"{fitsfile[:-5]}_{Time(tstart).datetime:%H%M%S}_{Time(tend).datetime:%H%M%S}.fits"
    primary_header.set('FILENAME', outfilename[outfilename.rfind('/') + 1:])
    primary_HDU = fits.PrimaryHDU(header=primary_header)

    hdul = fits.HDUList([primary_HDU, control, count_HDU, energy])
    hdul.writeto(outfilename, overwrite=True)

    return outfilename


def spec_fits_concatenate(fitsfile1,
                          fitsfile2,
                          tstart=None,
                          tend=None,
                          outfilename=None):
    """ Concatenate two STIX science data product (L1A, L1, or L4) files. Option to select only the 
        data within a given time interval. Create a new FITS file containing this data. The new file will be of the same processing level as the input file. 
        In case of overlapping time ranges, keep the data from the first file within this range (in an ideal case the data will anyway be identical)

    Inputs:
    fitsfile1 : str
        Name of first input FITS file

    fitsfile2 : str
        Name of second input FITS file

    tstart : optional, default = None
        Start time of new FITS file

    tend : optional, default = None
        End time of new FITS file

    outfilename : str, default = None
        Name of output FITS file

    Returns:
        outfilename : str
        Name of output FITS file"""

    primary_header1, control1, data1, energy1 = open_spec_fits(fitsfile1)
    primary_header2, control2, data2, energy2 = open_spec_fits(fitsfile2)

    # check that energy tables are the same. If not, there is an error
    for n in energy1.data.names:
        if not np.allclose(energy1.data[n], energy2.data[n]):
            raise ValueError(
                f"Values for {n} in energy table are different in {fitsfile1} and {fitsfile2}!"
            )

    # check that detector, pixel, and energy masks masks are the same
    for n in [
            'pixel_masks', 'detector_masks', 'pixel_mask', 'detector_mask',
            'energy_bin_mask'
    ]:
        if n in control1.data.names:
            if not np.allclose(control1.data[n], control2.data[n]):
                raise ValueError(
                    f"Values for {n} in control table are different in {fitsfile1} and {fitsfile2}!"
                )

    # get indices for tstart and tend - assuming tstart is in first file and tend in second.
    # test what happens if they are not..
    idx0, idx2 = 0, None  # index of start time in file 1, end time in file 2
    if tstart:
        idx0, _ = time_select_indices(tstart, tend, primary_header1,
                                      data1.data)  # first index
    else:
        tstart = primary_header1['DATE_BEG']

    tend1 = primary_header1[
        'DATE_END']  # end time of first file in case there is ovelap
    if not tend:
        tend = primary_header2['DATE_END']
    idx1, idx2 = time_select_indices(
        tend1, tend, primary_header2,
        data2.data)  # start time in file 2, end time in file 2

    # check that spectrograms are consecutive in time, ie that time1[-1] + timedel1[-1] == time2[0] within some tolerance
    # no longer accurate if using 2 indices for second data table?
    spec_time_gap = fits_time_to_datetime(
        primary_header2, data2.data).datetime[0] - fits_time_to_datetime(
            primary_header1, data1.data).datetime[-1]
    if spec_time_gap.total_seconds() > data1.data['timedel'][-1]:
        warnings.warn(
            f"Gap of {spec_time_gap.total_seconds() - data1.data['timedel'][-1]:.3f}s between spectrogram files {fitsfile1} and {fitsfile2}"
        )

    # concatenate data tables
    count_names = data1.data.names
    table_data = []
    for n in count_names:
        if data1.data[n].ndim > 1:
            new_data = np.concatenate(
                [data1.data[n][idx0:, :], data2.data[n][idx1:idx2, :]])
        else:
            if n == 'time':  # this has to be done differently since it is relative to timezero
                timevec1 = fits_time_to_datetime(primary_header1,
                                                 data1.data).mjd
                new_start_time = timevec1[idx0]
                timevec1 -= new_start_time  # relative to new start time
                timevec2 = fits_time_to_datetime(
                    primary_header2, data2.data).mjd - new_start_time
                new_data = np.concatenate(
                    [timevec1[idx0:] * 86400, timevec2[idx1:idx2] * 86400])
            else:
                new_data = np.concatenate(
                    [data1.data[n][idx0:], data2.data[n][idx1:idx2]])
        table_data.append(new_data)

    count_HDU = fits.BinTableHDU(data=Table(table_data, names=count_names))

    # insert other keywords into counts header (do datasum and checksum later)
    count_HDU.header.set('EXTNAME', 'DATA', 'extension name')

    # correct keywords in primary header
    primary_header1 = fits_time_corrections(primary_header1, tstart, tend)
    if not outfilename:
        outfilename = f"{fitsfile1[:-5]}_{Time(tstart).datetime:%H%M%S}_{Time(tend).datetime:%H%M%S}.fits"
    primary_header1.set('FILENAME', outfilename[outfilename.rfind('/') + 1:])
    primary_HDU = fits.PrimaryHDU(header=primary_header1)

    hdul = fits.HDUList([primary_HDU, control1, count_HDU, energy1])
    hdul.writeto(outfilename, overwrite=True)

    return outfilename



    
