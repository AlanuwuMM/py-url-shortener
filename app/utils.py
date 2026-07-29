"""
Funciones de negocio: generación de strings aleatorios, validación de
URLs y generación/consulta de URLs cortas.

Bugs corregidos respecto a la versión legada:
1. `short_url_generator` usaba `request.url_root` sin haber importado
   `request` de Flask (solo se importaba `Request` de `urllib.request`,
   una clase totalmente distinta). Esto provocaba un NameError en
   tiempo de ejecución. Ahora se importa correctamente
   `from flask import request`.
2. `url_checker` tenía un bloque `try/except HTTPError/else` donde el
   `else` era inalcanzable (el `return` dentro del `try` ya terminaba
   la función antes de llegar ahí). Se reescribe con `requests` y un
   manejo de excepciones más claro y completo (timeouts, errores de
   conexión, etc.), no solo HTTPError.
3. Se reemplaza `urllib.request` (bajo nivel, sin timeout por defecto)
   por la librería `requests` (estándar de facto en el ecosistema
   Python moderno), evitando que una URL lenta/caída cuelgue la app.
"""
import random
import string

from flask import request
import requests

from app.extensions import db
from app.models import Urls

DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (compatible; PyURLShortener/2.0; +https://github.com)'
)
REQUEST_TIMEOUT_SECONDS = 5


def random_string_generator(size):
    """Genera una cadena aleatoria alfanumérica de longitud `size`."""
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(size)
    )


def url_checker(long_url):
    """
    Verifica si `long_url` responde con un código HTTP < 400.
    Devuelve True si la URL está viva, False en cualquier otro caso
    (código de error, timeout, host inexistente, etc.).
    """
    headers = {'User-Agent': DEFAULT_USER_AGENT}
    try:
        response = requests.head(
            long_url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True,
        )
        return response.status_code < 400
    except requests.exceptions.RequestException:
        return False


def short_url_generator(long_url):
    """
    Devuelve una URL corta para `long_url`. Si ya existe en la base de
    datos, retorna la existente; si no, genera una nueva de forma
    incremental (6 a 10 caracteres) hasta encontrar una libre.
    """
    existing = Urls.query.filter_by(long_url=long_url).first()
    if existing is not None:
        return request.url_root + existing.short_url

    for size in range(6, 11):
        candidate = random_string_generator(size)
        collision = Urls.query.filter_by(short_url=candidate).first()
        if collision is None:
            new_entry = Urls(short_url=candidate, long_url=long_url)
            db.session.add(new_entry)
            db.session.commit()
            return request.url_root + candidate

    # Caso extremo: no debería ocurrir en la práctica (10 caracteres
    # alfanuméricos dan >60 mil millones de combinaciones).
    raise RuntimeError('No fue posible generar una URL corta única.')


def number_of_generated_short_url():
    """Cuenta cuántas URLs cortas existen en la base de datos."""
    return Urls.query.count()
