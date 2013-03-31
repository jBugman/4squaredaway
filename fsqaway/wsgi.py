# -*- coding: UTF-8 -*-
from gevent import monkey
monkey.patch_all()

import json

from flask import (
    Flask, Response,
    abort, render_template, request, redirect, url_for
)
from flask.ext.basicauth import BasicAuth
from flask.ext.assets import Environment, Bundle

from fsqaway.log import get_logger
from fsqaway.models import Venue, Category
from fsqaway.foursquare_api import FoursquareAPI
from fsqaway.magic import Magic, THRESHOLD


ITERATIONS = 10

logger = get_logger(__name__)

app = Flask(
    '4squaredaway',
    template_folder='templates',
    static_folder='static'
)
app.logger.handlers = []
app.config.from_object('fsqaway.config')
basic_auth = BasicAuth(app)

assets = Environment(app)

api = FoursquareAPI()
magic = Magic()


@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')


@app.route('/bootstrap')
@basic_auth.required
def bootstrap():
    _MOCK_TOTAL_COUNT = 15
    _MOCK_RELEVANT_COUNT = 3

    def _mocked_venues():
        return [{
            'relevance': 15 if x < _MOCK_RELEVANT_COUNT else 0,
            'icon': ['https://foursquare.com/img/categories_v2/shops/gas_', '.png'],
            'categories': 'Gas Station / Garage',
            'url': 'https://foursquare.com/',
            'name': u'Хаус Авто Доктор',
            'address': u'Комсомольская пл., 3',
            'checkins': 96,
            'users': 26,
            'tips': 2,
            'likes': 0,
            'photos': 0,
        } for x in range(_MOCK_TOTAL_COUNT)]

    return render_template(
        'magic.html',
        venues=_mocked_venues(),
        THRESHOLD=THRESHOLD,
        relevant_count=_MOCK_TOTAL_COUNT - _MOCK_RELEVANT_COUNT
    )


@app.route('/magic')
@basic_auth.required
def venue_magic():
    logger.debug('/magic')
    result = magic.get_venues_magically()
    return render_template(
        'magic.html',
        venues=result,
        THRESHOLD=THRESHOLD,
        relevant_count=len([x for x in result if x.relevance <= THRESHOLD])
    )


def render_venue_list(venues, format):
    if format == 'json':
        return Response(
            json.dumps(venues, indent=2),
            mimetype='application/json'
        )

    if format == 'csv':
        def generate_csv(data):
            for row in data:
                yield '\t'.join((unicode(x) for x in row)) + '\n'

        return Response(generate_csv(
            list(Venue(venue)) for venue in venues
        ), mimetype='text/plain')

    abort(400, u'Поддерживаются только CSV и JSON')


@app.route('/search/<name>')
@basic_auth.required
def venue_search(name):
    format = request.args.get('format', 'html')
    iterations = int(request.args.get('iterations', ITERATIONS))
    logger.debug('Search \'%s\' format=%s n=%d' % (name, format, iterations))
    result = api.batch_search(name, iterations, filter=False)
    return render_venue_list(result, format)


@app.route('/filter/<name>')
@basic_auth.required
def venue_filter(name):
    format = request.args.get('format', 'html')
    iterations = int(request.args.get('iterations', ITERATIONS))
    logger.debug('Filter \'%s\' format=%s n=%d' % (name, format, iterations))
    result = api.batch_search(name, iterations, filter=True)
    return render_venue_list(result, format)


@app.route('/dev/categories')
@basic_auth.required
def categories_tree():
    filtered = request.args.get('filter', False)
    result = api.get_categories()

    if filtered:
        result = Category.filter(result)

    return Response(
        json.dumps(result, indent=2),
        mimetype='application/json'
    )
