#!/usr/bin/python
"""
    This module provides algorithms to correct detector effects
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""
import numpy as np
from matplotlib import pyplot as plt

from stixdcpy import instrument as inst
from stixdcpy import science
from stixdcpy import time as sdt
from stixdcpy.logger import logger

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


class BackgroundSubtraction(object):
    def __init__(self, l1sig: science.ScienceL1, l1bkg: science.ScienceL1):
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

        count_rates = counts_arr / time_bins
        # print(counts_arr.shape)
        for det in range(32):
            trig_idx = inst.detector_id_to_trigger_index[det]
            nin = photons_in[:, trig_idx]
            live_ratio[:, det] = np.exp(
                -beta* nin * asic_tau * 1e-6) / (1 + nin * trig_tau)
        corrected_rates=count_rates/live_ratio[:, :, None, None]
        return  (corrected_rates, count_rates, photons_in, live_ratio)


class TransmissionCorrection(object):
    pass
