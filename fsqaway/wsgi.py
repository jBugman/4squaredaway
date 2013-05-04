# -*- coding: UTF-8 -*-
from gevent import monkey
monkey.patch_all()

import flask
from flask.ext.basicauth import BasicAuth
from flask.ext.assets import Environment, Bundle
from flaskext.kvsession import KVSessionExtension

from fsqaway.log import get_logger
from fsqaway.foursquare_api import FoursquareAPI
from fsqaway.magic import Magic, THRESHOLD
from fsqaway.dao import kvstore


SESSION_USER_KEY = 'user'


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
KVSessionExtension(kvstore.get_kvstore(), app)

api = FoursquareAPI()
magic = Magic()


@app.route('/')
@basic_auth.required
def index():
    return flask.render_template('index.html')


def get_user_from_session():
    return flask.session.get(SESSION_USER_KEY, None)


@app.route('/login')
def login():
    redirect_response = flask.redirect(flask.url_for('bootstrap'))  # FIXME

    user = get_user_from_session()
    if user is not None:
        return redirect_response

    access_code = flask.request.args.get('code', None)
    if access_code is not None:
        api.auth(access_code)
        user = api.get_current_user()
        flask.session[SESSION_USER_KEY] = user
        return redirect_response

    return flask.redirect(api.auth_url)


@app.route('/logout')
def logout():
    try:
        flask.session.destroy()
    except Exception:  # Crashes with empty session
        pass
    return flask.redirect(flask.url_for('index'))


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
        relevant_count=_MOCK_TOTAL_COUNT - _MOCK_RELEVANT_COUNT,
        user=get_user_from_session()
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
