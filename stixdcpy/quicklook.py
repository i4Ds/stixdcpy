#!/usr/bin/python
"""
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""
import datetime

from matplotlib import pyplot as plt
from stixdcpy import io as sio
from stixdcpy.net import JSONRequest as jreq


class QuickLook(sio.IO):
    def __init__(self):
        pass

    # def save_fits(self,fname):
    #    self.data.writeto(fname)


class LightCurves(QuickLook):
    def __init__(self, data):
        if 'error' not in data:
            self.data = data
        else:
            self.data = None

    @classmethod
    def from_sdc(cls, start_utc: str, end_utc: str, ltc=False):
        """ fetch light curve data from STIX data center

        Args:
            start_utc: str
                data start UTC
            end_utc: str
                data end UTC
            ltc: bool
                Light time correction flag. Do light time correction if it is True


        Returns:
            lc: python object
                Lightcurve object

        """
        data = jreq.fetch_light_curves(start_utc, end_utc, ltc)
        if 'light_curves' in data:
            # correct key name
            data['counts'] = data['light_curves']
            del data['light_curves']
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
        dt = [
            datetime.datetime.utcfromtimestamp(t)
            for t in self.data['unix_time']
        ]
        for i in range(5):
            ax.plot(dt,
                    self.data['counts'][str(i)],
                    label=self.data['energy_bins']['names'][i])
        dlt = self.data['DELTA_LIGHT_TIME']
        light_time_corrected = self.data['IS_LIGHT_TIME_CORRECTED']

        xlabel = f'UTC + {dlt:.2f} (4 sec time bins)' if light_time_corrected else 'UTC (4 sec time bins)'
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Counts')
        ax.legend(loc=legend_loc)
        ax.set_yscale('log')
        return ax
