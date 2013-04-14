import os

from settings import *

SITE_ROOT = 'http://opendatacatalog.mycity.gov:8000'

LOGIN_URL = SITE_ROOT + "/accounts/login/"

# Theme info
# LOCAL_STATICFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                '../../ODC-overlay/static'))
# LOCAL_TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                              '../../ODC-overlay/templates'))

# ReCatchpa stuff
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

# Twitter stuff
TWITTER_USER = None

# AWS Credentials for Warehouse stuff
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None

# Contacts
mx_host = 'mycity.gov'
ADMINS = (
     ('OpenData Admins', 'admin@%s' % (mx_host,)),
)
CONTACT_EMAILS = ['admin@%s' % (mx_host,),]
DEFAULT_FROM_EMAIL = 'OpenData Site <noreply@%s>'
EMAIL_SUBJECT_PREFIX = '[OpenDataCatalog - MYCITY] '
SERVER_EMAIL = 'OpenData Team <info@%s>' % (mx_host,)

MANAGERS = (
     ('OpenData Team', 'info@%s' % (mx_host,)),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'opendata',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'insecure'

