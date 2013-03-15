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


ITERATIONS = 10

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
    iterations = int(request.args.get('iterations', ITERATIONS))
    logger.debug('Search \'%s\' format=%s n=%d' % (name, format, iterations))
    result = api.batch_search(name, iterations, filter=False)
    return render_venue_list(result, format)


@app.route('/filter/<name>')
def venue_filter(name):
    format = request.args.get('format', 'html')
    iterations = int(request.args.get('iterations', ITERATIONS))
    logger.debug('Filter \'%s\' format=%s n=%d' % (name, format, iterations))
    result = api.batch_search(name, iterations, filter=True)
    return render_venue_list(result, format)


@app.route('/dev/categories')
def categories_tree():
    filtered = request.args.get('filter', False)
    categories = api.get_categories()
    # result = [Category(x) for x in categories]
    result = Category.cleanup(categories)

    if filtered:
        result = Category.filter(result)

    return Response(
        json.dumps(result, indent=2),
        # result,
        mimetype='application/json'
    )
