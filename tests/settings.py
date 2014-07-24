# -*- coding: utf-8 -*-
import os

NOTIFICATION_MODEL_MIXIN = 'test_models.AbstractNotificationMixin'
NOTIFICATION_MANAGER = 'test_models.managers.NotificationManager'
NOTIFICATIONS_BASE_TEMPLATE = 'base_notifications.html'

# Do not run in DEBUG in production!!!
DEBUG = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'bootstrapform',
    'django_notifications',
    'django_generics',
    'django_core',
    'django_nose',
    'test_models'  # adding as an installed app so testing models get picked up.
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django_notifications.context_processors.template_name',
    'django.contrib.auth.context_processors.auth',
)

SITE_ROOT = SITE_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates')
)

ROOT_URLCONF = 'urls'

# Added in django 1.5 secret key is required.  This is a random generated string
SECRET_KEY = '12345abcd'

# Added in django 1.4.4. See: https://docs.djangoproject.com/en/1.4/releases/1.4.4/#host-header-poisoning
ALLOWED_HOSTS = ['*']

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

here = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': here('test_db.db')
    }
}
