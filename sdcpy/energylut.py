#!/usr/bin/python
'''
    This script provides APIs to retrieve energy  calibration data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''

import datetime
from pprint import pprint
from matplotlib import pyplot as plt
import numpy as np

from sdcpy import net
from sdcpy import io as sio
from sdcpy.net import JSONRequest as jreq

class EnergyLUT(sio.IO):
    def __init__(self):
        self.data=None
    @classmethod
    def request(cls,utc):
        ob = cls.__new__(cls)
        ob.data=jreq.fetch_onboard_and_true_eluts(utc)
        '''
        data structure
        {'data':{
                    'onboard':self.onboard_elut, 
                    'calibration':self.calibration_run_elut,
                    'true_energy_bin_edges':self.true_energy_bin_edges,
                    'energy_bin_edges':NOMINAL_EBIN_EDGES,
                },
                'info': self.info(),
                }
                '''
        return ob
    @classmethod
    def from_file(cls, filename):
        ob = cls.__new__(cls)
        print('Not implemented yet')
        data=None
        ob.data=data
        return ob


    def info(self):
        try:
            pprint(self.data['info'])
            #pprint('Pixel 0 true energy bin  edges: ')
            #pprint(self.get_pixel_true_ebins(0))
            #pprint('...')

        except Exception as e:
            print(e)

    def __getattr__(self, name):
        if name == 'data':
            return self.data['data']
    def get_data(self):
        return self.data['data']

    def get_calibration_data(self):
        try:
            return self.data['data']['calibration']
        except Exception as e:
            print(e)
            return None

    def get_onboard_elut(self):
        try:
            return self.data['data']['onboard']
        except Exception as e:
            print(e)
    def get_true_energy_bin_edges(self):
        try:
            return np.array(self.data['data']['true_energy_bin_edges'])
        except Exception as e:
            print(e)
            return None

    def get_pixel_true_ebins(self, pixel):
        try:

            true_ebins=np.array(self.data['data']['true_energy_bin_edges'])
            pixel_ebins=true_ebins[:,pixel] #retrieve the column  
            return np.array([[pixel_ebins[i], pixel_ebins[i+1]] for i in range(32)])
        except Exception as e:
            print(e)
            return None



