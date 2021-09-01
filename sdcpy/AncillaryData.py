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

class Ephemeris(object):
    def __init__(self, utc=None):
        self.data=None
        if utc:
            self.fetch(utc)
    def fetch(self, utc):
        self.data=net.fetch_empheris(utc)
    def peek(self, ax=None):
        if not self.data:
            print(f'Data not loaded. ')
            return None
        data=self.data
        if not ax:
            _, ax=plt.subplots()
        if not data or 'error' in data:
            print(f'Data not available. ')
            return None
        sun= patches.Circle((0.0, 0.0), 0.25, alpha=0.8, fc='yellow')
        plt.text(0,0,'Sun')
        ax.add_patch(sun)
        earth= patches.Circle((-1,0), 0.12, alpha=0.8, fc='green')
        ax.add_patch(earth)
        ax.text(-1,0,'Earth')
        ax.plot(data['x'], data['y'], 'x') 
        ax.text(data['x'][-1],data['y'][-1],'SOLO')
        ax.set_xlabel('X (au)')
        ax.set_ylabel('Y (au)')
        ax.set_xlim(-2,2)
        ax.set_ylim(-2,2)
        ax.set_aspect('equal')
        ax.grid()
        plt.title(f'SOLO Location at {utc}')
        return ax
