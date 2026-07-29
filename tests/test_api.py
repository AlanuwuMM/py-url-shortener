from unittest.mock import patch


def test_api_health_returns_ok(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


@patch('app.blueprints.api.routes.url_checker', return_value=True)
def test_api_shorten_valid_url(mock_checker, client):
    response = client.post('/api/v1.0/', json={'long_url': 'https://valid.example.com'})
    body = response.get_json()
    assert response.status_code == 200
    assert body['state'] == 'ok'
    assert body['long_url'] == 'https://valid.example.com'
    assert body['short_url'] != ''


@patch('app.blueprints.api.routes.url_checker', return_value=False)
def test_api_shorten_dead_url(mock_checker, client):
    response = client.post('/api/v1.0/', json={'long_url': 'https://dead.example.com'})
    body = response.get_json()
    assert response.status_code == 200
    assert body['state'] == 'error'
    assert body['short_url'] == ''


def test_api_shorten_missing_long_url_field(client):
    response = client.post('/api/v1.0/', json={})
    assert response.status_code == 400
    assert response.get_json()['state'] == 'error'


def test_api_shorten_unsupported_version(client):
    response = client.post('/api/v9.9/', json={'long_url': 'https://x.com'})
    assert response.status_code == 400
    assert 'not supported' in response.get_json()['message']


def test_api_shorten_requires_post_method(client):
    response = client.get('/api/v1.0/')
    assert response.status_code == 405
