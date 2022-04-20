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
    'Altai':          (95, 50, [-750e3,-150e3, -300e3, 300e3]),
    'Putorana':       (95, 70, [-300e3, 200e3, -450e3, 150e3]),
    'Sayan':          (95, 50, [-150e3, 550e3, +050e3, 550e3]),
    'Khangai':        (95, 50, [ 150e3, 600e3, -400e3,-200e3]),
    'Transbaikal':   (115, 55, [-450e3, 350e3, -100e3, 500e3]),
    #'Stanovoy':      (130, 55, [-100e3, 300e3, +000e3, 200e3]),
    'Verkhoyansk':   (130, 65, [-250e3, 350e3, -200e3, 600e3]),
    #'YamAlin':       (135, 52, [-100e3, 100e3, -200e3, 200e3]),
    'Kolyma':        (160, 60, [-450e3, 350e3, -100e3, 600e3]),
    'Chersky':       (160, 60, [-1250e3,-450e3,-050e3, 1150e3]),
    'Kamchatka':     (160, 60, [-300e3, 200e3,-1000e3, 100e3]),
    'Anadyr':        (160, 60, [ 000e3, 500e3,  550e3,1050e3]),
    'Koryak':        (160, 60, [ 200e3,1000e3, -50e3, 550e3]),
    'Chukotka':      (160, 60, [500e3, 1500e3, 550e3, 1200e3]),
    'Brooks':       (-152, 70, [-450e3, 450e3, -400e3, 000e3]),
    'Ahklun':       (-160, 60, [-150e3, 150e3, -150e3, 150e3])}


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertAzimuthalEqualArea(
        central_longitude=135, central_latitude=60))
    ax.set_extent([-4e6, 4e6, -1e6, 3e6], crs=ax.projection)
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
    util.draw_model_domains(ax=ax, domains=DOMAINS, color='C3', grid=False, zorder=3)

    # add legend
    ax.legend([mpl.patches.Patch(facecolor='C0', alpha=0.75),
               mpl.patches.Patch(facecolor='C1', alpha=0.75),
               mpl.patches.Patch(facecolor='none', edgecolor='C3')],
              ['MIS 2 (Batchelor et al., 2019)',
               'MIS 4 (Batchelor et al., 2019)',
               'Planned model domains'], loc='upper left')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
