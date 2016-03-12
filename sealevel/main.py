from bottle import route, request, view

@route('/')
@view('sealevel/views/index')
def index():
    site = "%s://%s" % (request.urlparts.scheme, request.urlparts.netloc)
    return {"site": site}
