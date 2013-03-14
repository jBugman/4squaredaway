# -*- coding: UTF-8 -*-
import time
import json
from cStringIO import StringIO
import csv

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
    '4squaredaway',
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
logger = get_logger('4squaredaway')


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
    format = request.args.get('format', 'html')
    logger.debug('Search \'%s\' format=%s' % (name, format))
    result = search_with_intent(name, intent='browse')

    if format == 'json':
        return Response(
            json.dumps(result['venues'], indent=2),
            mimetype='application/json'
        )

    if format == 'html':
        def venue_comparator(venue):
            if 'categories' in venue and venue['categories']:
                return venue['categories'][0]['name']
            else:
                return ''
        return render_template(
            'venue_list.html',
            venues=sorted(result['venues'], key=venue_comparator)
        )

    if format == 'csv':
        si = StringIO()
        cw = csv.writer(si, dialect=csv.excel)
        for venue in result['venues']:
            cw.writerow([
                venue['name'].encode('UTF-8'),
                ';'.join((x['name'] for x in venue['categories'])).encode('UTF-8'),
                venue['stats']['checkinsCount'],
                venue['stats']['usersCount'],
                venue['stats']['tipCount'],
                venue['likes']['count'],
                venue['specials']['count'],
                venue['location'].get('city', '').encode('UTF-8'),
                venue['location'].get('address', '').encode('UTF-8'),
                venue['id'].encode('UTF-8'),
            ])
        return Response(
            si.getvalue().decode('UTF-8').encode('cp1251', 'replace'),
            content_type='text/csv; charset=cp1251'
        )
