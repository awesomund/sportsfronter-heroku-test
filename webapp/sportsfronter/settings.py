#############################################################
#         Django settings for sportsfronter project         #
#############################################################
#
# NOTE: This file contains production AND default settings.
#       To override a setting, create/use `settings_dev.py`.
#

import os.path

import dj_database_url

# Sportsfronter specific settings
ROOT_URL = "https://sportsfronter.iterate.no"
DOMAIN = "sportsfronter.iterate.no"
SSL_APPLE_DEV_CERTIFICATE_PATH = "/srv/sportsfronter.iterate.no/home/.ssl/ssl-cert-apple-dist.pem"
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# Django specific settings follows from here
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'corsheaders',
    'django_extensions',
    'push',
    'event',
    'auth',
    'management',
    'rest_framework.authtoken',
    'rest_framework',
    'south',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sportsfronter.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# Parse database configuration from $DATABASE_URL or use the default
DATABASES = {'default': dj_database_url.config(default='postgres://sf_admin:SportRocks!!!@localhost:5432/sportsfronter')}

## Email - production:
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'sportsfronter@sportsfronter.no'

SERVER_EMAIL = 'sportsfronter@sportsfronter.iterate.no'
ADMINS = ( ('Sportsfronter', 'sportsfronter-notify@iterate.no'), )
MANAGERS = ADMINS

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sportsfronter.wsgi.application'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    'localhost',
    '0.0.0.0',
    'sportsfronter.iterate.no',
    'sportsfronter-api.app.iterate.no',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'sportsfronter.iterate.no',
    'sportsfronter.app.iterate.no',
    '0.0.0.0:8000',
    '127.0.0.1:8000',
    'localhost:8000',
    'localhost',
)
CORS_ALLOW_HEADERS = (
    'X-Requested-With',
    'Content-Type',
    'Accept',
    'Origin',
    'Authorization',
    'X-csrftoken',
    'X-Mx-ReqToken',
    'DNT',
    'Keep-Alive',
    'User-Agent',
    'If-Modified-Since',
    'Cache-Control'
)

SITE_ID = 1
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET = 'utf-8'
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_AGE = 365 * 24 * 60 * 60 # One year

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Etc/Universal'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"

STATIC_ROOT = os.path.join(PROJECT_PATH, 'staticfiles')
# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin'
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%e=8o=ihk=-$psjw-&0__=%0agn5v2u!h!&p%)!pkja@kenoql'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#         },
#         'simple': {
#             'format': '%(levelname)s %(asctime)s %(message)s'
#         },
#     },
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         },
#         'console':{
#             'level': 'INFO',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         'logfile': {
#             'level':'DEBUG',
#             'class':'logging.handlers.RotatingFileHandler',
#             'filename': PROJECT_PATH + "/logfile",
#             'maxBytes': 50000,
#             'backupCount': 2,
#             'formatter': 'standard',
#         },
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         'sportsfronter': {
#             'handlers': ['mail_admins','console'],
#             'level': 'DEBUG',
#         }
#     }
# }
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': PROJECT_PATH + "/logfile",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console', 'logfile'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'sportsfronter': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}


try:
    from settings_dev import *
except ImportError: pass

STAGING = os.environ.get('STAGING', False)

if STAGING:
    try:
        from settings_staging import *
    except ImportError: pass
