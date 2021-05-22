# -*- coding: utf-8 -*-

import flask
import mwapi  # type: ignore
import os
import random
import string
import toolforge
from typing import Tuple, Union
import werkzeug
import yaml


app = flask.Flask(__name__)

user_agent = toolforge.set_user_agent(
    'translate-link',
    email='translate-link@lucaswerkmeister.de')

__dir__ = os.path.dirname(__file__)
try:
    with open(os.path.join(__dir__, 'config.yaml')) as config_file:
        app.config.update(yaml.safe_load(config_file))
except FileNotFoundError:
    print('config.yaml file not found, assuming local development setup')
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(64))
    app.secret_key = random_string


@app.route('/')
def index() -> str:
    return flask.render_template('index.html')


@app.route('/redirect/<key>/<language_code>')
def redirect(key: str, language_code: str) \
        -> Union[werkzeug.Response, Tuple[str, int]]:
    session = mwapi.Session(host='https://translatewiki.net',
                            user_agent=user_agent)
    search = session.get(action='query',
                         list='search',
                         srsearch=f'intitle:"{key}/qqq"',
                         srnamespace='*',
                         srinfo=[],
                         srprop=[],
                         formatversion=2)['query']['search']
    if len(search) != 1:
        # TODO better error handling
        return 'Message key is ambiguous or does not exist :(', 400
    title = search[0]['title']
    ttmserver = session.get(action='translationaids',
                            title=title,
                            prop=['ttmserver'])['helpers']['ttmserver']
    assert len(ttmserver) == 1
    url = 'https://translatewiki.net' + ttmserver[0]['editorUrl']
    # TODO replace the language code more robustly
    url = url.replace('language=qqq', f'language={language_code}')
    return flask.redirect(url)


@app.after_request
def deny_frame(response: flask.Response) -> flask.Response:
    """Disallow embedding the tool’s pages in other websites.

    Not every tool can be usefully embedded in other websites, but
    allowing embedding can expose the tool to clickjacking
    vulnerabilities, so err on the side of caution and disallow
    embedding. This can be removed (possibly only for certain pages)
    as long as other precautions against clickjacking are taken.
    """
    response.headers['X-Frame-Options'] = 'deny'
    return response
