#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD glacial inception threshold."""

import xarray as xr
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 87))
    ax0 = fig.add_axes([0, 0, 1, 1])
    ax1 = fig.add_axes_mm([10, 25, 25, 25])  # South Pacific
    ax2 = fig.add_axes_mm([70, 32.5, 25, 25])  # South Atlantic
    cax = fig.add_axes_mm([125, 35, 30, 2.5])  # Australia

    # plot global inception threshold (FIXME negate in processing?)
    git = xr.open_mfdataset('../data/processed/glopdd.git.cw5e5.nc').git
    sel = git.sel(lon=slice(None, None, 10), lat=slice(None, None, 10))
    sel.notnull().plot.contour(
        ax=ax0, add_labels=False, colors='0.9', levels=[0], linewidths=5, zorder=-1)
    # sel.plot.contour(
    #     ax=ax0, colors='w', levels=[0.5], linestyles=['--'])
    sel.plot.imshow(
        ax=ax0, add_labels=False, cmap='plasma_r', cbar_ax=cax, cbar_kwargs={
            'label': 'glacial inception threshold (K)',
            'orientation': 'horizontal'})
    sel = git.sel(lon=slice(-76.5, -70.5), lat=slice(-52, -46))
    sel.notnull().plot.contour(
        ax=ax1, add_labels=False, colors='0.9', levels=[0], linewidths=5, zorder=-1)
    sel.plot(
        ax=ax1, add_colorbar=False, add_labels=False, cmap='plasma_r')
    sel = git.sel(lon=slice(7.7, 8.3), lat=slice(46.2, 46.8))
    sel.notnull().plot.contour(
        ax=ax2, add_labels=False, colors='0.9', levels=[0], linewidths=5, zorder=-1)
    sel.plot(
        ax=ax2, add_colorbar=False, add_labels=False, cmap='plasma_r')

    # set axes properties
    ax0.set_aspect('equal')
    ax0.set_xticks(range(-180, 180, 30))
    ax0.set_yticks(range(-90, 90, 30))
    for ax in (ax1, ax2):
        ax.set_aspect('equal')
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
    cax.grid(False)

    # save figure
    fig.savefig(__file__[:-3], dpi=254)


if __name__ == '__main__':
    main()
