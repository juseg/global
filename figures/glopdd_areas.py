#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception areas."""

import xarray as xr
import matplotlib.pyplot as plt
import glopdd_utils


def regions_like(other):
    """Build a regions object with the same shape as given other."""

    # region definitions (Greenland overlaps Europe and N.Am.)
    bounds = {
        'Africa': (-30, -60, 60, 30),
        'Antarctica': (-180, -90, 180, -60),
        'Asia': (60, 0, 180, 90),
        'Europe': (-30, 30, 60, 90),
        'North America': (-180, 10, -30, 90),
        'Oceania': (60, -60, 180, 0),
        'South America': (-180, -60, -30, 10),
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

        # loop on glaciated regions
        ax = axes[0]
        regions = regions_like(git)
        for label in regions.labels:

            # select regional data
            mask = regions == label
            sel = git.where(mask.compute(), drop=True)

            # plot cumulative area
            cells = sel.groupby(sel).count()
            cells = cells.reindex(git=cells.git[::-1])
            cells = cells.cumsum(dim='git')
            cells.plot(ax=axes[0], label=label)

        # set axes properties
        ax.legend()
        ax.set_xlabel('temperature change (K)')
        ax.set_ylabel('glacial inception grid cells')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
