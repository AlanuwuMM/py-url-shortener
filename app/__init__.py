"""
Application Factory.

Cambio principal respecto al legado:
- Antes, `app = Flask(__name__)` y `db = SQLAlchemy(app)` eran variables
  globales creadas apenas se importaba el paquete `app`. Esto hacía
  IMPOSIBLE tener más de una instancia configurada distinta (por
  ejemplo, una para tests con SQLite en memoria y otra para producción
  con MySQL) sin recurrir a trucos.
- Ahora `create_app(config_name)` construye y devuelve una instancia
  nueva cada vez que se llama, recibiendo qué configuración usar
  ('development', 'testing', 'production'). Esto es indispensable para
  la Fase 3 (Pytest), donde los tests necesitan su propia app aislada
  con una base de datos de prueba.
- Los Blueprints se registran aquí explícitamente, en vez de los
  imports tardíos "from app import views" que existían para evitar
  imports circulares.
"""
import os

from flask import Flask

from app.extensions import db
from config import config_by_name


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)

    from app.blueprints.main import main_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
