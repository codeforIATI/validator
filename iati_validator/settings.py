"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from os.path import abspath, dirname, join

from environs import Env


basedir = abspath(dirname(__file__))

env = Env()
env.read_env()

ENV = env.str('FLASK_ENV', default='production')
DEBUG = ENV == 'development'
SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URL', default='sqlite:////' +
                                  join(basedir, 'db.sqlite3'))
SECRET_KEY = env.str('SECRET_KEY')
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'
MEDIA_FOLDER = join(basedir, '..', 'media')
