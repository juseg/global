#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Arctic Asia glaciations map."""


import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import absplots as apl
import util


def draw_shapefile(filename, ax=None, crs=None, **kwargs):
    """Add shapefile geometries without duplicates."""
    ax = ax or plt.gca()
    crs = crs or ccrs.PlateCarree()
    shp = cshp.Reader(filename)
    geometries = []
    for geom in shp.geometries():
        if geom not in geometries:
            geometries.append(geom)
    ax.add_geometries(geometries, crs, **kwargs)
    shp = None


def add_legend(ax, colors, labels, alpha=0.75, **kwargs):
    """Add a standalone legend."""
    artists = [mpl.patches.Patch(color=c, alpha=alpha) for c in colors]
    ax.legend(artists, labels, **kwargs)


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertAzimuthalEqualArea(
        central_longitude=135, central_latitude=60))
    ax.set_extent([-6e6, 6e6, -4e6, 4e6], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)

    # add etopo1bed background
    csr.add_topography('../data/external/ETOPO1_Bed_c_geotiff_asia.tif',
                       ax=ax, cmap='Greys', vmax=6000)

    # add physical elements
    cne.add_rivers(ax=ax, edgecolor='0.25', scale='50m')
    cne.add_lakes(ax=ax, edgecolor='0.25', facecolor='0.75', scale='50m')
    cne.add_coastline(ax=ax, edgecolor='0.25', scale='50m')
    cne.add_glaciers(ax=ax, edgecolor='0.25', facecolor='0.25', scale='50m')
    cne.add_graticules(ax=ax, interval=5, scale='50m')

    # add glaciers and domains
    draw_shapefile('../data/external/lgm_simple.shp',
                   ax=ax, alpha=0.75, facecolor='C0')
    draw_shapefile('../data/external/MIS4_best_estimate.shp',
                   ax=ax, alpha=0.75, facecolor='C1',
                   crs=ccrs.LambertAzimuthalEqualArea(central_latitude=90))
    draw_shapefile('../data/external/LGM_best_estimate.shp',
                   ax=ax, alpha=0.75, facecolor='C2')

    # add legend
    add_legend(
        ax=ax, alpha=0.75, colors=['C2', 'C1', 'C0', '0.75'],
        labels=['Batchelor et al., 2019, LGM', 'Batchelor et al., 2019, MIS4',
                'Ehlers et al., 2011', 'Modern glaciers'], loc='lower right')

    # save
    util.savefig(fig)


if __name__ == '__main__':
    main()
