#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Asia Japan mountain paleoglaciers map."""


import matplotlib as mpl
import cartopy.crs as ccrs
import cartowik.decorations as cde
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import absplots as apl
import util


DOMAINS = {
    'Hida':          (138, 36, [-40e3, -20e3, +40e3, +60e3]),
    'Kiso':          (138, 36, [-30e3, -10e3, -40e3, -20e3]),
    'Akaishi':       (138, 36, [+10e3, +30e3, -40e3, -20e3]),
    'Hidaka':        (143, 43, [-30e3, -10e3, -40e3, -20e3])}

REGIONS = {
    'Chubu':    (138, 36, [-070e3, 080e3, -095e3, 105e3], [.0, .0, .5, 1.]),
    'Hokkaido': (143, 43, [-100e3, 050e3, -110e3, 090e3], [.5, .0, .5, 1.]),
    'Japan':    (140, 40, [-500e3, 500e3, -750e3, 750e3], [.3, .4, .4, .5])}


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    grid = dict()
    for region, (lon, lat, extent, pos) in REGIONS.items():
        ax = fig.add_axes(pos, projection=ccrs.LambertAzimuthalEqualArea(
            central_longitude=lon, central_latitude=lat))
        ax.set_extent(extent, crs=ax.projection)

        # add region label
        cde.add_subfig_label(region, ax=ax)

        # add etopo1bed background
        csr.add_topography('../data/external/{}_{}.tif'.format(
            'ETOPO1_Bed_c_geotiff' if region == 'Japan' else 'srtm',
            region.lower()), ax=ax, cmap='Greys', vmax=4500)

        # add physical elements
        scale = '50m' if region == 'Japan' else '10m'
        cne.add_rivers(ax=ax, edgecolor='0.25', scale=scale)
        cne.add_lakes(ax=ax, edgecolor='0.25', facecolor='0.75', scale=scale)
        cne.add_coastline(ax=ax, edgecolor='0.25', scale=scale)
        cne.add_graticules(ax=ax, interval=5, scale=scale)

        # add glaciers and domains
        cne.add_shapefile('../data/external/lgm.shp',
                          ax=ax, alpha=0.75, facecolor='C0')
        util.draw_model_domains(ax=ax, domains=DOMAINS, grid=False, color='C3')

    # add legend
    fig.legend([mpl.patches.Patch(facecolor='C0', alpha=0.75),
                mpl.patches.Patch(facecolor='none', edgecolor='C3')],
               ['MIS 4 (Ehlers et al., 2011)', 'Planned model domains'],
               loc='upper right')

    # save
    util.savefig(fig)


if __name__ == '__main__':
    main()
