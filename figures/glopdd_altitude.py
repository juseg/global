#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception altitude."""

import xarray as xr
import matplotlib.pyplot as plt


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = plt.subplots(figsize=(160/25.4, 80/25.4))

    # open inception threshold and elevation model
    with (
            xr.open_dataarray('../data/processed/glopdd.git.cw5e5.nc') as git,
            xr.open_dataset('~/.cache/hyoga/chelsa/dem_latlong.nc') as dem):
        dem = dem.dem_latlong

        # select partial data for testing
        west, south, east, north = 0, 30, 30, 60
        west, south, east, north = -90, -60, -60, -30
        git = git.sel(lat=slice(south, north), lon=slice(west, east))
        dem = dem.sel(lat=slice(south, north), lon=slice(west, east))

        # asser coords are similar
        xr.testing.assert_allclose(git.lon, dem.lon)
        xr.testing.assert_allclose(git.lat, dem.lat)

        # option 1: convert dem coords to f4
        dem['lat'] = dem.lat.astype('f4')
        dem['lon'] = dem.lon.astype('f4')

        # option 2: align coordinates
        dem = dem.reindex_like(git, method='nearest', tolerance=1e-5)

        # assert coords are equal
        xr.testing.assert_equal(git.lon, dem.lon)
        xr.testing.assert_equal(git.lat, dem.lat)

        # compute zonal altitude statistics
        ela = dem.where(git == 0).quantile([0, 0.25, 0.5, 0.75, 1], dim='lon')

        # plot interquantile ranges and median
        color = 'tab:blue'
        ax.fill_between(
            ela.lat, *ela.sel(quantile=[0, 1]), alpha=0.2, color=color)
        ax.fill_between(
            ela.lat, *ela.sel(quantile=[0.25, 0.75]), alpha=0.325, color=color)
        ax.plot(ela.lat, ela.sel(quantile=0.5), color=color)

        # set axes properties
        ax.set_title('glacial inception altitude')
        ax.set_ylabel('altitude (m)')
        ax.set_xlabel('latitude')

    # save figure
    fig.savefig(__file__[:-3], dpi=254)


if __name__ == '__main__':
    main()
