"""Test configuration."""

from os.path import abspath, dirname, join


basedir = abspath(dirname(__file__))


"""Settings module for test app."""
ENV = 'development'
TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SECRET_KEY = 'not-so-secret-in-tests'
DEBUG_TB_ENABLED = False
CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'
WTF_CSRF_ENABLED = False  # Allows form testing
MEDIA_FOLDER = join(basedir, '..', 'media')
