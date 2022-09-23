#!/usr/bin/python
"""
    This module provides APIs to retrieve Housekeeping data from STIX data center  ,and some tools to display the data

"""
import pandas as pd
from astropy.io import fits
from matplotlib import pyplot as plt

from stixdcpy import io as sio
from stixdcpy import time as sdt
from stixdcpy.net import JSONRequest as jreq


class Housekeeping(sio.IO):
    def __init__(self, data):
        data['datetime'] = [sdt.utc2datetime(x) for x in data['time']]
        self.data = data
        self.param_names = self.data['names']

    @classmethod
    def from_sdc(cls, start_utc: str, end_utc: str):
        """
            Fetch housekeeping data from server
            Parameters
            start_utc: str
                data start time 
            end_utc: str
                data end time 
            Returns:
            housekeeping data object

        """
        data = jreq.fetch_housekeeping(start_utc, end_utc)
        return cls(data)

    def plot(self, parameters, which='eng', ax=None):
        """
        Plot a housekeeping parameter
        Parameters
        param: str
          parameter name
        which: str
          what parameter to plot. It can be 'raw' or 'eng'
        ax: matplotlib axes, optional
          a plot will be created if it is not specified
        Returns:
        ax:  matplotlib axes
        """
        params = parameters.split(',')
        if not ax:
            _, ax = plt.subplots()
        key = 'raw_values' if which == 'raw' else 'eng_values'
        for param in params:
            if param not in self.data[key]:
                raise KeyError('Invalid housekeeping parameter name')
            ax.plot(self.data['datetime'],
                    self.data[key][param],
                    label=self.data['names'].get(param, ''))
        ax.set_xlabel('UTC')
        ax.set_ylabel('Value')
        return ax

    def __getattr__(self, name):
        if name == 'data':
            return self.data

    def get_data(self):
        return self.data

    def peek(self, ax=None, legend_loc='upper right'):
        if not ax:
            _, ax = plt.subplots()
        ax.plot(self.data['datetime'], self.data['eng_values']['NIX00081'])
        ax.set_title(self.data['names']['NIX00081'])
        return ax
