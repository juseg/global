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

        # for selected temperature change
        for delta, color in zip(
                [0, -5, -10], ['tab:blue', 'tab:orange', 'tab:gray']):

            # compute zonal altitude statistics
            ela = dem.where(git == delta)
            min, med, max = ela.quantile([1/4, 2/4, 3/4], dim='lon')

            # plot interquartile range and median
            ax.fill_between(med.lat, min, max, color=color, alpha=0.25)
            ax.plot(med.lat, med, color=color, label=fr'{delta}$\,$K')

        # set axes properties
        ax.legend()
        ax.set_title('glacial inception altitude')
        ax.set_ylabel('altitude (m)')
        ax.set_xlabel('latitude')

    # save figure
    fig.savefig(__file__[:-3], dpi=254)


if __name__ == '__main__':
    main()
