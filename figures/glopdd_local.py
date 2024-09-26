#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception local showcase."""

import matplotlib.pyplot as plt
import glopdd_utils


def plot(source='cw5e5'):
    """Make plot and save figure for given source."""

    # initialize figure
    fig, axes = plt.subplots(
        figsize=(160/25.4, 80/25.4), ncols=3, gridspec_kw={
            'left': 0.5/36, 'bottom': 0.5/18, 'right': 35.5/36,
            'top': 16.5/18, 'wspace': 1/11})
    cax = fig.add_axes([15/36, 3.5/18, 6/36, 0.5/18])
    axes[1].add_patch(plt.Rectangle(
            (0, 0), 1, 4/16, alpha=0.75, ec=str(2/3), fc='w',
            transform=axes[1].transAxes))

    # choose plot regions (wsen, aspect 16x11)
    regions = {
        'Columbia & Rocky Mountains': [-120.5, 47, -115, 55],
        'Ethiopian Highlands': [35.5, 3.5, 41, 11.5],
        'Hida, Kiso & Akaishi Mountains': [137.3, 34.8, 138.95, 37.2],
        }

    # prepare plot properties
    label = glopdd_utils.get_plot_title(source=source)
    props = glopdd_utils.get_plot_kwargs(source=source)

    # open global inception threshold
    with glopdd_utils.open_inception_threshold(source=source) as da:

        # for each region
        for ax, (region, bounds) in zip(axes, regions.items()):
            west, south, east, north = bounds

            # plot regional map
            da.sel(lat=slice(south, north), lon=slice(west, east)).plot.imshow(
                ax=ax, add_labels=False, cbar_ax=cax, cbar_kwargs={
                    'label': label, 'orientation': 'horizontal'}, **props)

            # set axes properties
            ax.set_aspect('equal')
            ax.set_title(region)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5', 'fdiff', 'pdiff', 'sdiff']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
