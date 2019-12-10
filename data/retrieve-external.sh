#!/bin/bash
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Download project external data
# ------------------------------


# make directory or update modification date
mkdir -p external
touch external
cd external

# ETOPO1 bed topography data  # FIXME use pismx pseudo-boot file
wdir="https://ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/"
wdir+="cell_registered/georeferenced_tiff"
file="ETOPO1_Bed_c_geotiff"
wget -nc $wdir/$file.zip
unzip -n $file.zip
gdalwarp -s_srs "+ellps=WGS84 +proj=lonlat" \
         -t_srs "+ellps=WGS84 +proj=laea +lon_0=135 +lat_0=60" \
         -r cubic -srcnodata -2147483648 -dstnodata -32768 \
         -te -6000000 -4000000 6000000 4000000 -tr 5000 5000 \
         -wm 1024 -wo SOURCE_EXTRA=500 ${file}{,_asia}.tif
