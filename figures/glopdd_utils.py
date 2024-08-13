#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Global PDD plotting utils."""

import argparse
import itertools
import multiprocessing
import os.path
import sys
import time

import matplotlib.pyplot as plt
import xarray as xr


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
        plt.close(fig)


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
