from settings import *

DEBUG = False

SITE_ROOT = ''

LOGIN_URL = SITE_ROOT + "/accounts/login/"

# Theme info
# LOCAL_STATICFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                '../../ODC-overlay/static'))
# LOCAL_TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                              '../../ODC-overlay/templates'))

# ReCatchpa stuff
RECAPTCHA_PUBLIC_KEY = '6LfU8t8SAAAAAJKrpalcrjlSA6zf9SIJaMBbz33s'
RECAPTCHA_PRIVATE_KEY = ''

# Twitter stuff
TWITTER_USER = None

# AWS Credentials for Warehouse stuff
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None

# Contacts
# mx_host = 'mycity.gov'
ADMINS = (
    ('Colin', 'copelco@caktusgroup.com'),
)
CONTACT_EMAILS = ['copelco@caktusgroup.com']
DEFAULT_FROM_EMAIL = 'OpenData Site <noreply@example.com>'
EMAIL_SUBJECT_PREFIX = '[OpenDataCatalog - MYCITY] '
SERVER_EMAIL = 'OpenData Team <info@example.com>'

MANAGERS = (
    ('Colin', 'copelco@caktusgroup.com'),
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

INSTALLED_APPS += (
    'gunicorn',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'insecure'
