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


FPGA_TAU = 10.1e-6
ASIC_TAU = 2.63e-6
DETECTOR_GROUPS = [[1, 2], [6, 7], [5, 11], [12, 13], [14, 15], [10, 16],
                   [8, 9], [3, 4], [31, 32], [26, 27], [22, 28], [20, 21],
                   [18, 19], [17, 23], [24, 25], [29, 30]]
DET_SIBLINGS = {
    0: 1,
    1: 0,
    5: 6,
    6: 5,
    4: 10,
    10: 4,
    11: 12,
    12: 11,
    13: 14,
    14: 13,
    9: 15,
    15: 9,
    7: 8,
    8: 7,
    2: 3,
    3: 2,
    30: 31,
    31: 30,
    25: 26,
    26: 25,
    21: 27,
    27: 21,
    19: 20,
    20: 19,
    17: 18,
    18: 17,
    16: 22,
    22: 16,
    23: 24,
    24: 23,
    28: 29,
    29: 28
}

# detector sibling index



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
        #self.read_data()
    @property
    def url(self):
        req_id = self.request_id if not isinstance(
            self.request_id, list) else self.request_id[0]
        link = f'{net.HOST}/view/list/bsd/uid/{req_id}'
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
        self.counts = self.data['counts']

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
            if self.data_type == 'ScienceL1':
                self.counts = self.counts[1:, :, :, :]
                self.triggers = self.triggers[1:, :]
                self.rcr = self.rcr[1:]
            elif self.data_type == 'Spectrogram':
                self.counts = self.counts[1:, :]
                self.triggers = self.triggers[1:]
                #self.rcr = self.rcr[1:]

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
        self.energy_bin_mask = self.hdul["CONTROL"].data["energy_bin_mask"]

        ebin_nz_idx = self.energy_bin_mask.nonzero()
        self.max_ebin = np.max(ebin_nz_idx)  #indices of the non-zero elements
        self.min_ebin = np.min(ebin_nz_idx)

        self.ebins_mid = [
            (a + b) / 2.
            for a, b in zip(self.energies['e_low'], self.energies['e_high'])
        ]
        self.ebins_low, self.ebins_high = self.energies[
            'e_low'], self.energies['e_high']

        if self.data_type == 'ScienceL1':
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
        return cls(fname, request_id)

    @classmethod
    def from_fits(cls, filename):
        """
        factory class
        Arguments
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
    def __init__(self, fname, request_id):
        super().__init__(fname, request_id)
        self.data_type = 'ScienceL1'
        self.pixel_count_rates = None
        self.correct_pixel_count_rates = None
        self.read_fits()
        self.make_spectra()

    def make_spectra(self, pixel_counts=None):
        if pixel_counts is None:
            pixel_counts = self.pixel_counts
        self.spectrogram = np.sum(pixel_counts, axis=(1, 2))
        self.count_rate_spectrogram = self.spectrogram / self.timedel[:, np.
                                                                      newaxis]
        self.spectrum = np.sum(pixel_counts, axis=(0, 1, 2))

        self.mean_pixel_rate_spectra = np.sum(self.pixel_counts,
                                              axis=0) / self.duration
        self.mean_pixel_rate_spectra_err = np.sqrt(
            self.mean_pixel_rate_spectra) / np.sqrt(self.duration)
        #sum over all time bins and then divide them by the duration, counts per second

        self.pixel_total_counts = np.sum(self.pixel_counts, axis=(0, 3))


    def correct_dead_time(self ):
        """ dead time correction
        Returns:
          corrected_counts: tuple
          the tuple has four elements:
              corrected_rate: np.array
              count_rates:  np.array
              photon_in: np.array
              live_ratio: np.array
        """
        self.corrected=LiveTimeCorrection.correct(self.triggers, self.pixel_counts, self.timedel)
        return self.corrected

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
    def __init__(self, fname, request_id):
        super().__init__(fname,request_id)
        self.data_type = 'Spectrogram'

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



class BackgroundSubtraction(object):
    def __init__(self, l1sig: ScienceL1, l1bkg: ScienceL1):
        """
                   do background subtraction
                Arguments
                l1sig: a L1product instance containing the signal
                l1bkg: a L1Product instance containing the background

                """
        self.l1sig = l1sig
        self.l1bkg = l1bkg

        dmask = self.l1bkg.energy_bin_mask - self.l1sig.energy_bin_mask
        if np.any(dmask < 0):
            logger.error(
                'Background subtraction failed due to the background energy range does not cover the signal energy range  '
            )
            return

        #mean_pixel_rate_clip = self.l1bkg.mean_pixel_rate_spectra * self.l1sig.inverse_energy_bin_mask

        self.pixel_bkg_counts = np.array([
            int_time * self.l1bkg.mean_pixel_rate_spectra
            for int_time in self.l1sig.timedel
        ])
        # set counts beyond the signal energy range to 0
        self.subtracted_counts = (self.l1sig.counts - self.pixel_bkg_counts
                                  ) * self.l1sig.inverse_energy_bin_mask

        # Dead time correction needs to be included in the future
        self.subtracted_counts_err = np.sqrt(
            self.l1sig.counts + np.array([int_time * self.l1bkg.mean_pixel_rate_spectra_err ** 2 for int_time in self.l1sig.timedel])) * \
            self.l1sig.inverse_energy_bin_mask
        self.bkg_subtracted_spectrogram = np.sum(self.subtracted_counts,
                                                 axis=(1, 2))

    def peek(self):
        fig, axs = plt.subplots(2, 2)
        self.l1sig.peek(axs[0, 0])
        self.l1bkg.peek(axs[0, 1])
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

    def get_background_subtracted_spectrum(self, start_utc=None, end_utc=None):
        """
        Get signal background subtracted spectrum

        """
        start_unix = sdt.utc2unix(start_utc)
        end_unix = sdt.utc2unix(end_utc)
        start_time = start_unix - self.l1sig.T0_unix
        end_time = end_unix - self.l1sig.T0_unix
        start_i_tbin = np.argmax(
            self.l1sig.time - 0.5 * self.l1sig.timedel >= start_time) if (
                0 <= start_time <= self.l1sig.duration) else 0

        end_i_tbin = np.argmin(
            self.l1sig.time + 0.5 * self.l1sig.timedel <= end_time) if (
                start_time <= end_time <= self.l1sig.duration) else len(
                    self.l1sig.time)
        time_span = self.l1sig.time[end_i_tbin] - self.l1sig.time[
            start_i_tbin] + 0.5 * self.l1sig.timedel[
                start_i_tbin] + 0.5 * self.l1sig.timedel[end_i_tbin]

        bkg_sub_spectra = np.sum(
            self.subtracted_counts[start_i_tbin:end_i_tbin, :, :, :],
            axis=(0, 1, 2)) / time_span,
        bkg_sub_spectra_err = np.sqrt(
            np.sum(self.subtracted_counts_err[start_i_tbin:end_i_tbin, :, :, :]
                   **2,
                   axis=(0, 1, 2))) / time_span
        return bkg_sub_spectra, bkg_sub_spectra_err


class LiveTimeCorrection(object):
    """
    #counts is np.array   time_bins, detector, pixel, energy bins
    trigger_rates=l1data['triggers'][1:,:]/l1data['timedel'][:-1,None]
    # delta time is off by 1 time bin due a bug in the
    out=np.copy(trigger_rates)
    tau=11e-6
    live_time=1 - tau*trig
    photo_in=trig/(live_time)
	"""
    @staticmethod
    def correct(triggers, counts_arr, time_bins):
        """ Live time correction
        Args
            triggers: ndarray
                triggers in the spectrogram
            counts_arr:ndarray
                counts in the spectrogram
            time_bins: ndarray
                time_bins in the spectrogram
        Returns
        live_time_ratio: ndarray
            live time ratio of detectors
        count_rate:
            corrected count rate
        photons_in:
            rate of photons illuminating the detector group

        """

        fpga_tau = 10.1e-6
        asic_tau = 2.63e-6
        beta= 0.94
        trig_tau = fpga_tau + asic_tau

        time_bins = time_bins[:, None]
        photons_in = triggers / (time_bins - trig_tau * triggers)
        #photon rate calculated using triggers

        live_ratio= np.zeros((time_bins.size, 32))
        time_bins = time_bins[:, :, None, None]

        count_rate = counts_arr / time_bins
        # print(counts_arr.shape)
        for det in range(32):
            trig_idx = inst.detector_id_to_trigger_index(det)
            nin = photons_in[:, trig_idx]
            live_ratio[:, det] = np.exp(
                -beta* nin * asic_tau * 1e-6) / (1 + nin * trig_tau)
        corrected_rate=count_rate/live_ratio[:, :, None, None]
        return  {'corrected_rates': corrected_rate, 'count_rate': count_rate, 'photons_in': photons_in, 'live_ratio':live_ratio}


class TransmissionCorrection(object):
    pass
