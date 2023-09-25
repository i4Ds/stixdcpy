#!/usr/bin/python
"""
    This module provides APIs to retrieve STIX preview images from STIX data center,
    and provides tools to display the data.
"""
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.time import Time
from astropy.table import Table
from astropy import units as u
from matplotlib import pyplot as plt
from stixdcpy import time_util as sdt
from stixdcpy.logger import logger
from stixdcpy import io as sio
from stixdcpy import utils
from stixdcpy import net
from stixdcpy import instrument as inst
from pathlib import PurePath
from datetime import datetime as dt
from datetime import timedelta as td
from pprint import pprint
try:
    from IPython.display import Image, display, HTML
except ImportError:
    pass


class ImgSpecArchive(sio.IO):
    """
    A class to interact with the STIX data center, retrieve preview images,
    and provide tools to display the data.

    Attributes:
        response (dict): The response obtained from the STIX data center.
        flare_ephemeris (list): List of flare ephemeris data.

    Methods:
        query(flare_id=None, start_utc=None, end_utc=None): Query preview images
            based on flare_id or time range.
        data(): Returns the data of the imgspec_results.
        display_images(imgspec_results, map_name='CLEAN'): Display preview images and associated information.
        peek(image_type='clean'): Display a peek of the loaded flare image list.
        draw_map(imap, fig=None, panel_grid=111, title='', descr='', draw_image=True,
            contour_levels=[], zoom_ratio=1, cmap='std_gamma_2', color='w', grid_spacing=5*u.deg,
            text_xy=[0.02, 0.95], desc_xy=[0.95, 0.98], vmin=None): Draw a map using sunpy map.
    """

    def __init__(self, response=None):
        """
        Initializes the ImgSpecArchive object.

        Parameters:
            response (dict): The response obtained from the STIX data center.
        """
        self.response = response
        self.flare_ephemeris = []
        try:
            self.imgspec_results = response['data']
            self.flare_ephemeris = [
                x['flare_ephemeris'] for x in self.imgspec_results
                if 'flare_ephemeris' in x
            ]
        except:
            self.imgspec_results = None

    @classmethod
    def query(cls, *args, **kwargs):
        """
        Downloads flare meta data from the STIX data center.

        Parameters:
            flare_id (int): Flare unique id.
            start_utc (str): Start UTC to search for flares.
            end_utc (str): End UTC to search for flares.

        Returns:
            ImgSpecArchive object: The queried image archive.
        """
        flare_id = None
        start_utc = None
        end_utc = None

        if len(args) == 1:
            flare_id = int(args[0])
        elif len(args) == 2:
            start_utc, end_utc = args
        elif 'flare_id' in kwargs:
            flare_id = kwargs['flare_id']

        if 'start_utc' in kwargs:
            start_utc = kwargs['start_utc']
        if 'end_utc' in kwargs:
            end_utc = kwargs['end_utc']

        if flare_id:
            logger.info(f'Querying preview images for flare #{flare_id}')
            res = net.Request.query_imaging_spectroscopy_for_flare(flare_id)
        elif start_utc and end_utc:
            logger.info(f'Querying preview images {start_utc} {end_utc}')
            res = net.Request.query_imaging_spectroscopy_list(
                start_utc, end_utc)
        else:
            raise ValueError('Invalid arguments')

        return cls(res)
    @property
    def data(self):
        """
        Returns the data of the imgspec_results.

        Returns:
            dict: The data of the imgspec_results.
        """
        return self.imgspec_results
    


        # The implementation of this method goes here (omitted for brevity).
    def animate(self, image_type='CLEAN'):
        pass

    def peek(self, image_type='CLEAN'):
        """
        Display a peek of the loaded flare image list.

        Parameters:
            image_type (str): The type of image to display (default='clean').
        """
        if not utils.is_notebook():
            pprint(result)
            return
        ishown = 0
        for data in self.imgspec_results:
            display(HTML(f'<h3>Image ID # {data["_id"]}</h3>'))
            uid = data.get('unique_id', None)
            try:
                peak= data['peak_utc']
                display(
                    HTML(f'<h3>STIX flare observed at {peak} </h3>'))
            except KeyError:
                pass
            try:
                flare_meta = data['flare_ephemeris']
                display(pd.DataFrame(flare_meta, index=[0]).T)
            except KeyError:
                pprint(data)
                pass
            report=data.get('report',None)
            if not isinstance(report,dict):
                return
            for key, val in report.items():
                if image_type not in val['title']:
                    continue
                url = f'{net.HOST}/image-archive/{uid}/{val["filename"]}'
                display(HTML(f'<b>{val.get("title","")}</b>'))
                display(Image(url=url, width=400, height=300))
            ishown += 1
            if ishown >= 10:
                display(
                    HTML(
                        f'<div style="color:red">Only 10 of {len(self.imgspec_results)} flare images are shown!</div >'
                    ))
                break

    @staticmethod
    def draw_map(self,
                 imap,
                 fig=None,
                 panel_grid=111,
                 title='',
                 descr='',
                 draw_image=True,
                 contour_levels=[],
                 zoom_ratio=1,
                 cmap='std_gamma_2',
                 color='w',
                 grid_spacing=5 * u.deg,
                 text_xy=[0.02, 0.95],
                 desc_xy=[0.95, 0.98],
                 vmin=None):
        """
        Draw a map using sunpy map.

        Parameters:
            imap: Sunpy map.
            fig: Figure to plot on (default=None).
            panel_grid: Subplot (default=111).
            title: Title for the plot (default='').
            descr: Description for the plot (default='').
            draw_image: Boolean flag to draw the image (default=True).
            contour_levels: Contour levels (default=[]).
            zoom_ratio: Zoom ratio (default=1).
            cmap: Color map for plotting (default='std_gamma_2').
            color: Color for grid and limb (default='w').
            grid_spacing: Grid spacing (default=5*u.deg).
            text_xy: Coordinates for the text (default=[0.02, 0.95]).
            desc_xy: Coordinates for the description (default=[0.95, 0.98]).
            vmin: Minimum value for the plot (default=None).

        Returns:
            Axes: The axes for the plot.
        """
        if not fig:
            fig = plt.figure()
        ax = fig.add_subplot(panel_grid, projection=imap)
        if draw_image:
            if vmin is None:
                imap.plot(cmap=cmap, axes=ax, title="")
            else:
                imap.plot(cmap=cmap, axes=ax, title="", vmin=vmin * imap.max())
        imap.draw_grid(color=color, ls='--', grid_spacing=grid_spacing)
        imap.draw_limb(axes=ax, color=color, alpha=0.5)
        if title:
            ax.text(text_xy[0],
                    text_xy[1],
                    title,
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    color=color)
        if descr:
            ax.text(desc_xy[0],
                    desc_xy[1],
                    descr,
                    horizontalalignment='right',
                    verticalalignment='top',
                    transform=ax.transAxes,
                    color=color)
        if contour_levels:
            clevels = contour_levels * u.percent
            cs = imap.draw_contours(clevels)
            h, _ = cs.legend_elements()
            labels = [f'{x}%' for x in contour_levels]
            ax.legend(h, labels, framealpha=0)
        ax.set_aspect('equal')
        return ax
