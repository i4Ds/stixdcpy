#!/usr/bin/python
'''
    This module provides APIs to retrieve data from STIX data center 
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
from stixdcpy import science
import numpy as np
DETECTOR_GROUPS = [
	[1, 2],
	[6, 7],
	[5, 11],
	[12, 13],
	[14, 15],
	[10, 16],
	[8, 9],
	[3, 4],
	[31, 32],
	[26, 27],
	[22, 28],
	[20, 21],
	[18, 19],
	[17, 23],
	[24, 25],
	[29, 30]
]
DET_SIBLINGS={0: 1, 1: 0, 5: 6, 6: 5, 4: 10, 10: 4, 11: 12, 12: 11, 13: 14, 14: 13, 9: 15, 15: 9, 7: 8, 8: 7, 2: 3, 3: 2, 30: 31, 31: 30, 25: 26, 26: 25, 21: 27, 27: 21, 19: 20, 20: 19, 17: 18, 18: 17, 16: 22, 22: 16, 23: 24, 24: 23, 28: 29, 29: 28}
#detector sibling index 

def fill_count_with_background(sig:science.L1, bkg:science.L1):
    #sig  and bkg are science.L1 instance



def live_time_correction(l1data):
    #counts is np.array   time_bins, detector, pixel, energy bins
    trigger_rates=l1data['triggers'][1:,:]/l1data['timedel'][:-1,None]
    # delta time is off by 1 time bin due a bug in the
    out=np.copy(counts)
    tau=11e-6
    live_time=1 - tau*trig
    photo_in=trig/(live_time)

    
