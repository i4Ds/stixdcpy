#!/usr/bin/python
'''
    This module provides APIs to retrieve Quick-look data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
from matplotlib import pyplot as plt
from matplotlib import patches
import datetime
from stixdcpy import net
from stixdcpy import io as sio
from stixdcpy.net import JSONRequest as jreq

class Ephemeris(sio.IO):
    def __init__(self):
        self.data= None
    @classmethod
    def request(cls, start_utc:str, end_utc=None, steps=1):
        ob = cls.__new__(cls)
        if end_utc is None:
            end_utc=start_utc
        ob.start_utc, ob.end_utc=start_utc, end_utc
        ob.data=jreq.fetch_empheris(start_utc, end_utc, steps)
        return ob

    @classmethod
    def from_file(cls, filename):
        ob = cls.__new__(cls)
        print('Not implemented yet')
        data=None
        ob.data=data
        return ob

    def __getattr__(self, name):
        if name == 'data':
            return self.data
    def get_data(self):
        return self.data

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
        ax.plot(data['x'], data['y']) 
        ax.plot(data['x'][-1], data['y'][-1], 'x') 
        ax.text(data['x'][-1],data['y'][-1],'SOLO')
        ax.set_xlabel('X (au)')
        ax.set_ylabel('Y (au)')
        ax.set_xlim(-2,2)
        ax.set_ylim(-2,2)
        ax.set_aspect('equal')
        ax.grid()
        plt.title(f'SOLO Location at {self.start_utc}')
        return ax
