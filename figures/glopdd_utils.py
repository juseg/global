#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Global PDD plotting utils."""

import argparse
import contextlib
import itertools
import multiprocessing
import os.path
import sys
import time

import matplotlib as mpl
import numpy as np
import xarray as xr


# Parallel MultiPlotter class
# ---------------------------

class MultiPlotter():
    """Plot multiple figures in parallel."""

    def __init__(self, plotter, **options):
        """Initialize with a plot method and options dictionary."""
        self.plotter = plotter
        self.options = options

    def __call__(self):
        """Plot and save figures in parallel."""
        options = vars(self.parse())
        iterargs = itertools.product(*options.values())
        with multiprocessing.Pool() as pool:
            pool.starmap(self.savefig, iterargs)
        # unfortunately starmap can't take iterable keyword-arguments
        # iterkwargs = [dict(zip(options, combi)) for combi in iterargs]

    def parse(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description=__doc__)
        for name, choices in self.options.items():
            parser.add_argument(
                f'-{name}[0]', f'--{name}', choices=choices, default=choices,
                nargs='+')
        return parser.parse_args()

    def savefig(self, *args):
        """Plot and save one figure."""
        filename = '_'.join([sys.argv[0][:-3]] + list(args))
        basename = os.path.basename(filename)
        print(time.strftime(f'[%H:%M:%S] plotting {basename} ...'))
        fig = self.plotter(*args)
        fig.savefig(filename, dpi='figure')
        mpl.pyplot.close(fig)


# Plot helpers
# ------------

def combine_colormaps(*args, n=256):
    """Combine any number of colormaps in a single one."""
    name = ''.join(arg[:2] for arg in args)
    values = np.linspace(0, 1, int(n/len(args)))
    colors = np.vstack([mpl.colormaps[name](values) for name in args])
    return mpl.colors.LinearSegmentedColormap.from_list(name, colors)


def get_plot_labels(source='sdiff'):
    """Get titles for three-panel diff plots."""
    ref, sub, suffix = {
        'fdiff': ('2', '5', r'$\,kg\,m^{-2}\,K^{-1}\,day^{-1}$'),
        'pdiff': ('constant', 'reduced', ' precip'),
        'sdiff': ('CHELSA-W5E5', 'CHELSA-2.1', ''),
        }[source]
    return f'{ref}{suffix}', f'{sub}{suffix}', fr'{sub} - {ref}{suffix}'


def get_plot_title(source='cw5e5'):
    if source in ('cera5', 'cw5e5'):
        prefix = 'glacial'
    else:
        prefix = get_plot_labels(source=source)[2]
    return prefix + '\ninception threshold (K)'


def get_plot_kwargs(source='cw5e5'):
    combine = combine_colormaps
    return {
        'cera5': {'cmap': combine('Oranges', 'Blues'), 'vmin': -20, 'vmax': 0},
        'cw5e5': {'cmap': combine('Oranges', 'Blues'), 'vmin': -20, 'vmax': 0},
        'fdiff': {'cmap': 'Oranges_r'},
        'pdiff': {'cmap': 'Oranges_r', 'vmax': 0},
        'sdiff': {'cmap': combine('Oranges_r', 'Blues')}}[source]


# Open datasets
# -------------

@contextlib.contextmanager
def open_inception_threshold_duo(source='sdiff'):
    """Open duo of inception threshold maps."""
    kwargs0, kwargs1 = {
        'fdiff': ({'ddf': val} for val in (2, 5)),
        'pdiff': ({'precip': val} for val in ('cp', 'pp')),
        'sdiff': ({'source': val} for val in ('cw5e5', 'cera5'))}[source]
    with (
            open_inception_threshold(**kwargs0) as da0,
            open_inception_threshold(**kwargs1) as da1):
        yield (da0, da1)


def open_inception_threshold(source='cw5e5', precip='cp', ddf=3):
    """Open glacial inception threshold."""
    if source == 'fdiff':
        return (
            open_inception_threshold(source='cw5e5', precip=precip, ddf=5) -
            open_inception_threshold(source='cw5e5', precip=precip, ddf=2))
    if source == 'pdiff':
        return (
            open_inception_threshold(source='cw5e5', precip='pp', ddf=ddf) -
            open_inception_threshold(source='cw5e5', precip='cp', ddf=ddf))
    if source == 'sdiff':
        return (
            open_inception_threshold(source='cera5', precip=precip, ddf=ddf) -
            open_inception_threshold(source='cw5e5', precip=precip, ddf=ddf))
    da = xr.open_dataarray(
        f'../data/processed/glopdd.git.{source}.{precip}.ddf{ddf}.nc',
        chunks={})
    da = da.sortby(da.lat, ascending=True)
    return da
