"""
Configuración centralizada por entorno.

Cambio respecto al legado:
- El config.py original tenía la URI de MySQL y el SECRET_KEY escritos
  en texto plano dentro del propio repositorio (riesgo de seguridad
  grave si el repo es público, y viola el principio de "config
  externalizada" de las 12-factor apps).
- Ahora TODOS los valores sensibles se leen de variables de entorno
  vía os.environ, con python-dotenv cargando un archivo .env local
  (que NO se sube al repo, ver .gitignore) durante desarrollo. En
  producción (Fase 6), estas variables se configuran directamente en
  la plataforma de despliegue (Render/Railway/etc.), nunca en el código.
- Se separan 3 configuraciones (Development, Testing, Production) para
  que Pytest (Fase 3) pueda usar SQLite en memoria sin tocar la base de
  datos real, y para que producción tenga DEBUG=False obligatoriamente.
"""
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'dev.db')
    )
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def validate(cls):
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError('DATABASE_URL no está configurada en el entorno de producción.')
        if os.environ.get('SECRET_KEY') in (None, 'dev-key-change-me'):
            raise RuntimeError('SECRET_KEY debe configurarse explícitamente en producción.')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
