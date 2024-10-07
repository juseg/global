#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception areas."""

import matplotlib.pyplot as plt
import glopdd_utils


def plot(source='cw5e5'):
    """Make plot and save figure for given source."""

    # initialize figure
    fig, axes = plt.subplots(
        figsize=(160/25.4, 80/25.4), ncols=2, gridspec_kw={
            'left': 0.1, 'bottom': 0.15, 'right': 0.95, 'top': 0.9})

    # define glacier regions
    regions = {
        'Antarctica': [-180, -90, 180, -60],
        'Greenland': [-75, 60, -15, 90],
        'World': [-180, -90, 180, 90]}

    # open inception threshold and elevation model
    with glopdd_utils.open_inception_threshold(source=source) as git:

        # select partial data for testing
        label = 'Greenland'
        west, south, east, north = regions[label]
        git = git.sel(lat=slice(south, north), lon=slice(west, east))

        # plot cumulative area
        ax = axes[0]
        cells = git.groupby(git).count()
        cells = cells.reindex(git=cells.git[::-1])
        cells = cells.cumsum(dim='git')
        cells.plot(ax=ax, label=label)

        # set axes properties
        ax.legend()
        ax.set_xlabel('temperature change (K)')
        ax.set_ylabel('glacial inception grid cells')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
