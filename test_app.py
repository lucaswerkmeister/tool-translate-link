import pytest  # type: ignore
import re

import app as translate_link


@pytest.fixture
def client():
    translate_link.app.testing = True
    client = translate_link.app.test_client()

    with client:
        yield client
    # request context stays alive until the fixture is closed


def test_csrf_token_generate():
    with translate_link.app.test_request_context():
        token = translate_link.csrf_token()
        assert token != ''


def test_csrf_token_save():
    with translate_link.app.test_request_context() as context:
        token = translate_link.csrf_token()
        assert token == context.session['csrf_token']


def test_csrf_token_load():
    with translate_link.app.test_request_context() as context:
        context.session['csrf_token'] = 'test token'
        assert translate_link.csrf_token() == 'test token'


def test_praise(client):
    # default praise
    response = client.get('/praise')
    html = response.get_data(as_text=True)
    assert '<h2>You rock!</h2>' in html

    # extract CSRF token
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]*)"', html)
    assert match is not None
    csrf_token = match.group(1)

    referrer = translate_link.full_url('praise')
    headers = {'Referer': referrer}

    # update praise
    response = client.post('/praise',
                           data={'csrf_token': csrf_token,
                                 'praise': 'How cool!'},
                           headers=headers)
    html = response.get_data(as_text=True)
    assert '<h2>How cool!</h2>' in html
    assert 'You rock!' not in html

    # try to update praise with wrong CSRF token
    response = client.post('/praise',
                           data={'csrf_token': 'wrong ' + csrf_token,
                                 'praise': 'Boo!'},
                           headers=headers)
    html = response.get_data(as_text=True)
    assert '<h2>Boo!</h2>' not in html
    assert '<h2>How cool!</h2>' in html
    assert 'value="Boo!"' in html  # input is repeated
