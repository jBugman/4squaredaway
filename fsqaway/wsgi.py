# -*- coding: UTF-8 -*-
from gevent import monkey
monkey.patch_all()

import flask
from flask.ext.basicauth import BasicAuth
from flask.ext.assets import Environment, Bundle

from fsqaway.log import get_logger
from fsqaway.foursquare_api import FoursquareAPI
from fsqaway.magic import Magic, THRESHOLD


logger = get_logger(__name__)

app = flask.Flask(
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
    return flask.render_template('index.html')


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

    return flask.render_template(
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
    return flask.render_template(
        'magic.html',
        venues=result,
        THRESHOLD=THRESHOLD,
        relevant_count=len([x for x in result if x.relevance <= THRESHOLD])
    )
