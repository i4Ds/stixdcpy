#!/usr/bin/python
import numpy as np
import pandas as pd
from matplotlib import patches
from matplotlib import pyplot as plt

from stixdcpy import io as sio
from stixdcpy.logger import logger
from stixdcpy.net import JSONRequest as jreq


class Ephemeris(sio.IO):
    def __init__(self, start_utc, end_utc, data):
        self.start_utc = start_utc
        self.end_utc = end_utc
        self.data = data

    @classmethod
    def from_sdc(cls, start_utc: str, end_utc=None, steps=1):
        """
        Fetch ephemeris from STIX data center
        Args:
            start_utc: str
            Start UTC
            end_utc: str
            End UTC
            steps:
            Number of data steps
        Returns:
            ephemeris: object

        """
        if end_utc is None:
            end_utc = start_utc
        orbit = jreq.request_ephemeris(start_utc, end_utc, steps)
        att = jreq.request_attitude(start_utc, end_utc, steps)
        data = {'orbit': orbit, 'attitude': att}
        return cls(start_utc, end_utc, data)

    @classmethod
    def from_npy(cls, filename):
        """
        Load ephemeris data from a npz file
        Args:
            filename: str
            npz filename
        """
        with np.load(filename, allow_picke=True) as data:
            item = data.item()
            _data = item['data']
            start, end = item['start'], item['end']
            cls(start, end, _data)

    def save_npy(cls, filename):
        """
        Save ephemeris data as npy format
        Args:
            filename: str
            npy filename
        """
        _data = {
            'data': self.data,
            'start': self.start_utc,
            'end': self.end_utc
        }
        np.save(filename, _data)

    def to_pandas(self):
        """convert ephemeris data to pandas data frame

        Returns:
            df: pandas data frame


        """
        return pd.DataFrame(self.data)

    def __getattr__(self, name):
        if name == 'data':
            return self.data

    def get_data(self):
        return self.data

    def peek(self, ax=None):
        if not self.data:
            logger.error(f'Data not loaded. ')
            return None
        if not ax:
            _, ax = plt.subplots()
        data = self.data['orbit']
        if not data or 'error' in data:
            logger.error(f'Data not available. ')
            return None
        sun = patches.Circle((0.0, 0.0), 0.25, alpha=0.8, fc='yellow')
        plt.text(0, 0, 'Sun')
        ax.add_patch(sun)
        earth = patches.Circle((-1, 0), 0.12, alpha=0.8, fc='green')
        ax.add_patch(earth)
        ax.text(-1, 0, 'Earth')
        ax.plot(data['x'], data['y'])
        ax.plot(data['x'][-1], data['y'][-1], 'x')
        ax.text(data['x'][-1], data['y'][-1], 'SOLO')
        ax.set_xlabel('X (au)')
        ax.set_ylabel('Y (au)')
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        ax.grid()
        plt.title(f'SOLO Location at {self.start_utc}')
        return ax


class Pointing(Ephemeris):
    def __init__(self, utc, data):
        self.utc = utc
        self.data = data

    @classmethod
    def from_sdc(cls, utc):
        """
        Fetch ephemeris from STIX data center
        Args:
            start_utc: str
            Start UTC
            end_utc: str
            End UTC
            steps:
            Number of data steps
        Returns:
            ephemeris: object

        """
        data = jreq.request_pointing(utc)
        return cls(utc, data)

    def peek(self, ax=None):
        if not self.data:
            logger.error(f'Data not loaded. ')
            return None
        if not ax:
            _, ax = plt.subplots()
        data = self.data
        if not data or 'error' in data:
            logger.error(f'Data not available. ')
            return None
        ax.plot(data['fov']['x'],
                data['fov']['y'],
                '--',
                label='STIX FOV',
                color='black')
        ax.plot([data['sun_center'][0]], [data['sun_center'][1]],
                marker='+',
                label='Sun Center')
        ax.plot(data['limb']['x'],
                data['limb']['y'],
                label='Solar limb',
                color='red')
        center = [round(x, 1) for x in data["sun_center"]]
        ax.set_title(f'Solar center: {center}  arcsec \n {data["time"]} UT ')
        nsew_coords = np.array(data['nsew'])
        ax.plot(nsew_coords[0:2:, 0], nsew_coords[0:2, 1])
        ax.plot(nsew_coords[2::, 0], nsew_coords[2:, 1])
        ax.text(nsew_coords[0, 0], nsew_coords[0, 1], 'N')
        ax.text(nsew_coords[2, 0], nsew_coords[2, 1], 'E')
        ax.set_aspect('equal')
        ax.legend(loc='upper right')
        ax.set_xlim(-5400, 5400)
        ax.grid(True)
        ax.set_xlabel('STIX X (arcsec)')
        ax.set_ylabel('STIX Y (arcsec)')
        return ax
