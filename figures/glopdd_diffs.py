#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD side-by-side comparisons."""

import matplotlib.pyplot as plt
import glopdd_utils


def plot(source='sdiff'):
    """Make plot and save figure for given source."""

    # initialize figure
    fig, axes = plt.subplots(ncols=3, gridspec_kw={
        'left': .1, 'bottom': .2, 'top': .95})
    cax1 = fig.add_axes([.1, .15, .52, .05])
    cax2 = fig.add_axes([.67, .15, .23, .05])

    # open global inception threshold
    # FIXME allow fdiff, pdiff sources
    with (
            glopdd_utils.open_inception_threshold('cera5') as cera5,
            glopdd_utils.open_inception_threshold('cw5e5') as cw5e5):

        # plot absolute values
        for ax, git in zip(axes, (cera5, cw5e5)):
            git.plot.imshow(
                ax=ax, add_labels=False, vmin=-20, vmax=4,
                cmap='plasma_r', cbar_ax=cax1, cbar_kwargs={
                    'label': 'glacial inception threshold (k)',
                    'orientation': 'horizontal'})

        # plot difference
        diff = cw5e5 - cera5
        diff.plot.imshow(
            ax=axes[2], add_labels=False, center=0,
            cmap='RdBu', cbar_ax=cax2, cbar_kwargs={
                'label': 'glacial inception threshold (k)',
                'orientation': 'horizontal'})

    # set axes properties
    axes[0].set_title('CHELSA-ERA5')
    axes[1].set_title('CHELSA-W5E5')
    axes[2].set_title(r'CHELSA-W5E5 - CHELSA-ERA5')
    for ax in axes:
        ax.set_aspect('equal')
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['fdiff', 'pdiff', 'sdiff']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
