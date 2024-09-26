#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception threshold."""

import shapely
import matplotlib.pyplot as plt
import hyoga
import glopdd_utils


def plot(source='cw5e5'):
    """Main program called during execution."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    cax = fig.add_axes([2/36, 4/18, 12/36, 1/18])

    # plot glacial inception threshold
    west, south, east, north = 2, 49.25, 7, 51.75
    if source in ('cera5', 'cw5e5'):
        cmap = 'Blues'
    else:
        cmap = glopdd_utils.get_plot_kwargs(source=source)['cmap']
    with glopdd_utils.open_inception_threshold(source=source) as git:
        git = git.sel(lon=slice(west, east), lat=slice(south, north))
        git.plot.imshow(
            ax=ax, add_labels=False, cmap=cmap, cbar_ax=cax, cbar_kwargs={
                'label': glopdd_utils.get_plot_title(source=source),
                'orientation': 'horizontal'})

    # plot geographic vectors
    countries = hyoga.open.natural_earth('admin_0_countries', 'cultural')
    belux = countries[countries.NAME.isin(('Belgium', 'Luxembourg'))]
    corners = [(west, south), (east, south), (east, north), (west, north)]
    mask = shapely.Polygon(corners).difference(belux.dissolve().geometry)
    mask.plot(ax=ax, fc='w', alpha=0.75)
    belux.plot(ax=ax, fc='none', ec='0.25')
    cities = hyoga.open.natural_earth('populated_places', 'cultural')
    cities = cities[cities.SOV0NAME.isin(('Belgium', 'Luxembourg'))]
    cities.plot(ax=ax, color='0.25')

    # set axes properties
    ax.set_aspect('equal')
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    cax.grid(False)

    # mysterious tick labels
    # cax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('???'))

    # return figure
    return fig


def main():
    """Main program called during execution."""
    sources = ['cera5', 'cw5e5', 'fdiff', 'pdiff', 'sdiff']
    plotter = glopdd_utils.MultiPlotter(plot, sources=sources)
    plotter()


if __name__ == '__main__':
    main()
