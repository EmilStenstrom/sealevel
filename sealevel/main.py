from tempfile import NamedTemporaryFile
from collections import namedtuple
from bottle import route, request, view, response, abort
from PIL import Image
import numpy as np
import math

# Load data file into memory when webserver starts
INFILE = "elevation_data.npz"
ELEVATION_DATA = np.load(INFILE)["arr_0"]

LatLon = namedtuple("LatLon", ["lat", "lon"])
ELEVATION_LAT_PIXELS = 24771
ELEVATION_LON_PIXELS = 34156
ELEVATION_TOPLEFT = LatLon(69.4092519, 7.3987178)
ELEVATION_BOTTOMRIGHT = LatLon(54.7969333, 27.5472122)
ELEVATION_PIXEL_PER_LAT = ELEVATION_LAT_PIXELS / abs(ELEVATION_TOPLEFT.lat - ELEVATION_BOTTOMRIGHT.lat)
ELEVATION_PIXEL_PER_LON = ELEVATION_LON_PIXELS / abs(ELEVATION_TOPLEFT.lon - ELEVATION_BOTTOMRIGHT.lon)

@route('/')
@view('sealevel/views/index')
def index():
    site = "%s://%s" % (request.urlparts.scheme, request.urlparts.netloc)
    return {"site": site}

def _color(lat, lon):
    row = math.floor(abs(lat - ELEVATION_TOPLEFT.lat) * ELEVATION_PIXEL_PER_LAT)
    col = math.floor(abs(lon - ELEVATION_TOPLEFT.lon) * ELEVATION_PIXEL_PER_LON)
    return ELEVATION_DATA[row, col]

@route('/tile/')
def tile():
    nw_lat = float(request.query.nw_lat)
    nw_lng = float(request.query.nw_lng)
    se_lat = float(request.query.se_lat)
    se_lng = float(request.query.se_lng)

    if not (ELEVATION_BOTTOMRIGHT.lat < nw_lat < ELEVATION_TOPLEFT.lat):
        abort(404, "Nw_lat out of bounds %s" % nw_lat)

    if not (ELEVATION_TOPLEFT.lon < nw_lng < ELEVATION_BOTTOMRIGHT.lon):
        abort(404, "Nw_lng out of bounds %s" % nw_lng)

    if not (ELEVATION_BOTTOMRIGHT.lat < se_lat < ELEVATION_TOPLEFT.lat):
        abort(404, "Se_lat out of bounds %s" % se_lat)

    if not (ELEVATION_TOPLEFT.lon < se_lng < ELEVATION_BOTTOMRIGHT.lon):
        abort(404, "Se_lng out of bounds %s" % se_lng)

    tile = NamedTemporaryFile(mode='w+b')

    nrows, ncols = 256, 256

    data = np.zeros(shape=(nrows, ncols))

    for row in range(0, nrows):
        for col in range(0, ncols):
            lat = nw_lat - abs(nw_lat - se_lat) / nrows * row
            lon = nw_lng + abs(nw_lng - se_lng) / ncols * col
            data[row, col] = _color(lat, lon)

    image = Image.fromarray(data)
    image = image.convert("RGB")
    image.save(tile, format="PNG")

    tile.seek(0)

    response.content_type = "image/png"
    return tile
