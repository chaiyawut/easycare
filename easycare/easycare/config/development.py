import os
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DATABASE_PATH, 'easycare.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import djcelery
djcelery.setup_loader()

INSTALLED_APPS += (
	'djcelery',
    'djcelery_email',
)

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

