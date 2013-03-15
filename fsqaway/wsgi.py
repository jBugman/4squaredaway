# -*- coding: UTF-8 -*-
import time
import json

from flask import (
    Flask, Response,
    abort, render_template, request, redirect, url_for
)
from flask.ext.cache import Cache

from fsqaway.log import get_logger
from fsqaway.models import Venue, Category
from fsqaway.foursquare_api import FoursquareAPI


app = Flask(
    '4squaredaway',
    template_folder='templates',
    static_folder='static'
)
app.logger.handlers = []
app.config.from_object('fsqaway.config')
cache = Cache(app, with_jinja2_ext=False)
api = FoursquareAPI(cache)
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


def render_venue_list(venues, format):
    if format == 'json':
        return Response(
            json.dumps(venues, indent=2),
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
            venues=sorted(venues, key=venue_comparator)
        )

    if format == 'csv':
        def generate_csv(data):
            for row in data:
                yield '\t'.join((unicode(x) for x in row)) + '\n'

        return Response(generate_csv(
            list(Venue(venue)) for venue in venues
        ), mimetype='text/plain')


@app.route('/search/<name>')
def venue_search(name):
    format = request.args.get('format', 'html')
    logger.debug('Search \'%s\' format=%s' % (name, format))
    result = api.search_with_intent(name, intent='browse')
    return render_venue_list(result['venues'], format)


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
    categories = api.get_categories()
    # result = [Category(x) for x in categories]
    result = cleanup_categories(categories)

    if filtered:
        result = filter_categories(result)

    return Response(
        json.dumps(result, indent=2),
        # result,
        mimetype='application/json'
    )
