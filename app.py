# -*- coding: utf-8 -*-

import flask
import mwapi  # type: ignore
import random
import re
import string
import toolforge
from typing import List
import werkzeug
import yaml


app = flask.Flask(__name__)

user_agent = toolforge.set_user_agent(
    'translate-link',
    email='translate-link@lucaswerkmeister.de')

app.config.from_file('config.yaml',
                     load=toolforge.load_private_yaml,
                     silent=True)
app.config.from_prefixed_env('TOOL',
                             loads=yaml.safe_load)
if app.secret_key is None:
    print('No configuration found, assuming local development setup')
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


@app.route('/healthz')
def health() -> str:
    return ''


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
    """Find a translate URL for the given title using GroupsAid."""
    groups = session.get(action='translationaids',
                         title=title,
                         prop=['groups'])['helpers']['groups']
    if groups:
        group = groups[0]
        if 'mediawiki' in groups:
            key = mediawiki_title_to_key(title, key)
        return ('https://translatewiki.net/w/i.php'
                '?title=Special:Translate'
                f'&showMessage={key}'
                f'&group={group}'
                '&language=qqq')
    else:
        description = f'translationaids gave no groups for {title} ({key})'
        flask.abort(500, description=description)


def mediawiki_title_to_key(title: str, original_key: str) -> str:
    """Turn a title for a MediaWiki message back into a message key.

    This is necessary because the key may be in the wrong case;
    for MediaWiki messages, we can determine the correct key from the title
    (convert first character to lowercase, use the title’s case for the rest).
    Do not use this function for non-MediaWiki titles or keys:
    we don’t know how to convert the case for other systems."""
    match = re.fullmatch(r'[^:]*:(.*)/qqq', title)
    if match:
        title_text = match[1]
        key = title_text[0].lower() + title_text[1:]
        if key.lower() == original_key.lower():
            return key
        description = (f'title {title} appears to belong to key {key}, '
                       f'expected {original_key}')
    else:
        description = f'title {title} does not match expected format'
    flask.abort(500, description=description)


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
