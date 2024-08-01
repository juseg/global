#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception world map."""

import argparse
import xarray as xr
import matplotlib.pyplot as plt
from glopdd_threshold import cmaps

def open_git(source='cw5e5', precip='cp', ddf=3):
    """Open glacial inception threshold."""
    if source == 'cdiff':
        return open_git('cera5', precip, ddf) - open_git('cw5e5', precip, ddf)
    if precip == 'dp':
        return open_git(source, 'pp', ddf) - open_git(source, 'cp', ddf)
    if ddf == 'd':
        return open_git(source, precip, 5) - open_git(source, precip, 2)
    da = xr.open_dataarray(
        f'../data/processed/glopdd.git.{source}.{precip}.ddf{ddf}.nc',
        chunks={})
    da = da.sortby(da.lat, ascending=True)
    return da


def main():
    """Main program called during execution."""

    # parse command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-d', '--ddf', default=3, type=int)
    parser.add_argument(
        '-p', '--precip', choices=['cp', 'dp', 'pp'], default='cp')
    parser.add_argument(
        '-s', '--source', choices=['cera5', 'cw5e5'], default='cw5e5')
    args = parser.parse_args()

    # plot and save figure
    plot(**vars(args))


def plot(source='cw5e5', precip='cp', ddf=3):
    """Make plot and save figure for given arguments."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax0 = fig.add_axes([0, 0, 1, 1])
    insets = [fig.add_axes(rect) for rect in (
        [1/36, 2/18, 8/36, 8/18],
        [23/36, 2/18, 8/36, 8/18])]
    cax = fig.add_axes([14/36, 3.5/18, 6/36, .5/18])

    # prepare plot properties
    if source == 'cdiff':
        label = 'inception threshold bias (K)'
        props = {'cmap': cmaps('Oranges_r', 'Blues'), 'vmin': -10, 'vmax': 10}
    elif precip == 'dp':
        label = 'inception threshold difference (K)'
        props = {'cmap': cmaps('Oranges_r', 'Blues'), 'vmin': -10, 'vmax': 10}
    else:
        label = 'glacial inception threshold (K)'
        props = {'cmap': cmaps('Oranges', 'Blues'), 'vmin': -20, 'vmax': 0}

    # open global inception threshold
    with open_git(source=source, precip=precip, ddf=ddf) as diff:

        # plot global map
        diff.isel(lat=slice(0, -1, 10), lon=slice(0, -1, 10)).plot.imshow(
            ax=ax0, add_labels=False, cbar_ax=cax, cbar_kwargs={
                'label': label, 'orientation': 'horizontal'}, **props)

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
                ax=ax, add_colorbar=False, add_labels=False, **props)

            # mark inset
            ax0.indicate_inset(
                [west, south, east-west, north-south], inset_ax=ax)

            # set axes properties
            ax.set_aspect('equal')
            ax.set_title(region)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)

    # save figure
    fig.savefig(f'{__file__[:-3]}_{source}_{precip}_ddf{ddf}', dpi=254)


if __name__ == '__main__':
    main()
