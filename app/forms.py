"""
Formularios WTForms.

Cambios respecto al legado (app/form.py):
- `flask_wtf.Form` -> `flask_wtf.FlaskForm` (Form fue eliminado en
  Flask-WTF >= 0.13).
- `wtforms.fields.html5.URLField` -> `wtforms.fields.URLField`
  (el submódulo `html5` fue eliminado en WTForms >= 3.0; el campo se
  unificó dentro de `wtforms.fields`).
- Se agrega DataRequired para no depender solo del validador `url()`
  y dar un mensaje de error más claro en campos vacíos.
"""
from flask_wtf import FlaskForm
from wtforms.fields import URLField
from wtforms.validators import DataRequired, URL


class GetLinkForm(FlaskForm):
    long_url = URLField(
        'URL',
        validators=[
            DataRequired(message='Por favor, ingresa una URL.'),
            URL(message='Por favor, ingresa una URL válida.'),
        ],
    )
