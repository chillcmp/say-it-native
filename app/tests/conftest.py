from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_db_session_user_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    db.add.return_value = None
    db.commit.return_value = None
    return db


@pytest.fixture
def make_mock_db_session_user_exists():
    def _make(email: str):
        db = MagicMock()
        existing_user = MagicMock()
        existing_user.email = email
        db.query().filter().first.return_value = existing_user
        db.add.return_value = None
        db.commit.return_value = None
        return db
    return _make
