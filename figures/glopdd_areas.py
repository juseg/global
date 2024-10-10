#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception areas."""

import time
import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt
import glopdd_utils


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


def regions_like(other):
    """Build a regions object with the same shape as given other."""

    # region definitions (Greenland overlaps Europe and N.Am.)
    bounds = {
        'Asia': (60, 0, 180, 90),
        'North America': (-180, 10, -30, 90),
        'Europe': (-30, 30, 60, 90),
        'South America': (-180, -60, -30, 10),
        'Africa': (-30, -60, 60, 30),
        'Oceania': (60, -60, 180, 0),
        'Antarctica': (-180, -90, 180, -60),
        'Greenland': (-75, 60, -15, 90)}

    # build a region mask object
    regions = xr.zeros_like(other, dtype=str)
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
    fig, axes = plt.subplots(
        figsize=(160/25.4, 80/25.4), ncols=2, gridspec_kw={
            'left': 0.1, 'bottom': 0.15, 'right': 0.95, 'top': 0.9})

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
                ax=axes[0], add_labels=False, add_colorbar=False,
                cmap=color_colormap(color, gamma=1/3))

            # plot cumulative area
            gia = cells.broadcast_like(sel).groupby(sel).sum()
            gia = gia.reindex(git=gia.git[::-1]).cumsum(dim='git') / 1e12
            gia.plot(ax=axes[1], color=color, label=label)

        # set axes properties
        axes[1].legend(ncols=2)
        axes[1].set_xlabel('temperature change (K)')
        axes[1].set_ylabel(r'glacial inception area ($10^6\,km^2$)')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
