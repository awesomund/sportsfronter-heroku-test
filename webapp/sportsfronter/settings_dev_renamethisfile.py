# Override default settings for local development.
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Sportsfronter', 'sportsfronter@gmail.com'),
)

SERVER_EMAIL = 'sportsfronter@gmail.com'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sportsfronter.wsgi.application'

if 'test' in sys.argv:
    DATABASES = { 'default': {'ENGINE': 'django.db.backends.sqlite3'} }
else:
    import dj_database_url
    db_url = 'postgres://sportsfronter:sportsfronter-django@localhost:5432/sportsfronter'
    DATABASES = { 'default': dj_database_url.config(default=db_url) }

## Email - dev:
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'sportsfronter@gmail.com'
EMAIL_HOST_PASSWORD = 'iterate123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
ROOT_URL = 'http://localhost:5000'
PASSWORD_RESET_URL = 'http://localhost:5000/admin/password_reset/'
