"""
Centraliza las extensiones de Flask (SQLAlchemy, etc).

Se instancian aquí SIN vincularlas todavía a una app concreta.
Esto permite usar el patrón "Application Factory": la vinculación real
ocurre después, dentro de create_app(), llamando a db.init_app(app).

Ventaja sobre la versión legada: elimina el import circular que existía
entre app/__init__.py <-> app/models.py <-> app/api.py, sin necesidad de
los imports tardíos ("from app import api" al final del archivo) que
tenía el código original.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
