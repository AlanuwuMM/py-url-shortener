from unittest.mock import patch

from app.models import Urls


def test_home_get_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Py URL Shortener' in response.data or b'form' in response.data.lower()


@patch('app.blueprints.main.routes.url_checker', return_value=True)
def test_home_post_valid_alive_url(mock_checker, client):
    response = client.post('/', data={'long_url': 'https://valid-and-alive.example.com'})
    assert response.status_code == 200
    assert b'http' in response.data


@patch('app.blueprints.main.routes.url_checker', return_value=False)
def test_home_post_dead_url_shows_message(mock_checker, client):
    response = client.post('/', data={'long_url': 'https://dead.example.com'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'dead'.encode() in response.data.lower() or b'seems' in response.data


def test_home_post_invalid_url_format(client):
    response = client.post('/', data={'long_url': 'no-es-una-url'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'valid' in response.data.lower() or b'link' in response.data.lower()


def test_home_post_empty_url(client):
    response = client.post('/', data={'long_url': ''}, follow_redirects=True)
    assert response.status_code == 200


def test_redirect_existing_short_url(client, db):
    entry = Urls(short_url='goto01', long_url='https://destino.example.com')
    db.session.add(entry)
    db.session.commit()

    response = client.get('/goto01', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == 'https://destino.example.com'


def test_redirect_nonexistent_short_url_returns_404(client):
    response = client.get('/no-existe-este-short-url')
    assert response.status_code == 404


def test_custom_404_page_content(client):
    response = client.get('/ruta-totalmente-inventada')
    assert response.status_code == 404
    assert b'404' in response.data
