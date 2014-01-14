# -*- coding: utf-8 -*-
import os

from setuptools import find_packages
from setuptools import setup


classifiers = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='django-notifications',
    version='0.0.1',
    description='Notifications app for django',
    long_description=README,
    author='Troy Grosfield',
    maintainer='Troy Grosfield',
    url='https://github.com/InfoAgeTech/django-notifications',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'https://github.com/InfoAgeTech/django-generic/tarball/master',
        'https://github.com/InfoAgeTech/django-core/tarball/master',
        'https://github.com/InfoAgeTech/python-tools/tarball/master'
    ],
    setup_requires=[
        'django >= 1.5.5',
    ],
    test_suite='nose.collector',
    tests_require=[
        'django_nose',
        'https://github.com/InfoAgeTech/django-testing/tarball/master'
    ],
    classifiers=classifiers
)
