#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception threshold."""

import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt

def cmaps(*args, n=256):
    """Merge any number of color maps into one."""
    name = ''.join(arg[:2] for arg in args)
    values = np.linspace(0, 1, int(n/len(args)))
    colors = np.vstack([mpl.colormaps[name](values) for name in args])
    return mpl.colors.LinearSegmentedColormap.from_list(name, colors)


def main():
    """Main program called during execution."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    axes = [fig.add_axes(rect) for rect in (
        [0, 0, 1, 1],
        [2/36, 5/18, 5/36, 5/18],
        [14/36, 6.5/18, 5/36, 5/18],
        [23/36, 5/18, 5/36, 5/18])]
    cax = fig.add_axes([17/36, 4.5/18, 5/36, .5/18])
    cmap = cmaps('Oranges', 'Blues')

    # open glacial inception threshold
    with xr.open_dataarray('../data/processed/glopdd.git.cw5e5.nc') as git:
        # git = git.where((-12 < git)*(git < 0))

        # for each region
        for ax, (region, bounds) in zip(axes, {
                'World': [-180, -90, 180, 90],
                'Patagonia': [-76.5, -52, -70.5, -46],
                'Alps': [7.7, 46.2, 8.3, 46.8],
                'Rwenzori': [29.5, 0, 30.5, 1]}.items()):
            west, south, east, north = bounds

            # select partial data
            if region == 'World':
                sel = git.isel(lat=slice(0, -1, 10), lon=slice(0, -1, 10))
            else:
                sel = git.sel(lat=slice(south, north), lon=slice(west, east))

            # plot image map
            if region == 'World':
                kwargs = {'cbar_ax': cax, 'cbar_kwargs': {
                    'label': 'glacial inception threshold (K)',
                    'orientation': 'horizontal'}}
            else:
                kwargs = {'add_colorbar': False}
                axes[0].indicate_inset(
                    [west, south, east-west, north-south], inset_ax=ax)
            sel.plot.imshow(
                ax=ax, add_labels=False, cmap=cmap, vmin=-20, vmax=0, **kwargs)

            # set axes properties
            ax.set_aspect('equal')
            ax.set_ylim(south, north)
            ax.set_xlim(west, east)
            if region == 'World':
                ax.set_xticks(range(-180, 180, 30))
                ax.set_yticks(range(-90, 90, 30))
            else:
                ax.set_title(region)
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)

        # set colorbar axes properties
        cax.grid(False)

    # save figure
    fig.savefig(__file__[:-3], dpi=254)


if __name__ == '__main__':
    main()
