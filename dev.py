#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fsqaway.wsgi import app
from fsqaway.config import HTTP_PORT, DEBUG


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=HTTP_PORT,
        debug=DEBUG,
        use_evalex=False
    )
