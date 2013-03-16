# -*- coding: UTF-8 -*-
from gevent.wsgi import WSGIServer

from fsqaway.wsgi import app
from fsqaway.config import HTTP_PORT, DEBUG


if __name__ == '__main__':
    if DEBUG:
        app.run(
            host='0.0.0.0',
            port=HTTP_PORT,
            debug=DEBUG,
            use_evalex=False
        )
    else:
        WSGIServer(('', HTTP_PORT), app).serve_forever()
