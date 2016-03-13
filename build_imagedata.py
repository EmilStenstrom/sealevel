"""
    Before running this command you need to download the latest elevation
    data from lantmateriet called nh_riks_Sweref_99_TM_geotiff.

    Merge all the geotiff files into one big image:
    $ mkdir nh_riks_WGS84_geotiff
    $ gdal_merge.py -o nh_riks_Sweref_99_TM_geotiff/out.tif nh_riks_Sweref_99_TM_geotiff/*

    Now warp the images from SWEREF99TM to WGS84
    $ gdalwarp -t_srs "EPSG:4326" nh_riks_Sweref_99_TM_geotiffout.tif nh_riks_WGS84_geotiff/out.tif

    And lastly produce the elevation file from that data:
    `python build_imagedata.py`
"""

import georasters as gr
import numpy as np

DATA_IN = "nh_riks_WGS84_geotiff/out.tif"
# DATA_IN = "nh_riks_WGS84_geotiff/nh_61_3.tif"
OUTFILE = "elevation_data.npz"

data = gr.from_file(DATA_IN).raster

# Data from lantmateriet has 10 decimals, none of them are significant
data = data.round(decimals=0)

# MaskedArrays can't be save to disk, convert to ndarray
data = data.filled(101)

# We don't care about data larger than 255 meters, which will convert to white
data = data.clip(0, 101)

np.savez_compressed(OUTFILE, data)
