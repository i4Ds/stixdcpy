#!/usr/bin/python3
"""
 Python script to plot and animate STIX preview images
 Author: Hualin Xiao (hualin.xiao@fhnw.ch)
 History: v1.0 -- Aug 22, 2022

"""
import wget
import sunpy
import sunpy.map
import numpy as np
from astropy import units as u
from matplotlib import pyplot as plt
from astropy.coordinates import SkyCoord
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

CMAP='std_gamma_2' #color map
def plot(stix_map, fig=None, ax=None, grid=111, title='', descr='', 
                     draw_image=True, contour_levels=[], 
        cmap=CMAP, color='w',   grid_spacing=10*u.deg, 
        text_xy=(0.02,0.95), desc_xy=(0.95, 0.98),
                     vmin=None):
    """
    plot a stix flare image on an matplotlib axes

    Parameters
    -----------------------------
        stix_map:  sunpy.map or image filename
            stix image loaded into sunpy.map or image filename
        fig: matplot figure, optional
            figure to plot the image on, if none creates a new figure
        ax:  (matplotlib.axes.Axes)
            axes to plot the image on, if none uses current axes
        title: str, optional
            title of the plot
        descr: str, optional
            description of the map
        draw_image: bool, default to True
            whether draw image
        contour_levels: list, optional
            draw contours if the list is not empty
        cmap: str
            color map used to plot the image
        grid_spacing: Astropy.Quantity, optional
            grid spacing. default to 10*u.deg
        text_xy: tuple
            position of the title to be placed
        desc_xy: tuple
            position of the description to be placed
            
    Returns:
    -----------------------------
        ax: matplotlib axe

    """
    if isinstance(stix_map, str):
        stix_map=sunpy.map.Map(stix_map)
    elif not isinstance(stix_map, sunpy.map.mapbase.GenericMap):
        raise TypeError('Invalid image type')
    if not fig:
        fig=plt.figure()
    if not ax:
        ax = fig.add_subplot(grid, projection=stix_map)
    if draw_image:
        if vmin is None:
            stix_map.plot(cmap=cmap, axes=ax, title="")
        else:
            stix_map.plot(cmap=cmap, axes=ax, title="", vmin=vmin*stix_map.max())
            
    stix_map.draw_grid(color=color, ls='--', grid_spacing=10*u.deg)
    stix_map.draw_limb(axes=ax, color=color,alpha=0.5)
    if title:
        ax.text(text_xy[0], text_xy[1],title,
             horizontalalignment='left',   verticalalignment='center',   
                transform = ax.transAxes, color=color)
    if descr:
        ax.text(desc_xy[0], desc_xy[1],descr, 
                horizontalalignment='right', verticalalignment='top',  
                transform = ax.transAxes, color=color)
        
    if contour_levels:
        clevels = np.array(contour_levels)*stix_map.max()
        cs=stix_map.draw_contours(clevels)
        proxy = [plt.Rectangle((1, 1), 2, 1, fc=pc.get_edgecolor()[0]) for pc in
        cs.collections]
        legends=[ f'{contour_levels[i]*100:.0f} %'  for i, x in enumerate(clevels) ]
        plt.legend(proxy, legends)
    ax.set_aspect('equal')
    return  ax

def get_range(m):
    w,h=m.data.shape
    c=m.pixel_to_world(0*u.pix, 0*u.pix) 
    c2=m.pixel_to_world(w*u.pix, h*u.pix) 
    return {'min':(c.Tx.value, c.Ty.value), 'max':(c2.Tx.value, c2.Ty.value)}
def union_lim(ranges):
    res={'min':[-np.inf, -np.inf], 'max':[np.inf,np.inf]}
    for lim in ranges:
        res['min'][0] =max(lim['min'][0], res['min'][0])
        res['min'][1] =max(lim['min'][1], res['min'][1])
        res['max'][0] =min(lim['max'][0], res['max'][0])
        res['max'][1] =min(lim['max'][1], res['max'][1])
    return res
def set_range(ax, m, boundbox):
    c1,c2=boundbox['min'], boundbox['max']    
       
    xlims_world = [c1[0], c2[0]]*u.arcsec
    ylims_world = [c1[1], c2[1]]*u.arcsec
    world_coords = SkyCoord(Tx=xlims_world, Ty=ylims_world, frame=m.coordinate_frame)
    pixel_coords = m.world_to_pixel(world_coords)
    xlims_pixel = pixel_coords.x.value
    ylims_pixel = pixel_coords.y.value
    ax.set_xlim(xlims_pixel)
    ax.set_ylim(ylims_pixel)
    ax.set_aspect('equal')

def animate(filenames, fig=None, interval=500):
    seq = sunpy.map.Map(filenames, sequence=True, sortby='date')
    ims=[]
    fig=plt.figure() if fig is None else fig
    ax = fig.add_subplot(111, projection=seq[0])
    plot(seq[0], fig, ax, title=seq[0].meta['date-obs'])
    fc=ax.get_facecolor()


    xylims=[get_range(s)  for s in seq]
    xylim=union_lim(xylims)
    #fig, ax = plt.subplots()
    def update(i):
        global ax
        global fc
        m=seq[i]
        ax.remove()
        ax = fig.add_subplot(111, projection=m)
        ax.set_facecolor(fc)
        title=f"Start: {m.meta['date-obs']}\nExposure time: {m.meta['exptime']} sec"
        ax=plot(m, fig, ax, title=title)
        set_range(ax, m, xylim)
        return m
      
    ani = FuncAnimation(fig, update, frames=len(seq), interval=interval)
    return ani
        
