from __future__ import unicode_literals

import os


DEBUG = False

ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'en-us'
ROOT_URLCONF = 'urls'
SECRET_KEY = '12345abcd'
SITE_ID = 1
SITE_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
TIME_ZONE = 'UTC'
USE_I18N = True

ACTIVITIES_BASE_TEMPLATE = 'base_activities.html'

INSTALLED_APPS = (
    'test_without_migrations',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'activities',
    'django_core',
    'test_models'  # adding as an installed app so testing models get picked up.
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'activities.context_processors.template_name',
    'django.contrib.auth.context_processors.auth',
)

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'activities/templates'),
)

here = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': here('test_db.db')
    }
}
