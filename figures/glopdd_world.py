#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception world map."""

import argparse
import multiprocessing
import os.path
import time
import xarray as xr
import matplotlib.pyplot as plt
from glopdd_threshold import cmaps


def open_git(source='cw5e5', precip='cp', ddf=3):
    """Open glacial inception threshold."""
    if source == 'fdiff':
        return open_git(source, precip, 5) - open_git(source, precip, 2)
    elif source == 'pdiff':
        return open_git(source, 'pp', ddf) - open_git(source, 'cp', ddf)
    elif source == 'sdiff':
        return open_git('cera5', precip, ddf) - open_git('cw5e5', precip, ddf)
    da = xr.open_dataarray(
        f'../data/processed/glopdd.git.{source}.{precip}.ddf{ddf}.nc',
        chunks={})
    da = da.sortby(da.lat, ascending=True)
    return da


def main():
    """Main program called during execution."""

    # available data sources
    sources = ['cera5', 'cw5e5', 'fdiff', 'pdiff', 'sdiff']

    # parse command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-f', '--factor', choices=[3], default=[3], nargs='+')
    parser.add_argument(
        '-p', '--precip', choices=['cp', 'pp'], default=['cp'], nargs='+')
    parser.add_argument(
        '-s', '--source', choices=sources, default=sources, nargs='+')
    args = parser.parse_args()

    # iterable plot arguments excluding recursive diff
    iterargs = [
        (source, precip, ddf) for source in args.source
        for precip in args.precip for ddf in args.factor]

    # plot all frames in parallel
    with multiprocessing.Pool() as pool:
        pool.starmap(save, iterargs)


def plot(source='cw5e5', precip='cp', ddf=3):
    """Make plot and save figure for given arguments."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax0 = fig.add_axes([0, 0, 1, 1])
    insets = [fig.add_axes(rect) for rect in (
        [1/36, 2/18, 8/36, 8/18],
        [23/36, 2/18, 8/36, 8/18])]
    ax0.add_patch(
        plt.Rectangle((-50, -80), 90, 50, alpha=0.75, ec=str(2/3), fc='w'))
    cax = fig.add_axes([14.5/36, 4.5/18, 6/36, .5/18])

    # prepare plot properties
    if source == 'cdiff':
        label = r'CHELSA-2.1$-$CHELSA-W5E5' + '\ninception threshold (K)'
        props = {'cmap': cmaps('Oranges_r', 'Blues')}
    elif precip == 'dp':
        label = r'scaled$-$constant precip' + '\ninception threshold (K)'
        props = {'cmap': 'Oranges_r', 'vmax': 0}
    else:
        label = 'glacial inception\nthreshold (K)'
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

    # return figure
    return fig


def save(source, precip, ddf):
    """Plot and save figure."""
    filename = f'{__file__[:-3]}_{source}_{precip}_ddf{ddf}'
    print(f"[{time.strftime('%H:%M:%S')}] plotting {os.path.basename(filename)} ...")
    fig = plot(source, precip, ddf)
    fig.savefig(filename, dpi='figure')
    plt.close(fig)


if __name__ == '__main__':
    main()
