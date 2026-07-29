"""
Fixtures compartidas para toda la suite de pruebas.

Se usa la configuración 'testing' (SQLite en memoria, CSRF deshabilitado)
gracias a que app/__init__.py implementa el patrón Application Factory
introducido en la Fase 1. Sin ese refactor, no sería posible aislar cada
test con su propia base de datos limpia.
"""
import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    application = create_app('testing')
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db
