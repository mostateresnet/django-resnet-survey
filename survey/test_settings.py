TEST_RUNNER = 'discover_runner.DiscoverRunner'
ROOT_URLCONF = 'survey.urls'
STATIC_URL = '/static/'
USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'survey.sqlite3',                # Or path to database file if using sqlite3.
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'survey',
    'south',
)
