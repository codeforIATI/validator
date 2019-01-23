"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_webpack import Webpack
from flask_wtf.csrf import CSRFProtect


csrf_protect = CSRFProtect()  # pylint: disable=invalid-name
db = SQLAlchemy()  # pylint: disable=invalid-name
migrate = Migrate()  # pylint: disable=invalid-name
cache = Cache()  # pylint: disable=invalid-name
debug_toolbar = DebugToolbarExtension()  # pylint: disable=invalid-name
webpack = Webpack()  # pylint: disable=invalid-name
