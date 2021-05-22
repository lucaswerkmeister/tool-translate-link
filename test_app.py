import mwapi  # type: ignore
import pytest  # type: ignore
from typing import List

import app as translate_link


@pytest.fixture
def client():
    translate_link.app.testing = True
    client = translate_link.app.test_client()

    with client:
        yield client
    # request context stays alive until the fixture is closed


test_user_agent = ('translate-link-tests '
                   '(https://translate-link.toolforge.org/; '
                   'translate-link@lucaswerkmeister.de)')
test_session = mwapi.Session(host='https://translatewiki.net',
                             user_agent=test_user_agent)


@pytest.mark.parametrize('key, titles',  [
    ('wikibase-setlabel-label', [
        'MediaWiki:Wikibase-setlabel-label/qqq',
    ]),
    ('wikidata-lexeme-forms-duplicates-warning', [
        'Wikimedia:Wikidata-lexeme-forms-duplicates-warning/qqq',
    ]),
])
def test_key_to_titles(key: str, titles: List[str]):
    assert translate_link.key_to_titles(key, test_session) == titles
