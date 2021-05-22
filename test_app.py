import pytest  # type: ignore

import app as translate_link


@pytest.fixture
def client():
    translate_link.app.testing = True
    client = translate_link.app.test_client()

    with client:
        yield client
    # request context stays alive until the fixture is closed
