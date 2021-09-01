#!/usr/bin/python
'''
    This script provides APIs to retrieve energy  calibration data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''

import datetime
import requests
from pprint import pprint
from matplotlib import pyplot as plt

from sdcpy import net

class Calibration(object):
    def __init__(self):
        pass
class EnergyLUT(Calibration):
    def __init__(self, utc):
        self.data=net.fetch_onboard_and_true_eluts(utc)
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
    def info(self):
        try:
            pprint(self.data['info'])
            pprint('Pixel 0 true energy bin  edges: ')
            pprint(self.get_pixel_true_ebins(0))
            pprint('...')

        except Exception as e:
            print(e)


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
    def get_true_ebin_edges(self):
        try:
            return self.data['data']['onboard']
        except Exception as e:
            print(e)
            return None

    def get_pixel_true_ebins(self, pixel):
        try:
            ebins=self.data['true_energy_bin_edges'][:,pixel] #retrieve the column  
            return np.array([ (ebins[i], ebins[i+1]) for i in range(32)])
        except Exception as e:
            print(e)
            return None



