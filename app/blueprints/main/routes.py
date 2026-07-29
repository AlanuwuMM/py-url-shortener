"""
Rutas HTML (antes en app/views.py, mezcladas con la ruta de API).

Cambios respecto al legado:
- Separadas en su propio Blueprint 'main', sin ninguna lógica de API.
- El endpoint se llama ahora 'main.home' (Flask antepone el nombre del
  blueprint), por lo que el template index.html se actualizó de
  `url_for('home')` a `url_for('main.home')`.
"""
from flask import abort, flash, redirect, render_template, request

from app.blueprints.main import main_bp
from app.forms import GetLinkForm
from app.models import Urls
from app.utils import number_of_generated_short_url, short_url_generator, url_checker


@main_bp.route('/', methods=['GET', 'POST'])
def home():
    number = number_of_generated_short_url()
    form = GetLinkForm(request.form)

    if request.method == 'POST':
        if form.validate():
            long_url = form.long_url.data
            if url_checker(long_url):
                short_url = short_url_generator(long_url)
                return render_template(
                    'index.html', form=form, short_url=short_url, number=number
                )
            flash('The URL seems to be dead at this moment.')
            return render_template('index.html', form=form, number=number)

        flash('Please, paste a valid link to shorten it.')
        return render_template('index.html', form=form, number=number)

    return render_template('index.html', form=form, number=number)


@main_bp.route('/<string:short_url>')
def redirect_to_main_url(short_url):
    entry = Urls.query.filter_by(short_url=short_url).first()
    if entry is None:
        abort(404)
    return redirect(entry.long_url)


@main_bp.app_errorhandler(404)
def page_not_found(error):
    number = number_of_generated_short_url()
    return render_template('404.html', number=number), 404
