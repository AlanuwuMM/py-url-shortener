"""
Endpoints JSON (antes mezclados dentro de app/views.py + app/api.py).

Cambios respecto al legado:
- Prefijo de URL '/api' centralizado en el Blueprint (url_prefix='/api'),
  ya no se arma manualmente en cada ruta.
- La ruta ahora es POST /api/<version>/shorten en vez de POST
  /api/<version>/ para que el propósito del endpoint sea explícito.
- Se valida la versión con un mapeo, y se responde 400 (no 403, que es
  semánticamente incorrecto para "versión no soportada") con un JSON de
  error descriptivo si `long_url` falta en el body o la versión no
  existe.
- NOTA: el endpoint /api/health (Fase 6, monitoreo) se añadirá aquí
  mismo cuando lleguemos a esa fase, ya que pertenece naturalmente al
  blueprint de la API.
"""
from flask import jsonify, request

from app.blueprints.api import api_bp
from app.utils import short_url_generator, url_checker

SUPPORTED_VERSIONS = {'v1.0'}


def _shorten_v1(long_url):
    if url_checker(long_url):
        short_url = short_url_generator(long_url)
        return {
            'state': 'ok',
            'long_url': long_url,
            'short_url': short_url,
            'message': '',
        }
    return {
        'state': 'error',
        'long_url': long_url,
        'short_url': '',
        'message': 'The URL seems to be dead at this moment.',
    }


@api_bp.route('/health')
def health():
    """
    Endpoint de diagnóstico para monitoreo (Fase 6).
    No depende de la base de datos a propósito: un healthcheck debe
    responder rápido y no fallar solo porque la BD esté momentáneamente
    ocupada; el objetivo es confirmar que el proceso Flask está vivo.
    """
    return jsonify({'status': 'ok'}), 200


@api_bp.route('/<string:version>/', methods=['POST'])
def shorten(version):
    if version not in SUPPORTED_VERSIONS:
        return jsonify({'state': 'error', 'message': f'API version {version} not supported.'}), 400

    payload = request.get_json(silent=True) or {}
    long_url = payload.get('long_url')
    if not long_url:
        return jsonify({'state': 'error', 'message': "'long_url' field is required."}), 400

    result = _shorten_v1(long_url)
    return jsonify(result)
