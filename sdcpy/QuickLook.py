#!/usr/bin/python
'''
    This script provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
from matplotlib import pyplot as plt
import datetime
from sdcpy import net

class QuickLook(object):
    def __init__(self):
        pass
class LightCurves(QuickLook):
    def __init__(self, begin_utc, end_utc, ltc=False):
        self.data=net.fetch_light_curves(begin_utc, end_utc,ltc)
    def peek(self, ax=None, legend_loc='upper right'):
        if not ax:
            _, ax=plt.subplots()
        dt=[datetime.datetime.utcfromtimestamp(t) for t in self.data['unix_time']]
        for i in range(5):
            plt.plot(dt, self.data['light_curves'][str(i)], label=self.data['energy_bins']['names'][i])
        dlt=self.data['light_time_diff']
        light_time_corrected=self.data['light_time_corrected']
        
        xlabel=f'UTC + {dlt:.2f} (4 sec time bins)' if light_time_corrected else 'UTC (4 sec time bins)'
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Counts')
        ax.legend(loc=legend_loc)
        ax.set_yscale('log')
        return ax
