from unittest.mock import MagicMock, patch

import requests

from app.models import Urls
from app.utils import (
    number_of_generated_short_url,
    random_string_generator,
    short_url_generator,
    url_checker,
)


def test_random_string_generator_length():
    result = random_string_generator(8)
    assert len(result) == 8
    assert result.isalnum()


def test_random_string_generator_is_random():
    """No debería generar siempre la misma cadena (con probabilidad despreciable de colisión)."""
    results = {random_string_generator(10) for _ in range(20)}
    assert len(results) == 20


@patch('app.utils.requests.head')
def test_url_checker_alive(mock_head):
    mock_head.return_value = MagicMock(status_code=200)
    assert url_checker('https://example.com') is True


@patch('app.utils.requests.head')
def test_url_checker_dead_status_code(mock_head):
    mock_head.return_value = MagicMock(status_code=404)
    assert url_checker('https://example.com/not-found') is False


@patch('app.utils.requests.head')
def test_url_checker_connection_error(mock_head):
    mock_head.side_effect = requests.exceptions.ConnectionError()
    assert url_checker('https://dominio-que-no-existe.invalid') is False


@patch('app.utils.requests.head')
def test_url_checker_timeout(mock_head):
    mock_head.side_effect = requests.exceptions.Timeout()
    assert url_checker('https://example.com/slow') is False


def test_short_url_generator_creates_new(app, db):
    with app.test_request_context('/'):
        short = short_url_generator('https://newsite.example.com')
        assert short.startswith('http://')
        assert Urls.query.filter_by(long_url='https://newsite.example.com').count() == 1


def test_short_url_generator_reuses_existing(app, db):
    with app.test_request_context('/'):
        first = short_url_generator('https://repeated.example.com')
        second = short_url_generator('https://repeated.example.com')
        assert first == second
        assert Urls.query.filter_by(long_url='https://repeated.example.com').count() == 1


def test_number_of_generated_short_url(app, db):
    with app.test_request_context('/'):
        assert number_of_generated_short_url() == 0
        short_url_generator('https://one.example.com')
        short_url_generator('https://two.example.com')
        assert number_of_generated_short_url() == 2
