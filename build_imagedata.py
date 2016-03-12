"""
    Before running this command you need to download the latest elevation
    data from lantmateriet called nh_riks_Sweref_99_TM_geotiff. Put those
    files into a directory in the project root and run
    `python build_imagedata.py`
"""

import os
import georasters as gr
import numpy as np

DATA_IN = "nh_riks_Sweref_99_TM_geotiff"
OUTFILE = "elevation_data.npz"

filenames = os.listdir(DATA_IN)
# filenames = ["nh_61_3.tif"]

rasters = []
for filename in filenames:
    print "Importings raster %s" % filename
    file_path = os.path.join(DATA_IN, filename)
    rasters.append(gr.from_file(file_path))

print "Merging rasters"
data = gr.union(rasters).raster

# Data from lantmateriet has 10 decimals, none of them are significant
data = data.round(decimals=0)

# MaskedArrays can't be save to disk, convert to ndarray
data = data.filled(-1)

np.savez_compressed(OUTFILE, data)
