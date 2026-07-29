"""
Modelo de datos para las URLs acortadas.

Cambio respecto a la versión legada (app/models.py):
- Se mueve a su propio paquete `app/models/` para que, si el proyecto
  crece, cada entidad tenga su propio archivo (ej. models/user.py).
- Importa `db` desde app.extensions en lugar de `from app import db`,
  rompiendo la dependencia circular con app/__init__.py.
- Se agrega un `created_at` (buena práctica de auditoría) y un
  `__repr__` para facilitar debugging/tests.
"""
from datetime import datetime, timezone

from app.extensions import db


class Urls(db.Model):
    __tablename__ = 'urls'

    # NOTA técnica: se usa Integer (no BigInteger) a propósito. SQLAlchemy
    # solo mapea automáticamente el autoincremento de la PK sobre el
    # "rowid" de SQLite cuando la columna es exactamente Integer; con
    # BigInteger (como estaba en el legado) el INSERT falla en SQLite con
    # "NOT NULL constraint failed" porque no se genera el ID. En MySQL
    # (producción) Integer sigue soportando autoincrement sin problema.
    # Esto era invisible en el código legado porque nunca se probó contra
    # una base de datos real en CI.
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(100), unique=True, nullable=False, index=True)
    long_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, short_url, long_url):
        self.short_url = short_url
        self.long_url = long_url

    def __repr__(self):
        return f'<Urls id={self.id} short_url={self.short_url!r}>'
