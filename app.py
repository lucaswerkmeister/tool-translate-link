# -*- coding: utf-8 -*-

import flask
import mwapi  # type: ignore
import os
import random
import re
import string
import toolforge
from typing import List, Optional
import warnings
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


@app.route('/show/', methods=['POST'])
def index_show() -> werkzeug.Response:
    url = flask.url_for('show',
                        key=flask.request.form['key'],
                        language_code=flask.request.form['language-code'])
    return flask.redirect(url)


@app.route('/redirect/', methods=['POST'])
def index_redirect() -> werkzeug.Response:
    url = flask.url_for('redirect',
                        key=flask.request.form['key'],
                        language_code=flask.request.form['language-code'])
    return flask.redirect(url)


@app.route('/show/<key>/<language_code>')
def show(key: str, language_code: str) -> str:
    session = mwapi.Session(host='https://translatewiki.net',
                            user_agent=user_agent)
    urls = []
    for title in key_to_titles(key, session):
        url = title_to_url(key, title, session)
        url = url_set_language(url, language_code)
        urls.append(url)
    return flask.render_template('show.html',
                                 key=key,
                                 language_code=language_code,
                                 urls=urls)


@app.route('/redirect/<key>/<language_code>')
def redirect(key: str, language_code: str) -> werkzeug.Response:
    session = mwapi.Session(host='https://translatewiki.net',
                            user_agent=user_agent)
    titles = key_to_titles(key, session)
    if len(titles) != 1:
        # point to show(), which can handle other result counts
        return flask.redirect(flask.url_for('show',
                                            key=key,
                                            language_code=language_code),
                              code=303)  # See Other
    title = titles[0]
    url = title_to_url(key, title, session)
    url = url_set_language(url, language_code)
    return flask.redirect(url)


def key_to_titles(key: str, session: mwapi.Session) -> List[str]:
    search = session.get(action='query',
                         list='search',
                         srsearch=f'intitle:"{key}/qqq"',
                         srnamespace='*',
                         srinfo=[],
                         srprop=[],
                         formatversion=2)['query']['search']
    pattern = r'[^:]*:' + re.escape(f'{key}/qqq')
    return [result['title']
            for result in search
            if re.fullmatch(pattern, result['title'], re.I)]


def title_to_url(key: str, title: str, session: mwapi.Session) -> str:
    """Return some translate URL for the given title."""
    return (title_to_url_groups(key, title, session)
            or title_to_url_ttm(title, session)
            or title_to_url_edit(title))


def title_to_url_groups(key: str, title: str, session: mwapi.Session) \
        -> Optional[str]:
    """Try to find a translate URL for the given title using GroupsAid.

    It’s not really clear if this can fail at all, to be honest."""
    groups = session.get(action='translationaids',
                         title=title,
                         prop=['groups'])['helpers']['groups']
    if groups:
        group = groups[0]
        return ('https://translatewiki.net/w/i.php'
                '?title=Special:Translate'
                f'&showMessage={key}'
                f'&group={group}'
                '&language=qqq')
    else:
        warnings.warn(f'translationaids gave no groups for {title} ({key})')
        return None


def title_to_url_ttm(title: str, session: mwapi.Session) -> Optional[str]:
    """Try to find a translate URL for the given title using TTM.

    This can fail if there are many messages with the same message text,
    in which case the TTM results may not include the original message."""
    ttmserver = session.get(action='translationaids',
                            title=title,
                            prop=['ttmserver'])['helpers']['ttmserver']
    urls = ['https://translatewiki.net' + result['editorUrl']
            for result in ttmserver
            if result['location'] == title]
    assert len(urls) <= 1
    return urls[0] if urls else None


def title_to_url_edit(title: str) -> str:
    """Return an action=edit URL for the given title.

    This should only be used as a final fallback,
    but is better than nothing."""
    return f'https://translatewiki.net/w/i.php?title={title}&action=edit'


def url_set_language(url: str, language_code: str) -> str:
    url = re.sub(r'([?&])language=qqq(&|#|$)',
                 r'\1language=' + language_code + r'\2',
                 url)
    url = re.sub(r'/qqq(&|#|$)',
                 r'/' + language_code + r'\1',
                 url)
    return url


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
