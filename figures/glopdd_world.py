#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception world map."""

import matplotlib.pyplot as plt
import glopdd_utils


def plot(source='cw5e5'):
    """Make plot and save figure for given source."""

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
    if source == 'fdiff':
        label = (
            r'$5-2\,kg\,m^{-2}\,K^{-1}\,day^{-1}$'
            '\ninception threshold (K)')
        props = {'cmap': 'Oranges_r'}
    elif source == 'pdiff':
        label = r'scaled$-$constant precip' + '\ninception threshold (K)'
        props = {'cmap': 'Oranges_r', 'vmax': 0}
    elif source == 'sdiff':
        label = r'CHELSA-2.1$-$CHELSA-W5E5' + '\ninception threshold (K)'
        props = {'cmap': glopdd_utils.combine_colormaps('Oranges_r', 'Blues')}
    else:
        label = 'glacial inception\nthreshold (K)'
        props = {
            'cmap': glopdd_utils.combine_colormaps('Oranges', 'Blues'),
            'vmin': -20, 'vmax': 0}

    # open global inception threshold
    with glopdd_utils.open_inception_threshold(source=source) as da:

        # plot global map
        da.isel(lat=slice(0, -1, 10), lon=slice(0, -1, 10)).plot.imshow(
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
            da.sel(lat=slice(south, north), lon=slice(west, east)).plot.imshow(
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


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5', 'fdiff', 'pdiff', 'sdiff']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
