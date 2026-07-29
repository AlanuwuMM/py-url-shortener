# Py URL Shortener — Proyecto de Reingeniería

> Proyecto original: [maateen/py-url-shortener](https://github.com/maateen/py-url-shortener).
> Este repositorio documenta el proceso de **refactorización, modernización,
> automatización y despliegue continuo** aplicado sobre ese sistema legado,
> como parte del Proyecto Final de Reingeniería.

## Índice

- [Fase 1 — Arquitectura previa vs. propuesta](#fase-1--ingeniería-reversa-y-refactorización)
- [Cómo correr el proyecto localmente](#cómo-correr-el-proyecto-localmente)
- Fase 2 — Docker *(en progreso)*
- Fase 3 — Pytest *(pendiente)*
- Fase 4 — Selenium E2E *(pendiente)*
- Fase 5 — GitHub Actions *(pendiente)*
- Fase 6 — Despliegue y monitoreo *(pendiente)*

---

## Fase 1 — Ingeniería Reversa y Refactorización

### Arquitectura previa (legada)

```
py-url-shortener/
├── app/
│   ├── __init__.py    # Instancia global de Flask y SQLAlchemy
│   ├── api.py         # Lógica del endpoint JSON
│   ├── form.py        # Formulario con Flask-WTF (API deprecada)
│   ├── models.py      # Modelo único Urls
│   ├── utils.py       # Lógica de negocio (con bugs, ver abajo)
│   ├── views.py       # Rutas HTML + registro de la ruta API
│   ├── static/
│   └── templates/
├── config.py           # Credenciales de MySQL y SECRET_KEY en texto plano
├── manage.py           # Script manual para crear tablas
└── run.py
```

**Problemas identificados:**

| # | Problema | Ubicación | Riesgo |
|---|----------|-----------|--------|
| 1 | `app` y `db` como variables globales del módulo, con imports tardíos (`from app import views` al final de `__init__.py`) para evitar import circular | `app/__init__.py` | Imposible tener múltiples instancias configuradas (bloquea testing) |
| 2 | Credenciales de base de datos y `SECRET_KEY` hardcodeadas en texto plano | `config.py` | Fuga de credenciales si el repo es público |
| 3 | `request.url_root` usado sin importar `request` de Flask (solo se importaba `Request` de `urllib.request`) | `app/utils.py` | `NameError` en tiempo de ejecución |
| 4 | Bloque `try/except/else` con `else` inalcanzable | `app/utils.py` | Código muerto, confusión de mantenimiento |
| 5 | Sin separación de responsabilidades (rutas HTML y API mezcladas), sin Blueprints | `app/views.py` | No escala, difícil de testear en aislamiento |
| 6 | `id = db.BigInteger` como PK, incompatible con autoincremento en SQLite | `app/models.py` | Rompe al testear con SQLite (detectado durante esta reingeniería) |
| 7 | Dependencias de 2015-2016 (`Flask==0.10.1`, etc.), con vulnerabilidades conocidas y sin soporte para Python 3.12 | `requirements.txt` | Riesgo de seguridad, imposible instalar en entornos modernos |
| 8 | `flask_wtf.Form` y `wtforms.fields.html5.URLField`, ambos eliminados en versiones actuales | `app/form.py` | Código no ejecutable con librerías actuales |

### Arquitectura propuesta (nueva)

```
py-url-shortener/
├── app/
│   ├── __init__.py            # Application Factory: create_app(config_name)
│   ├── extensions.py          # db = SQLAlchemy() sin vincular (evita import circular)
│   ├── forms.py                # FlaskForm moderno
│   ├── utils.py                # Lógica de negocio, bugs corregidos, usa `requests`
│   ├── blueprints/
│   │   ├── main/                # Rutas HTML (home, redirect, error 404)
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── api/                 # Rutas JSON versionadas (/api/v1.0/...)
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── url.py               # Modelo Urls segregado
│   ├── static/
│   └── templates/
├── config.py                    # Config por clases (Development/Testing/Production)
├── .env.example                 # Plantilla pública de variables de entorno
├── .env                          # Variables reales (NUNCA se commitea, ver .gitignore)
├── .gitignore
├── manage.py                     # Actualizado al patrón factory
├── requirements.txt              # Dependencias modernas y seguras
└── run.py                        # Punto de entrada, host 0.0.0.0 + PORT (listo para Docker)
```

**Decisiones de diseño clave:**

1. **Application Factory (`create_app`)**: permite crear instancias de la app con configuración distinta (`development`, `testing`, `production`) sin variables globales. Esto es lo que hace posible, más adelante, que Pytest use una base de datos SQLite en memoria aislada por test.
2. **Blueprints (`main`, `api`)**: separan completamente las rutas de interfaz web de las rutas de API versionada, cada una con su propio prefijo y responsabilidad.
3. **Configuración centralizada por entorno**: ninguna credencial vive en el código; todo se lee de variables de entorno (`os.environ`) vía `python-dotenv`.
4. **Corrección de bugs legados**: ver tabla arriba — todos corregidos y verificados con pruebas funcionales antes de continuar a la Fase 2.
5. **Dependencias actualizadas**: Flask 3.x, Flask-SQLAlchemy 3.x, Flask-WTF 1.x, compatibles con Python 3.12.

### Cómo correr el proyecto localmente

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # Ajustar valores si es necesario
python manage.py syncdb          # Crea las tablas (SQLite por defecto en desarrollo)
python run.py                    # Sirve en http://localhost:5000
```
