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
gdalargs="-r cubic -s_srs +proj=longlat -srcnodata -2147483648 \
-dstnodata -32768 -wm 1024 -wo SOURCE_EXTRA=500"
gdalwarp -t_srs "+proj=laea +lon_0=135 +lat_0=60" \
         -te -4000000 -2000000 4000000 4000000 -tr 4000 4000 \
         $gdalargs ${file}{,_asia}.tif  # 8000x6000km @4km
gdalwarp -t_srs "+proj=laea +lon_0=140 +lat_0=40" \
         -te -1000000 -750000 1000000 750000 -tr 1000 1000 \
         $gdalargs ${file}{,_japan}.tif  # 2000x1500km @1km

# SRTM land topography data  # FIXME use pismx pseudo-boot file
wdir="http://srtm.csi.cgiar.org/SRT-ZIP/SRTM_V41/SRTM_Data_GeoTiff"
wdir="http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/tiff"
for tile in srtm_{64_05,64_06,65_04}
do
    wget -nc $wdir/$tile.zip
    unzip -n $tile.zip $tile.{hdr,tfw,tif}
done
gdalwarp -r cubic -s_srs "+proj=longlat" \
         -t_srs '+proj=laea +lon_0=138 +lat_0=36' \
         -te -100000 -150000 100000 150000 -tr 200 200 \
         srtm_64_{05,06}.tif srtm_chubu.tif  # 200x300km @200m
gdalwarp -r cubic -s_srs "+proj=longlat" \
         -t_srs '+proj=laea +lon_0=143 +lat_0=43' \
         -te -100000 -150000 100000 150000 -tr 200 200 \
         srtm_65_04.tif srtm_hokkaido.tif  # 200x300km @200m

# Ehlers et al. (2011) simplified LGM outline
wdir="http://static.us.elsevierhealth.com/ehlers_digital_maps/"
file="digital_maps_02_all_other_files.zip"
wget -nc $wdir/$file
unzip -jn $file lgm.??? lgm_alpen.???
if [ ! -f lgm_simple.shp ]
then
    ogr2ogr -where "OGR_GEOM_AREA > 1e-3" -simplify 0.01 lgm_simple.shp lgm.shp
    ogr2ogr -where "OGR_GEOM_AREA > 1e-3" -simplify 0.01 \
            -append lgm_simple.shp lgm_alpen.shp
fi

# Batchelor et al. (2019) LGM and MIS4 ice outlines
wget -nc https://osf.io/gzkwc/download -O LGM_best_estimate.dbf
wget -nc https://osf.io/xm6tu/download -O LGM_best_estimate.prj
wget -nc https://osf.io/9yhdv/download -O LGM_best_estimate.shp
wget -nc https://osf.io/9bjwn/download -O LGM_best_estimate.shx
wget -nc https://osf.io/6rk85/download -O MIS4_best_estimate.dbf
wget -nc https://osf.io/2jkua/download -O MIS4_best_estimate.prj
wget -nc https://osf.io/4q9f2/download -O MIS4_best_estimate.shp
wget -nc https://osf.io/kj5mv/download -O MIS4_best_estimate.shx
