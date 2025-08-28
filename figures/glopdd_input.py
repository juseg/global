#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD input temperature, precipitation and stdev."""

import sys
import absplots as apl
import glopdd_utils

# FIXME align coordinate names and units within hyoga to avoid that import
# FIXME this fails on relative paths (use ln -s ../data/external external)
sys.path.append('../data/')
import glopdd  # noqa pylint: disable=import-error, wrong-import-order, wrong-import-position


def plot(source='cw5e5'):
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(160, 80), ncols=3, nrows=3, gridspec_kw={
            'left': 2.5, 'right': 2.5, 'bottom': 17.5, 'top': 2.5,
            'wspace': 2.5, 'hspace': 2.5, 'height_ratios': (5, 5, 1)})

    # open climatology
    temp, prec, stdv = glopdd.open_climate_tile('n30e060', source=source)
    temp = temp.sortby(temp.lat, ascending=True)
    prec = prec.sortby(prec.lat, ascending=True)
    stdv = stdv.sortby(stdv.lat, ascending=True)

    # plot climate variables
    for axrow, month in zip(axes, (1, 7)):
        indexers = {'month': month, 'lat': slice(32, 42), 'lon': slice(65, 85)}
        kwargs = {'add_labels': False, 'add_colorbar': False}
        temp_plot = temp.sel(indexers).plot.imshow(
            ax=axrow[0], cmap='RdBu_r', vmin=-30, vmax=30, **kwargs)
        prec_plot = prec.sel(indexers).plot.imshow(
            ax=axrow[1], cmap='Greens', vmin=0, vmax=15, **kwargs)
        stdv_plot = stdv.sel(indexers).plot.imshow(
            ax=axrow[2], cmap='Purples', vmin=0, vmax=5, **kwargs)

    # add colorbars
    fig.colorbar(
        temp_plot, cax=axes[2, 0], label='surface air temperature (°C)',
        extend='both', orientation='horizontal')
    fig.colorbar(
        prec_plot, cax=axes[2, 1], label=r'precipitation ($mm day^{-1}$)',
        extend='max', orientation='horizontal')
    fig.colorbar(
        stdv_plot, cax=axes[2, 2], label='temp standard deviation (K)',
        extend='max', orientation='horizontal')

    # set axes properties
    for ax in axes[:2].flat:
        ax.set_aspect('equal')
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
