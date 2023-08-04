#!/usr/bin/python
"""
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from stixdcpy import io as sio
from stixdcpy.net import Request as jreq
import matplotlib.dates as mdates
import pandas as pd


class QuickLook(sio.IO):
    def __init__(self):
        pass

    # def save_fits(self,fname):
    #    self.data.writeto(fname)


class LightCurves(QuickLook):
    def __init__(self, data):
        self.data = data
        self.counts = []
        self.time = []
        self.energy_bins = []
        self.dlt = 0
        self.rcr = []
        self.triggers = []
        if data is not None:
            if 'error' not in data and 'counts' in data:
                self.counts = np.array(data['counts'])
                self.time = [datetime.utcfromtimestamp(
                    t + data['start_unix']) for t in data['delta_time']]
                self.triggers = np.array(data['triggers'])
                self.rcr = np.array(data['rcr'])
                self.dlt = data['light_time_diff']
                self.light_time_corrected = data['is_light_time_corrected']
                self.energy_bins = data['energy_bins']

    @classmethod
    def from_sdc(cls, start_utc, end_utc, ltc=False):
        """ fetch light curve data from STIX data center

        Args:
            start_utc: str or datetime
                data start UTC
            end_utc: str or datetime
                data end UTC
            ltc: bool
                Light time correction flag. Do light time correction if it is True


        Returns:
            lc: python object
                Lightcurve object

        """
        data = jreq.fetch_light_curves(start_utc, end_utc, ltc)
        return cls(data)

    def __getattr__(self, name):
        if name == 'data':
            return self.data

    def get_data(self):
        """ get light curve data
        Returns:
            data: dict
                light curve data

        """
        return self.data

    def to_pandas(self):
        stix_df = pd.DataFrame(np.array(self.data["counts"]).T, 
                               index=self.time, 
                               columns=self.data["energy_bins"]["names"])
        return stix_df

    def peek(self, ax=None, legend_loc='upper right'):
        """
        Plot light curves
        Args:
            ltc: light time correction flag. The default value is False. Do light time correction if ltc=True
        Returns
            ax: matplotlib axs

        """
        if not self.data:
            ax.text(0.5, 0.5, 'LC not available!')
            return ax

        if not ax:
            _, ax = plt.subplots()
        for i in range(5):
            ax.plot(self.time,
                    self.counts[i, :],
                    label=self.energy_bins['names'][i])
        xlabel = f'UTC + {self.dlt:.2f} (4 sec time bins)' if self.light_time_corrected else 'UTC (4 sec time bins)'
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Counts')
        ax.legend(loc=legend_loc)
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.set_yscale('log')
        return ax
