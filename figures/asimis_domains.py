#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Arctic Asia glaciations map."""


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
    [geometries.append(g) for g in shp.geometries() if g not in geometries]
    ax.add_geometries(geometries, crs, **kwargs)
    shp = None


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertAzimuthalEqualArea(
        central_longitude=135, central_latitude=60))
    ax.set_extent([-6e6, 6e6, -4e6, 4e6], crs=ax.projection)

    # add etopo1bed background
    csr.add_topography('../data/external/ETOPO1_Bed_c_geotiff_asia.tif',
                       ax=ax, cmap='Greys', vmax=6000)

    # add physical elements
    cne.add_rivers(ax=ax, edgecolor='0.25', scale='50m')
    cne.add_lakes(ax=ax, edgecolor='0.25', facecolor='0.75', scale='50m')
    cne.add_coastline(ax=ax, edgecolor='0.25', scale='50m')
    cne.add_glaciers(ax=ax, edgecolor='0.25', facecolor='0.25', scale='50m')
    cne.add_graticules(ax=ax, interval=5, scale='50m')

    # add glaciers
    draw_shapefile('../data/external/lgm_simple.shp',
                   ax=ax, alpha=1.0, facecolor='C0')

    # save
    util.savefig(fig)


if __name__ == '__main__':
    main()
