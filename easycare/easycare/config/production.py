DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'easycare',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'wmp;ui;y<oN',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = False
TEMPLATE_DEBUG = DEBUG

import djcelery
djcelery.setup_loader()

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

#CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
#CELERY_ALWAYS_EAGER = True
#BROKER_BACKEND = 'memory'