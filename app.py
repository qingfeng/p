# a dummy wsgi app
def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ["hello, world!"]
