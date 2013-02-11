# Django settings for easycare project.
import os, sys
gettext = lambda s: s
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

#Settings 
LOGIN_REDIRECT_URL = "/records/pending/"

################### Production/Development settings ###########################
# This snippet loads configuration from either:
#   config/development.py or
#   config/production.py based on DJANGO_ENV environment variable
# 
# Ref: http://thomas.pelletier.im/2010/08/rails-like-configuration-style-for-django/
# 
# Set a default value for environements
default = 'development'
# Grab the current environement from the system environment variable named
 # DJANGO_ENV
current_env = os.getenv('DJANGO_ENV', default=None)
# Print an alert if no value is found: better for debug
if current_env == None:
    print "No DJANGO_ENV defined. Falling back to '%s'." % default
    current_env = default

CURRENT_ENV = current_env = current_env.lower()
if '.' in current_env:
    raise Exception('You configuration environement must not contain a dot.')
# Finally import the configuration
try:
    exec("from easycare.config.%s import *" % current_env) # This is the specific
    # configuration.
except ImportError:
    print "The module 'config.%s' was not found. Only the base configuration\
       has been imported." % current_env
###############################################################################

ADMINS = (
    # ('Chaiyawut Sookplang', 'chaiyawut.so@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_OPTIONS = { "charset": "utf8", "init_command": "SET storage_engine=InnoDB", }
DEFAULT_CHARSET='utf-8'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Bangkok'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'th'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-z+yxwszn)ah4dr2g)=$1j=j_2zj3508#jz!^y-!-laz$x75-e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'easycare.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'easycare.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'frontend',
)


EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'easycare.sit@gmail.com'
EMAIL_HOST_PASSWORD = 'wmp;ui;y<oN'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


