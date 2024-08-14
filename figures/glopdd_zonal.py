#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception altitude."""

import xarray as xr
import matplotlib.pyplot as plt

import glopdd_utils


def plot(source='cw5e5'):
    """Make plot and save figure for given source."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax = fig.add_axes([0.1, 0.15, 0.85, 0.75])

    # open inception threshold and elevation model
    with (
            glopdd_utils.open_inception_threshold(source=source) as git,
            xr.open_dataset('~/.cache/hyoga/chelsa/dem_latlong.nc') as dem):
        dem = dem.dem_latlong

        # select partial data for testing
        # west, south, east, north = -90, -60, -60, -30
        # git = git.sel(lat=slice(south, north), lon=slice(west, east))
        # dem = dem.sel(lat=slice(south, north), lon=slice(west, east))

        # align coordinates
        dem = dem.reindex_like(git, method='nearest', tolerance=1e-5)

        # for selected temperature change
        for change, color in zip(
                [0, -5, -10], ['tab:blue', 'tab:orange', 'tab:gray']):

            # compute zonal altitude statistics
            ela = dem.where((change-1 < git) & (git < change+1)).chunk(lon=-1)
            low, med, top = ela.quantile([1/4, 2/4, 3/4], dim='lon')

            # plot interquartile range and median
            ax.fill_between(med.lat, low, top, color=color, alpha=0.25)
            ax.plot(med.lat, med, color=color, label=fr'${change}\pm 1\,$K')

        # set axes properties
        ax.legend()
        ax.set_title('zonal median glacial inception altitude')
        ax.set_ylabel('altitude (m)')
        ax.set_xlabel('latitude (°)')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
