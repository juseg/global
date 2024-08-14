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
    with glopdd_utils.open_inception_threshold_duo(source) as (da0, da1):

        # select region
        da0 = da0.sel(lat=slice(-55, -45), lon=slice(-75, -70))
        da1 = da1.sel(lat=slice(-55, -45), lon=slice(-75, -70))

        # plot absolute values
        cmap = glopdd_utils.combine_colormaps('Oranges', 'Blues')
        for ax, git in zip(axes, (da0, da1)):
            git.plot.imshow(
                ax=ax, add_labels=False, vmin=-20, vmax=0,
                cmap=cmap, cbar_ax=cax1, cbar_kwargs={
                    'label': 'glacial inception threshold (K)',
                    'orientation': 'horizontal'})

        # plot difference
        cmap = glopdd_utils.combine_colormaps('Oranges_r', 'Blues')
        diff = da1 - da0
        diff.plot.imshow(
            ax=axes[2], add_labels=False, center=0,
            cmap=cmap, cbar_ax=cax2, cbar_kwargs={
                'label': 'difference (K)',
                'orientation': 'horizontal'})

    # titles for each panel
    ref, sub, suffix = {
        'fdiff': ('2', '5', r'$\,kg\,m^{-2}\,K^{-1}\,day^{-1}$'),
        'pdiff': ('constant', 'reduced', ' precipitation'),
        'sdiff': ('CHELSA-ERA5', 'CHELSA-W5E5', '')}[source]
    titles = (f'{ref}{suffix}', f'{sub}{suffix}', fr'{sub} - {ref}{suffix}')

    # set axes properties
    for ax, title in zip(axes, titles):
        ax.set_title(title)
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
