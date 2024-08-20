#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD input temperature side-by-side comparison."""

import os.path
import xarray as xr
import matplotlib.pyplot as plt


def open_climatology(month=7, source='cw5e5', var='tas'):
    """Open input climatology from hyoga cache directory."""
    prefix = os.path.join('~', '.cache', 'hyoga', source, 'clim', source)
    da = xr.open_mfdataset(
        f'{prefix}.{var}.mon.8110.avg.??0???0.nc',
        chunks={}, decode_coords='all').to_array().squeeze()
    # FIXME align coordinate names and values in hyoga?
    if source == 'cera5':
        da = da.assign_coords(month=range(1, 13)).rename(x='lon', y='lat')
        da['lat'] = da.lat.astype('f4')
        da['lon'] = da.lon.astype('f4')
        da = da.sortby(da.lat, ascending=True)
    if source == 'cw5e5' and var == 'tas':
        da = da - 273.15
    da = da.sel(month=month)
    return da


def plot():
    """Main program called during execution."""

    # initialize figure
    fig, axes = plt.subplots(
        figsize=(160/25.4, 80/25.4), ncols=3, gridspec_kw={
            'left': 0.5/36, 'bottom': 0.5/18, 'right': 35.5/36,
            'top': 16.5/18, 'wspace': 1/11})
    cax1 = fig.add_axes([3/36, 3/18, 6/36, 0.5/18])
    cax2 = fig.add_axes([27/36, 3/18, 6/36, 0.5/18])
    for ax in (axes[0], axes[2]):
        ax.add_patch(plt.Rectangle(
            (0, 0), 1, 3.5/16, alpha=0.75, ec=str(2/3), fc='w',
            transform=ax.transAxes))

    # open july temperature from hyoga cache directory
    with (
            open_climatology(source='cera5') as cera5,
            open_climatology(source='cw5e5') as cw5e5):

        # select region (aspect 16x11 = 8x5.5)
        cera5 = cera5.sel(lat=slice(27, 43), lon=slice(74, 85))
        cw5e5 = cw5e5.sel(lat=slice(27, 43), lon=slice(74, 85))

        # plot absolute values
        for ax, git in zip(axes, (cera5, cw5e5)):
            git.plot.imshow(
                ax=ax, add_labels=False, cmap='Reds', vmin=-10, vmax=30,
                cbar_ax=cax1, cbar_kwargs={
                    'label': '1981 - 2010 July temp (°C)',
                    'orientation': 'horizontal'})

        # plot difference
        diff = cw5e5 - cera5
        diff.plot.imshow(
            ax=axes[2], add_labels=False,
            cmap='RdBu_r', cbar_ax=cax2, cbar_kwargs={
                'label': 'difference (K)',
                'orientation': 'horizontal'})

    # set axes properties
    titles = ('CHELSA-ERA5', 'CHELSA-W5E5', r'CHELSA-W5E5 $-$ CHELSA-ERA5')
    for ax, title in zip(axes, titles):
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    fig = plot()
    fig.savefig(__file__[:-3], dpi='figure')


if __name__ == '__main__':
    main()
