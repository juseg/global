#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Global PDD plotting utils."""

import argparse
import itertools
import multiprocessing
import os.path
import time
import matplotlib.pyplot as plt


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
        filename = '_'.join([__file__[:-3]] + list(args))  # FIXME __file__
        basename = os.path.basename(filename)
        print(time.strftime(f'[%H:%M:%S] plotting {basename} ...'))
        fig = self.plotter(*args)
        fig.savefig(filename, dpi='figure')
        plt.close(fig)

