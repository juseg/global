#!/usr/bin/python
# Copyright (c) 2024-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception areas."""

import time
import absplots as apl
import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt
import glopdd_utils
import hyoga


def add_cut_axes_mm(ax, width=30, height=15, pad=2.5):
    """Cut inset axes in top-right corner of main axes."""

    # get main axes position
    pos = ax.get_position(original=True)  # cf mpl api changes 3.0.0
    ax.patch.set_ec('none')

    # compute dims relative to main axes
    fig = ax.figure
    figw, figh = fig.get_size_inches()*25.4

    # cut main axes (using transAxes)
    axw = (width / pos.width + pad) / figw
    axh = (height / pos.height + pad) / figh
    x = [0, 1, 1, 1-axw, 1-axw, 0, 0]
    y = [0, 0, 1-axh, 1-axh, 1, 1, 0]
    kwargs = {'clip_on': False, 'transform': ax.transAxes, 'zorder': 3}
    poly = plt.Polygon(list(zip(x, y)), ec='k', fc='none', **kwargs)
    rect = plt.Rectangle((1-axw, 1-axh), axw, axh, ec='w', fc='w', **kwargs)
    ax.add_patch(rect)
    ax.add_patch(poly)

    # return new cut axes
    return fig.add_axes([
        pos.x1-width/figw, pos.y1-height/figh, width/figw, height/figh])


def cell_areas_ellipsoidal(lat, dlat, dlon=None, a=6378137, b=6356752.314245):
    """Compute elemental surface area on ellipsoidal Earth."""
    dlon = dlon or dlat
    e = (1-(b/a)**2)**0.5
    return (
        a**2 * (1-e**2) * (1-e**2*np.sin(np.pi*lat/180)**2)**-2 *
        np.cos(np.pi*lat/180) * dlat * dlon * (np.pi/180)**2)


def cell_areas_spherical(lat, dlat, dlon=None, radius=6371230):
    """Compute elemental surface area on spherical Earth."""
    dlon = dlon or dlat
    return radius**2 * np.cos(np.pi*lat/180) * dlat * dlon * (np.pi/180)**2


def color_colormap(color, gamma=1):
    """Create a colormap from white to given colour."""
    return mpl.colors.LinearSegmentedColormap.from_list(
        color, [(0, 'w'), (1, color)], gamma=gamma)


def open_regions():
    """Open custom regions geodataframe."""
    countries = hyoga.open.natural_earth(
        'admin_0_countries', category='cultural', scale='50m')
    countries = countries.set_index('NAME')
    countries.loc['Russia', 'CONTINENT'] = 'Asia'
    countries.loc['Greenland', 'CONTINENT'] = 'Greenland'
    regions = countries.dissolve(by='CONTINENT')
    regions = regions.rename(index={
        'North America': 'N. Am.', 'South America': 'S. Am.'})
    regions.loc['Antarctica*'] = regions.loc[[
        'Antarctica', 'Seven seas (open ocean)']].union_all()
    regions = regions.reindex(index=[
        'Asia', 'N. Am.', 'Europe', 'S. Am.', 'Africa', 'Oceania',
        'Antarctica*', 'Greenland'])
    return regions


def regions_like(other):
    """Build a regions object with the same shape as given other."""

    # region definitions (Greenland overlaps Europe and N.Am.)
    bounds = {
        'Asia': (60, 0, 180, 90),
        'N. Am.': (-180, 10, -30, 90),
        'Europe': (-30, 30, 60, 90),
        'S. Am.': (-180, -60, -30, 10),
        'Africa': (-30, -60, 60, 30),
        'Oceania': (60, -60, 180, 0),
        'Antarctica': (-180, -90, 180, -60),
        'Greenland': (-75, 60, -15, 90)}

    # build a region mask object
    regions = xr.zeros_like(other, dtype=np.dtype('U10'))
    for name, (west, south, east, north) in bounds.items():
        lon_mask = (west <= regions.lon) & (regions.lon <= east)
        lat_mask = (south <= regions.lat) & (regions.lat <= north)

        # dask does not support multi-dim vect indexing, so use where
        # regions.loc[{'lat': lat_mask, 'lon': lon_mask}] = name
        regions = regions.where(~(lat_mask & lon_mask), name)

    # assign non-dimensional region name coordinate
    regions = regions.assign_attrs(labels=bounds.keys())

    # return new object
    return regions


def plot(source='cw5e5'):
    """Make plot and save figure for given source."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(85, 60), gridspec_kw={
        'left': 12.5, 'right': 2.5, 'bottom': 10, 'top': 2.5})
    inset = add_cut_axes_mm(ax)

    # open inception threshold and elevation model
    with glopdd_utils.open_inception_threshold(source=source) as git:

        # select partial data for testing
        git = git.isel(lat=slice(0, -1, 10), lon=slice(0, -1, 10))

        # compute cell areas
        cells = cell_areas_ellipsoidal(git.lat, git.lat[1] - git.lat[0])

        # loop on glaciated regions
        regions = regions_like(git)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for color, label in zip(colors, regions.labels):

            # select regional data
            print(time.strftime(f'[%H:%M:%S] - computing areas in {label}...'))
            sel = git.where(regions == label)

            # plot regions map
            sel.plot.imshow(
                ax=inset, add_labels=False, add_colorbar=False,
                cmap=color_colormap(color, gamma=1/3))

            # plot cumulative area
            gia = cells.broadcast_like(sel).groupby(sel).sum()
            gia = gia.reindex(git=gia.git[::-1]).cumsum(dim='git') / 1e12
            gia.plot(ax=ax, color=color, label=label)

            # add region label
            ytext = 3 if label == 'Africa' else -3 if label == 'Oceania' else 0
            ax.annotate(
                label, color=color, fontsize=6, fontweight='bold',
                xy=(gia[-1].git, gia[-1]), xytext=(-6, ytext),
                textcoords='offset points', ha='right', va='center')

        # set axes properties
        ax.set_xlabel('temperature change (K)')
        ax.set_ylabel(r'glacial inception area ($10^6\,km^2$)')
        ax.set_xlim(-26, 6)
        ax.set_ylim(-1, 26)
        inset.set_aspect('equal')
        inset.set_ylim(-90, 90)
        inset.xaxis.set_visible(False)
        inset.yaxis.set_visible(False)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
