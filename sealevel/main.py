from tempfile import NamedTemporaryFile
from bottle import route, request, view, response
from PIL import Image
import numpy as np

@route('/')
@view('sealevel/views/index')
def index():
    site = "%s://%s" % (request.urlparts.scheme, request.urlparts.netloc)
    return {"site": site}

@route('/tile/')
def tile():
    tile = NamedTemporaryFile(mode='w+b', suffix='png')

    data = np.random.rand(500, 500)
    data = (data * 255).round(decimals=0)

    image = Image.fromarray(data)
    image = image.convert("RGB")
    image.save(tile, format="PNG")

    tile.seek(0)

    response.content_type = "image/png"
    return tile
