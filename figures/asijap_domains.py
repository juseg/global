#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Asia Japan mountain paleoglaciers map."""


import matplotlib as mpl
import cartopy.crs as ccrs
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import absplots as apl
import util


DOMAINS = {
    'Hida':          (138, 36, [-40e3, -20e3, +40e3, +60e3]),
    'Kiso':          (138, 36, [-30e3, -10e3, -40e3, -20e3]),
    'Akaishi':       (138, 36, [+10e3, +30e3, -40e3, -20e3]),
    'Hidaka':        (143, 43, [-30e3, -10e3, -40e3, -20e3])}


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    ax0 = fig.add_axes(
        [0, 0, 0.5, 1], projection=ccrs.LambertAzimuthalEqualArea(
            central_longitude=138, central_latitude=36))
    ax1 = fig.add_axes(
        [0.5, 0, 0.5, 1], projection=ccrs.LambertAzimuthalEqualArea(
            central_longitude=143, central_latitude=43))
    ax0.set_extent([-75e3, 75e3, -100e3, 100e3], crs=ax0.projection)
    ax1.set_extent([-75e3, 75e3, -100e3, 100e3], crs=ax1.projection)

    # add etopo1bed background
    csr.add_topography('../data/external/srtm_chubu.tif',
                       ax=ax0, cmap='Greys', vmax=4500)
    csr.add_topography('../data/external/srtm_hokkaido.tif',
                       ax=ax1, cmap='Greys', vmax=4500)

    # add physical elements
    for ax in (ax0, ax1):
        cne.add_rivers(ax=ax, edgecolor='0.25', scale='10m')
        cne.add_lakes(ax=ax, edgecolor='0.25', facecolor='0.75', scale='10m')
        cne.add_coastline(ax=ax, edgecolor='0.25', scale='10m')
        cne.add_graticules(ax=ax, interval=1, scale='10m')

        # add glaciers and domains
        cne.add_shapefile('../data/external/lgm.shp',
                          ax=ax, alpha=0.75, facecolor='C0')
        util.draw_model_domains(ax=ax, domains=DOMAINS, color='C3', zorder=3)

    # add legend
    ax.legend([mpl.patches.Patch(facecolor='C0', alpha=0.75),
               mpl.patches.Patch(facecolor='none', edgecolor='C3')],
              ['MIS 4 (Ehlers et al., 2011)', 'Planned model domains'],
              loc='upper right')

    # save
    util.savefig(fig)


if __name__ == '__main__':
    main()
