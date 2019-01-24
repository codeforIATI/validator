"""Defines fixtures available to all tests."""

import pytest

from iati_validator.app import create_app
from iati_validator.extensions import db as _db


@pytest.fixture
def app():
    """An application for the tests."""
    return create_app('tests.settings')


@pytest.fixture
def db(app):  # pylint: disable=invalid-name,redefined-outer-name
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()
