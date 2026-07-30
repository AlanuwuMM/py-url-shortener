#!/bin/sh
set -e

echo "Verificando/creando tablas de la base de datos..."
python manage.py init

echo "Iniciando servidor Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 run:app