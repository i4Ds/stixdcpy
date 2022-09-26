import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.colors as colors
from dateutil import parser as dtparser
from stixdcpy import io as sio
from stixdcpy.net import JSONRequest as jreq
from stixdcpy import instrument as inst
from stixdcpy.logger import logger


class Spectrogram(object):
    """
        Spectrogram object constructed using json data fetched  from STIX data  center
    """

    def __init__(self, start_utc: str, end_utc: str, data: dict):
        self.start_utc = start_utc
        self.end_utc = end_utc
        self.data = data

    def peek(self, plot_type='spec', ax=None):
        """Create quick-look plots for the loaded spectrogram data
        Parameters
        ----------
        ax: plt.axes
            axes to be plotted
        plot_type: str
            plot type, can be 'spec' to plot spectrogram or 'lc' to plot time series
        """
        if ax is None:
            fig, ax = plt.subplots()

        if plot_type == 'spec':
            ax.pcolor(self.data['datetime'],
                      self.data['energy_bin_names'],
                      self.data['spectrogram'],
                      norm=colors.LogNorm())
            ax.set_ylabel('Energy (keV)')
        else:
            for spec, ebin_name in zip(self.data['spectrogram'], self.data['energy_bin_names']):
                ax.plot(self.data['datetime'], spec, label=ebin_name)
            ax.set_ylabel('Count rate (cps)')
            ax.set_yscale('log')
            ax.legend()

        ax.set_xlabel('Time')

    def plot(self, energy_bins=None, min_time_bins=None, ax=None):

        pass

    @classmethod
    def from_sdc(cls, start_utc: str, end_utc: str):
        """
        fetch spectrogram data from stix data center
        Parameters:
        ---------
        start_utc: str
            data start time
        end_utc: str
            data end time
        Returns:
        --------
        spectrogram: Spectrogram
                A class instance of Spectrogram
        """
        json_data = jreq.fetch_spectrogram(start_utc, end_utc)
        if not json_data:
            logger.warning('Failed to download the data from STIX data center')
            return

        spectrograms = []
        begin, end = dtparser.parse(start_utc).timestamp(), dtparser.parse(
            end_utc).timestamp()
        last_unix = 0
        timestamps = []
        time_bins = []
        E1, E2, Eunit, dmask, pmask = [], [], [], [], []
        utcs = []
        rcr = []
        for req in json_data['data']:
            for gr in req['groups']:
                E1.append(gr['E1'])
                E2.append(gr['E2'])
                rcr.append(gr['rcr'])
                Eunit.append(gr['Eunit'])
                dmask.append(gr['detector_mask'])
                pmask.append(gr['pixel_mask'])
                for sb in gr['subgroups']:
                    unix = sb[0]
                    if unix < last_unix or unix < begin or unix > end:
                        continue
                    spectrograms.append(sb[2])
                    utcs.append(datetime.utcfromtimestamp(unix))
                    time_bins.append(sb[3])

        if np.unique(E1).size > 1 or np.unique(E2).size > 1 or np.unique(
                dmask).size > 1 or np.unique(pmask).size > 1:
            raise ValueError(
                'Failed to merge the spectrogram! STIX spectrogram configuration changed in the requested time frame! '
            )
        time_bins = np.array(time_bins)
        spectrograms = np.array(spectrograms).T / time_bins
        ebands = inst.get_spectrogram_energy_bins(E1[0], E2[0], Eunit[0])
        data = {
            'datetime': utcs,
            'time_bin': time_bins,
            'spectrogram': spectrograms,
            'time_bins': time_bins,
            'rcr': np.unique(rcr),
            'elow': np.unique(E1),
            'ehigh': np.unique(E2),
            'dmask': np.unique(dmask),
            'pmask': np.unique(pmask),
            'energy_bins': ebands,
            'energy_bin_names': [f'{a} – {b} keV' for (a, b) in ebands]
        }

        return cls(start_utc, end_utc, data=data)


def test():
    spec = Spectrogram.from_sdc('2022-08-01T00:00:00', '2022-08-01T10:00:00')
    spec.peek()
    plt.show()


if __name__ == '__main__':
    test()
