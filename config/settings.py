"""
Django settings for config project.

Proyecto: Plataforma de hoteles y lanchas/tours en Santiago de Tolú (Sucre).
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only")
# DEBUG booleano desde env
DEBUG = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes", "on")

# ALLOWED_HOSTS configurable por env; auto-incluye los dominios de Railway.
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# Dominio de producción propio (siempre permitido, sin depender de la env var).
ALLOWED_HOSTS += ["viajesventasyturismotolu.com", "www.viajesventasyturismotolu.com"]

# Railway: dominio público generado (variable inyectada por la plataforma) y,
# como red de seguridad, cualquier subdominio *.railway.app / *.up.railway.app.
_railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)
ALLOWED_HOSTS += [".railway.app", ".up.railway.app"]

# Desarrollo local: con DEBUG=True permite localhost/127.0.0.1.
if DEBUG:
    ALLOWED_HOSTS += ["localhost", "127.0.0.1", "[::1]"]

# Detrás del proxy de Railway: respeta el esquema https reenviado por el proxy
# (necesario para CSRF, cookies seguras y request.is_secure()).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Application definition
# NOTA (Unfold): `unfold` y sus contribuciones deben ir ANTES de
# `django.contrib.admin` para que sobrescriban las plantillas del admin.
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Apps del proyecto
    'core',
    'servicios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise sirve los archivos estáticos también con DEBUG=False
    # (debe ir justo después de SecurityMiddleware).
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Expone la ConfiguracionSitio y las redes en todas las plantillas.
                'core.context_processors.sitio',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Por defecto SQLite (pruebas). Para producción basta con cambiar este bloque
# por la configuración de PostgreSQL (ver README); los modelos y vistas no cambian.
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Ejemplo de migración a PostgreSQL (descomentar y ajustar credenciales):
# import os
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'tolu_turismo'),
#         'USER': os.environ.get('DB_USER', 'tolu'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Orígenes de confianza para CSRF (sin barra final ni ruta: solo esquema://host).
CSRF_TRUSTED_ORIGINS = [
    "https://chase-nondrinkable-editorially.ngrok-free.dev",
    "https://viajesventasyturismotolu.com",
    "https://www.viajesventasyturismotolu.com",
    "https://*.railway.app",
    "https://*.up.railway.app",
]
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")

# Internationalization
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: compresión + nombres con hash para servir estáticos en producción.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------------------------------------------------------
# Configuración de django-unfold (panel de administración)
# Branding costero acorde al Golfo de Morrosquillo.
# -------------------------------------------------------------------
from django.templatetags.static import static  # noqa: E402
from django.utils.translation import gettext_lazy as _  # noqa: E402

UNFOLD = {
    "SITE_TITLE": "Tolú Turismo · Admin",
    "SITE_HEADER": "Tolú Turismo",
    "SITE_SUBHEADER": "Hoteles y lanchas en Santiago de Tolú",
    "SITE_SYMBOL": "sailing",  # ícono Material Symbols (lancha/vela)
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        # Paleta costera: turquesa del Golfo como color primario del panel.
        "primary": {
            "50": "236 252 252",
            "100": "207 246 246",
            "200": "162 236 237",
            "300": "108 220 223",
            "400": "52 196 201",
            "500": "21 160 166",
            "600": "16 129 137",
            "700": "18 103 110",
            "800": "22 83 90",
            "900": "21 69 76",
            "950": "8 42 48",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Contenido"),
                "separator": True,
                "items": [
                    {
                        "title": _("Servicios"),
                        "icon": "beach_access",
                        "link": "/admin/servicios/servicio/",
                    },
                    {
                        "title": _("Redes sociales"),
                        "icon": "share",
                        "link": "/admin/core/redsocial/",
                    },
                    {
                        "title": _("Configuración del sitio"),
                        "icon": "settings",
                        "link": "/admin/core/configuracionsitio/",
                    },
                ],
            },
        ],
    },
}
