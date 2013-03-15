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
    SEARCH_CACHE_TIMEOUT, CATEGORIES_LIST_CACHE_TIMEOUT
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


@cache.memoize(timeout=SEARCH_CACHE_TIMEOUT)
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
        def generate_csv(data):
            for row in data:
                yield '\t'.join((unicode(x) for x in row)) + '\n'

        return Response(generate_csv((
            [
                venue['name'],
                ';'.join((x['name'] for x in venue['categories'])),
                venue['stats']['checkinsCount'],
                venue['stats']['usersCount'],
                venue['stats']['tipCount'],
                venue['likes']['count'],
                venue['specials']['count'],
                venue['location'].get('city', ''),
                venue['location'].get('address', ''),
                venue['id'],
            ] for venue in result['venues']
        )), mimetype='text/csv')


@cache.cached(timeout=CATEGORIES_LIST_CACHE_TIMEOUT)
def get_categories():
    logger.debug('API call \'Categories\'')
    return fsq.venues.categories()['categories']


def filter_categories(categories):
    result = []
    for c in categories:
        if 'Residence' not in c['name']:
            c.pop('categories', None)
            result.append(c)
        else:
            for sub_c in c['categories']:
                if 'Home (private)' not in sub_c['name']:
                    sub_c.pop('categories', None)
                    result.append(sub_c)
    return result


def cleanup_categories(categories):
    for c in categories:
        c.pop('pluralName', None)
        c.pop('shortName', None)
        icon = c.pop('icon', None)
        if icon:
            c['icon'] = icon['prefix'] + 'bg_32' + icon['suffix']
        if 'categories' in c:
            cleanup_categories(c['categories'])
            if not c['categories']:
                c.pop('categories', None)
    return categories


@app.route('/dev/categories')
def categories_tree():
    filtered = request.args.get('filter', False)

    result = cleanup_categories(get_categories())

    if filtered:
        result = filter_categories(result)

    return Response(
        json.dumps(result, indent=2),
        mimetype='application/json'
    )
