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
    ('parentheses', [
        'MediaWiki:Parentheses/qqq',
    ]),
])
def test_key_to_titles(key: str, titles: List[str]):
    assert translate_link.key_to_titles(key, test_session) == titles


@pytest.mark.parametrize('title, url', [
    ('MediaWiki:Wikibase-setlabel-label/qqq',
     'https://translatewiki.net/w/i.php?title=Special:Translate&showMessage=wikibase-setlabel-label&group=ext-wikibase-repo-interface&language=qqq'),  # noqa: E501
    ('Wikimedia:Wikidata-lexeme-forms-duplicates-warning/qqq',
     'https://translatewiki.net/w/i.php?title=Special:Translate&showMessage=wikidata-lexeme-forms-duplicates-warning&group=wikidata-lexeme-forms&language=qqq'),  # noqa: E501
    ('MediaWiki:Parentheses/qqq',
     'https://translatewiki.net/w/i.php?title=Special:Translate&showMessage=parentheses&group=core&language=qqq'),  # noqa: E501
])
def test_title_to_url(title: str, url: str):
    assert translate_link.title_to_url(title, test_session) == url


@pytest.mark.parametrize('url, language_code, expected', [
    ('https://translatewiki.net/w/i.php?title=Special:Translate&showMessage=wikibase-setlabel-label&group=ext-wikibase-repo-interface&language=qqq',  # noqa: E501
     'en',
     'https://translatewiki.net/w/i.php?title=Special%3ATranslate&showMessage=wikibase-setlabel-label&group=ext-wikibase-repo-interface&language=en'),  # noqa: E501
    ('http://example.com/?language=qqq&other_language=qqq',
     'de',
     'http://example.com/?language=de&other_language=qqq'),
    ('http://example.com?language=qqq#&language=qqq',
     'pt',
     'http://example.com?language=pt#&language=qqq'),
])
def test_url_set_language(url: str, language_code: str, expected: str):
    assert translate_link.url_set_language(url, language_code) == expected
