#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Asia mountain ice sheet glaciations map."""


import matplotlib as mpl
import cartopy.crs as ccrs
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import absplots as apl
import util


DOMAINS = {
    'Altai':          (92, 48, [-100e3, 100e3, -100e3, 100e3]),
    'Putorana':       (94, 69, [-100e3, 100e3, -100e3, 100e3]),
    'Sayan':          (98, 53, [-100e3, 100e3, -100e3, 100e3]),
    'Khangai':       (100, 49, [-100e3, 100e3, -100e3, 100e3]),
    'Transbaikal':   (117, 57, [-100e3, 100e3, -100e3, 100e3]),
    'Stanovoy':      (126, 56, [-100e3, 100e3, -100e3, 100e3]),
    'Verkhoyansk':   (129, 67, [-100e3, 100e3, -100e3, 100e3]),
    'YamAlin':       (135, 54, [-100e3, 100e3, -100e3, 100e3]),
    'Kolyma':        (159, 63, [-100e3, 100e3, -100e3, 100e3]),
    'Chersky':       (143, 64, [-100e3, 100e3, -100e3, 100e3]),
    'Kamchatka':     (160, 55, [-100e3, 100e3, -100e3, 100e3]),
    'Anadyr':        (170, 67, [-100e3, 100e3, -100e3, 100e3]),
    'Koryak':        (172, 62, [-100e3, 100e3, -100e3, 100e3]),
    'Chukotka':      (177, 68, [-100e3, 100e3, -100e3, 100e3]),
    'Brooks':       (-152, 68, [-100e3, 100e3, -100e3, 100e3]),
    'Ahklun':       (-161, 59, [-100e3, 100e3, -100e3, 100e3])}


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertAzimuthalEqualArea(
        central_longitude=135, central_latitude=60))
    ax.set_extent([-3.6e6, 3.6e6, -1.6e6, 3.2e6], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)

    # add etopo1bed background
    csr.add_topography('../data/external/ETOPO1_Bed_c_geotiff_asia.tif',
                       ax=ax, cmap='Greys', vmax=4500)

    # add physical elements
    cne.add_rivers(ax=ax, edgecolor='0.25', scale='50m')
    cne.add_lakes(ax=ax, edgecolor='0.25', facecolor='0.75', scale='50m')
    cne.add_coastline(ax=ax, edgecolor='0.25', scale='50m')
    cne.add_glaciers(ax=ax, edgecolor='0.25', facecolor='0.25', scale='50m')
    cne.add_graticules(ax=ax, interval=5, scale='50m')

    # add glaciers and domains
    cne.add_shapefile('../data/external/MIS4_best_estimate.shp',
                      ax=ax, alpha=0.75, facecolor='C1',
                      crs=ccrs.LambertAzimuthalEqualArea(central_latitude=90))
    cne.add_shapefile('../data/external/LGM_best_estimate.shp',
                      ax=ax, alpha=0.75, facecolor='C0')
    util.draw_model_domains(ax=ax, domains=DOMAINS, color='C3', zorder=3)

    # add legend
    ax.legend([mpl.patches.Patch(facecolor='C0', alpha=0.75),
               mpl.patches.Patch(facecolor='C1', alpha=0.75),
               mpl.patches.Patch(facecolor='none', edgecolor='C3')],
              ['MIS 2 (Batchelor et al., 2019)',
               'MIS 4 (Batchelor et al., 2019)',
               'Planned model domains'], loc='lower right')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
