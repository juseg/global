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
    'Hida':          (138, 36, [-50e3, -10e3, +30e3, +90e3]),
    'Kiso':          (138, 36, [-20e3, -10e3, -40e3, -20e3]),
    'Akaishi':       (138, 36, [+00e3, +30e3, -80e3, -20e3]),
    'Hidaka':        (143, 43, [-30e3, +10e3, -80e3, -20e3])}

REGIONS = {
    'Chubu':    (138, 36, [-080e3, 100e3, -120e3, 120e3]),
    'Hokkaido': (143, 43, [-100e3, 080e3, -120e3, 120e3]),
    'Japan':    (140, 40, [-500e3, 500e3, -750e3, 750e3])}

POSITIONS = {
    'Chubu':     [0.0, 0.0, 0.5, 1.0],
    'Hokkaido':  [0.5, 0.0, 0.5, 1.0],
    'Japan':     [0.3, 0.4, 0.4, 0.5]}

VOLCANOES = {
    'Fuji':     (138.73, 35.36),
    'Norikura': (137.55, 36.11),
    'Ontake':   (137.48, 35.89),
    'Asahi':    (142.85, 43.66)}


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    lonlat = ccrs.PlateCarree()
    for region, (lon, lat, extent) in REGIONS.items():
        ax = fig.add_axes(
            POSITIONS[region], projection=ccrs.LambertAzimuthalEqualArea(
                central_longitude=lon, central_latitude=lat))
        ax.set_extent(extent, crs=ax.projection)
        ax.set_rasterization_zorder(2.5)

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
        cne.add_shapefile('../data/external/lgm.shp', ax=ax, alpha=0.75,
                          facecolor='C0', edgecolor='C0')
        util.draw_model_domains(ax=ax, domains=DOMAINS, color='C3', grid=False,
                                names=(region != 'Japan'))

        # on Japan map, plot inset regions
        if region == 'Japan':
            util.draw_model_domains(ax=ax, color='0.25', domains={
                k: REGIONS[k] for k in REGIONS if k != 'Japan'})

        # on map insets, add active volcanoes
        if region != 'Japan':
            for name, coords in VOLCANOES.items():
                ax.plot(*coords, color='C3', marker='o', transform=lonlat)
                ax.text(*coords, name+'\n\n', color='C3', fontsize=6,
                        fontweight='bold', transform=lonlat, va='center')

    # add legend
    fig.legend([mpl.patches.Patch(facecolor='C0', alpha=0.75),
                mpl.patches.Patch(facecolor='none', edgecolor='C3')],
               ['MIS 4 (Ehlers et al., 2011)', 'Planned model domains'],
               loc='upper right')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
