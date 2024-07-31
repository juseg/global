#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception world map."""

import xarray as xr
import matplotlib.pyplot as plt
from glopdd_threshold import cmaps

def open_git(source='cw5e5'):  # prec='cp', pdd=3
    """Open glacial inception threshold."""
    if source == 'cdiff':
        return open_git('cera5') - open_git('cw5e5')
    da = xr.open_dataarray(f'../data/processed/glopdd.git.{source}.nc')
    da = da.sortby(da.lat, ascending=True)
    return da


def main():
    """Main program called during execution."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax0 = fig.add_axes([0, 0, 1, 1])
    insets = [fig.add_axes(rect) for rect in (
        [1/36, 2/18, 8/36, 8/18],
        [23/36, 2/18, 8/36, 8/18])]
    cax = fig.add_axes([14/36, 3.5/18, 6/36, .5/18])
    kwargs = {'cmap': cmaps('Oranges_r', 'Purples'), 'vmin': -10, 'vmax': 10}

    # open global inception threshold
    with open_git('cdiff') as diff:

        # plot global map
        diff.isel(lat=slice(0, -1, 10), lon=slice(0, -1, 10)).plot.imshow(
            ax=ax0, add_labels=False, cbar_ax=cax, cbar_kwargs={
                'label': 'inception threshold bias (K)',
                'orientation': 'horizontal'}, **kwargs)

        # set axes properties
        ax0.set_aspect('equal')
        ax0.set_xlim(-180, 180)
        ax0.set_ylim(-90, 90)
        ax0.set_xticks(range(-180, 180, 30))
        ax0.set_yticks(range(-90, 90, 30))
        cax.grid(False)

        # for each region
        for ax, (region, bounds) in zip(insets, {
                'Patagonia': [-80, -60, -60, -40],
                'Kunlun': [70, 25, 90, 45]}.items()):
            west, south, east, north = bounds

            # plot regional map
            diff.sel(
                    lat=slice(south, north), lon=slice(west, east)).plot.imshow(
                ax=ax, add_colorbar=False, add_labels=False, **kwargs)

            # mark inset
            ax0.indicate_inset(
                [west, south, east-west, north-south], inset_ax=ax)

            # set axes properties
            ax.set_aspect('equal')
            ax.set_title(region)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)

    # save figure
    fig.savefig(__file__[:-3], dpi=254)


if __name__ == '__main__':
    main()
