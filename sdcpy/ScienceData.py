#!/usr/bin/python
'''
    This script provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
from matplotlib import pyplot as plt
from matplotlib import patches
import datetime
from sdcpy import net

class ScienceData(object):
    def __init__(self, id=None):
        self.data=None
        if id is not None:
            self.fetch(id)
    def fetch(self, id):
        self._id=id
        self.data=net.fetch_science_data(id)
    def __getattr__(self, name):
        if name == 'data':
            return self.data
    def get_data(self):
        return self.data

    def peek(self, ax=None):
        if not self.data:
            print(f'Data not loaded. ')
            return None
        if not ax:
            _, ax=plt.subplots()
        if not data or 'error' in data:
            print(f'Data not available. ')
            return None
        return ax
