# -*- coding: UTF-8 -*-
from gevent import monkey
monkey.patch_all()

from functools import wraps

import flask
from flask.ext.assets import Environment, Bundle
from flaskext.kvsession import KVSessionExtension

from fsqaway.config import ALLOWED_USERS
from fsqaway.log import get_logger
from fsqaway.foursquare_api import FoursquareAPI
from fsqaway.magic import Magic, THRESHOLD
from fsqaway.dao import kvstore
from fsqaway.dao.database import db


SESSION_TOKEN_KEY = 'token'
SESSION_USER_KEY = 'user'


logger = get_logger(__name__)

app = flask.Flask(
    '4squaredaway',
    template_folder='templates',
    static_folder='static'
)
app.logger.handlers = []
app.config.from_object('fsqaway.config')
assets = Environment(app)
KVSessionExtension(kvstore.get_kvstore(), app)

_api = FoursquareAPI()


def get_user_from_session():
    return flask.session.get(SESSION_USER_KEY, None)


def get_token_from_session():
    return flask.session.get(SESSION_TOKEN_KEY, None)


def get_api():
    token = get_token_from_session()
    if token is not None:
        return _api.set_token(token)
    else:
        return _api


def get_magic():
    return Magic(foursquare_api=get_api())


def update_user_in_session():
    user = get_api().get_current_user()
    flask.session[SESSION_USER_KEY] = user
    return user


def fsq_auth(f):  # pragma: no cover
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_session()
        if token is None:
            return flask.redirect(flask.url_for('login'))

        user = get_user_from_session()
        if user is None:
            user = update_user_in_session()

        if not (user.id in ALLOWED_USERS):
            flask.abort(403)

        return f(*args, **kwargs)
    return decorated


@app.route('/login')
def login():
    redirect_response = flask.redirect(flask.url_for('index'))

    user = get_user_from_session()
    if user is not None:
        return redirect_response

    logger.debug('/login')

    access_code = flask.request.args.get('code', None)
    if access_code is not None:
        flask.session[SESSION_TOKEN_KEY] = _api.auth(access_code)
        update_user_in_session()
        return redirect_response

    return flask.redirect(get_api().auth_url)


@app.route('/logout')
def logout():
    try:
        flask.session.destroy()
    except Exception:  # Crashes with empty session
        pass
    return flask.redirect(flask.url_for('index'))


@app.route('/')
@fsq_auth
def index():
    return flask.render_template('index.html')


@app.route('/bootstrap')
@fsq_auth
def bootstrap():
    return flask.render_template(
        'test.html',
        user=get_user_from_session()
    )


@app.route('/api/test')
@fsq_auth
def api_test():
    _MOCK_TOTAL_COUNT = 15
    _MOCK_RELEVANT_COUNT = 3

    import random
    import json

    def _mocked_venues():
        return [{
            'id': '{:x}'.format(random.randint(1000000, 9999999)),
            'relevance': 15 if x < _MOCK_RELEVANT_COUNT else 0,
            'icon': ['https://foursquare.com/img/categories_v2/shops/gas_', '.png'],
            'categories': ['Gas Station / Garage'],
            'url': 'https://foursquare.com/',
            'name': u'Хаус Авто Доктор',
            'address': u'Комсомольская пл., 3',
            'checkins': 96,
            'users': 26,
            'tips': 2,
            'likes': 0,
            'photos': 0,
        } for x in range(_MOCK_TOTAL_COUNT)]

    return flask.Response(
        json.dumps({
            'threshold': THRESHOLD,
            'venues': _mocked_venues(),
        }, indent=2),
        mimetype='application/json'
    )


@app.route('/magic')
@fsq_auth
def venue_magic():
    logger.debug('/magic')
    result = get_magic().get_venues_magically()
    return flask.render_template(
        'magic.html',
        venues=result,
        THRESHOLD=THRESHOLD,
        relevant_count=len([x for x in result if x.relevance <= THRESHOLD])
    )


@app.route('/api/test/review/<venue_id>')
@fsq_auth
def api_test_review_venue(venue_id):
    logger.debug('/dev/check/' + venue_id)
    db.Venue.find_and_modify(
        query={'id': venue_id},
        update={'$inc': {'reviewed': 1}},
        upsert=False,
        new=True
    )
    return 'ok'
