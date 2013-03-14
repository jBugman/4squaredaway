# -*- coding: UTF-8 -*-
import time
import json

from flask import (
    Flask, Response,
    abort, render_template, request, redirect, url_for
)
from flask.ext.cache import Cache
from foursquare import Foursquare

from .config import (
    FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
    SEARCH_CACHE_TIMEOUT
)
from .log import get_logger


NEAR = 'Москва'

app = Flask(
    '4sqaredaway',
    template_folder='templates',
    static_folder='static'
)
app.logger.handlers = []
app.config.from_object('fsqaway.config')
cache = Cache(app, with_jinja2_ext=False)
fsq = Foursquare(
    client_id=FOURSQUARE_CLIENT_ID,
    client_secret=FOURSQUARE_CLIENT_SECRET
)
logger = get_logger('4sqaredaway')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for(
        'static',
        filename='poweredByFoursquare_16x16.png'
    ))


@app.route('/')
def index():
    return '4sqaredaway'


@cache.memoize(SEARCH_CACHE_TIMEOUT)
def search_with_intent(search_term, intent='match', near=NEAR):
    logger.debug('API call \'%s\' intent=%s' % (search_term, intent))
    return fsq.venues.search(params={
        'intent': intent,
        'near': NEAR,
        'query': search_term.encode('UTF-8'),
        'limit': 50
    })


@app.route('/search/<name>')
def venue_search(name):
    as_json = request.args.get('json', False)
    result = search_with_intent(name, intent='browse')
    if as_json:
        return Response(
            json.dumps(result['venues'], indent=2),
            mimetype='application/json'
        )
    else:
        def venue_comparator(venue):
            if 'categories' in venue and venue['categories']:
                return venue['categories'][0]['name']
            else:
                return ''
        return render_template(
            'venue_list.html',
            venues=sorted(result['venues'], key=venue_comparator)
        )
