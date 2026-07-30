"""
Script de administración de la base de datos.

Cambio respecto al legado: antes importaba la `app`/`db` globales
directamente. Ahora crea explícitamente una instancia con create_app()
antes de operar sobre la base de datos, ya que db.create_all() necesita
un contexto de aplicación activo.

Uso:
    python manage.py syncdb
"""
import sys

from app import create_app
from app.extensions import db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if 'syncdb' in sys.argv:
            db.drop_all()
            db.create_all()
            print('Base de datos sincronizada (reiniciada).')
        elif 'init' in sys.argv:
            db.create_all()
            print('Base de datos inicializada (tablas verificadas).')
        else:
            print('Uso: python manage.py syncdb | python manage.py init')
