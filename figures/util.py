# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Utils and parameters for the Asia project.
"""

import os
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def draw_model_domain(ax, extent, grid=True, name=None, **kwargs):
    """Draw model domain with projection axes."""
    west, east, south, north = extent
    ax.plot([west, east, east, west, west],
            [south, south, north, north, south], **kwargs)
    if grid is True:
        ax.plot([0, 0], [south, north], lw=0.5, **kwargs)
        ax.plot([west, east], [0, 0], lw=0.5, **kwargs)
        ax.plot(0, 0, marker='o', **kwargs)
    if name is not None:
        ax.text(west, north, name+'\n\n', fontsize=6, fontweight='bold',
                va='center', **{k: kwargs[k] for k in ('color', 'transform')})


def draw_model_domains(ax, domains, names=True, **kwargs):
    """Draw multiple model domains."""
    for name, (lon, lat, extent) in domains.items():
        proj = ccrs.LambertAzimuthalEqualArea(
            central_longitude=lon, central_latitude=lat)
        draw_model_domain(ax, extent, name=(name if names is True else None),
                          transform=proj, **kwargs)
