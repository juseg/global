#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception on PMIP4 ensemble mean."""

import os.path
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import glopdd_utils
import hyoga


class ExternalDownloader(hyoga.open.downloader.Downloader):
    """A downloader that stores files in local external data directory.

    Call parameters
    ---------------
    url : str
        The url of the file to download
    path : str
        The path of the downloaded file relative to the external directory.
    """
    def path(self, *args):
        path = super().path(*args)
        return os.path.join('..', 'external', path)


def open_pmip_anomaly():
    """Open PMIP temperature change from PI to LGM."""
    basename = 'PMIP4-ens-means.nc4'
    filepath = ExternalDownloader()(
        'https://data.ipsl.fr/data4papers/kageyama-2021/PMIP4_LGM_paper/'
        'Figures1_6_8_Temperature_Precipitation_Evaporation/' + basename,
        os.path.join('..', 'external', basename))
    with xr.open_dataset(filepath) as pmip:
        da = pmip.lgm_tas - pmip.pi_tas
        da = da.assign_coords(lon=pmip.lon % 360 - 180)
        return da


def plot(source='cw5e5'):
    """Make plot and save figure for given source."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    inset = fig.add_axes([16/36, 3.5/18, 18/36, 6/18])
    ax.add_patch(
        plt.Rectangle((-50, -80), 220, 100, alpha=0.75, ec=str(2/3), fc='w'))

    # open global inception threshold and PMIP4 LGM temperature change
    with (
            glopdd_utils.open_inception_threshold(source=source) as git,
            open_pmip_anomaly() as lgm):

        # interpolate PMIP LGM anomaly to CHELSA grid
        lgm = lgm.interp_like(git)

        # plot global inception areas
        gia = git > lgm
        gia.isel(lat=slice(0, -1, 10), lon=slice(0, -1, 10)).plot.imshow(
                ax=ax, add_labels=False, add_colorbar=False,
                cmap='Blues', vmax=1.5)
                # levels=[0.5], colors=['tab:blues'])

        # set axes properties
        ax.set_aspect('equal')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_xticks(range(-180, 180, 30))
        ax.set_yticks(range(-90, 90, 30))

        # select american cordilleras
        west, south, east, north = -135, -60, -60, 45
        git = git.sel(lat=slice(south, north), lon=slice(west, east))

        # mark inset
        ax.indicate_inset(
            [west, south, east-west, north-south])

        # open digital elevation model
        with xr.open_dataset('~/.cache/hyoga/chelsa/dem_latlong.nc') as dem:
            dem = dem.dem_latlong / 1e3

            # align coordinates
            dem = dem.sel(lat=slice(south, north), lon=slice(west, east))
            dem = dem.reindex_like(git, method='nearest', tolerance=1e-5)

            # for selected temperature change
            for change, color, label in (
                    (0, 'tab:gray', '0'), (lgm, 'tab:blue', 'PMIP4 LGM')):

                # compute zonal altitude statistics
                ela = dem.where((change-1 < git) & (git < change+1))
                low, med, top = ela.quantile([0, 2/4, 1], dim='lon')

                # plot interquartile range and median
                inset.fill_between(med.lat, low, top, color=color, alpha=0.25)
                inset.plot(
                    med.lat, med, color=color, label=label+r'$\pm 1\,$K')

        # set axes properties
        inset.legend()
        inset.set_title('zonal median glacial inception altitude')
        inset.set_ylabel('altitude (km)')
        inset.set_xlabel('latitude (°)')

    # plot paleoglacier equilibrium line altitudes
    ela = pd.read_csv('../data/native/ela_legrain_etal_2023.csv')
    ax.plot(ela.Longitude, ela.Latitude, color='tab:red', ls='', marker='+')
    inset.errorbar(
        ela.Latitude, ela['LGM ELA (m)']/1e3, yerr=ela['σ(m)']/1e3,
        color='tab:red', ls='', marker='_', label='Paleo-glacier ELA')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
