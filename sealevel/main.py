from tempfile import NamedTemporaryFile
from collections import namedtuple
from bottle import route, request, view, response, abort
from PIL import Image
import numpy as np

# Load data file into memory when webserver starts
INFILE = "elevation_data.npz"
# ELEVATION_DATA = np.load(INFILE)["arr_0"]

LatLon = namedtuple("LatLon", ["lat", "lon"])
ELEVATION_TOPLEFT = LatLon(7.3987178, 69.4092519)
ELEVATION_BOTTOMRIGHT = LatLon(27.5472122, 54.7969333)

@route('/')
@view('sealevel/views/index')
def index():
    site = "%s://%s" % (request.urlparts.scheme, request.urlparts.netloc)
    return {"site": site}

@route('/tile/')
def tile():
    nw_lat = float(request.query.nw_lat)
    nw_lng = float(request.query.nw_lng)
    se_lat = float(request.query.se_lat)
    se_lng = float(request.query.se_lng)

    if not (ELEVATION_TOPLEFT.lat < nw_lat < ELEVATION_BOTTOMRIGHT.lat):
        abort(404, "Nw_lat out of bounds")

    if not (ELEVATION_BOTTOMRIGHT.lon < nw_lng < ELEVATION_TOPLEFT.lon):
        abort(404, "Nw_lng out of bounds")

    if not (ELEVATION_TOPLEFT.lat < se_lat < ELEVATION_BOTTOMRIGHT.lat):
        abort(404, "Se_lat out of bounds")

    if not (ELEVATION_BOTTOMRIGHT.lon < se_lng < ELEVATION_TOPLEFT.lon):
        abort(404, "Se_lng out of bounds")

    assert False, (nw_lat, nw_lng, se_lat, se_lng)

    tile = NamedTemporaryFile(mode='w+b')

    nrows, ncols = 256, 256
    startrow, startcol = 0, 0
    max_rows, max_cols = len(ELEVATION_DATA), len(ELEVATION_DATA[0])

    row_from = min(startrow, max_rows)
    row_to = min(startrow + nrows, max_rows)
    col_from = min(startcol, max_cols)
    col_to = min(startcol + ncols, max_cols)
    data = ELEVATION_DATA[row_from:row_to, col_from:col_to]
    # assert False, data

    image = Image.fromarray(data)
    image = image.convert("RGB")
    image.save(tile, format="PNG")

    tile.seek(0)

    response.content_type = "image/png"
    return tile
