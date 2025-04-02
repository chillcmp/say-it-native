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
    def _make(email: str = "", user_id: int = 1):
        db = MagicMock()
        existing_user = MagicMock()
        existing_user.email = email
        existing_user.id = user_id
        db.query().filter().first.return_value = existing_user
        db.add.return_value = None
        db.commit.return_value = None
        return db
    return _make


@pytest.fixture
def mock_pwd_context(monkeypatch):
    pwd = MagicMock()
    monkeypatch.setattr("app.services.auth_service.pwd_context", pwd)
    return pwd


@pytest.fixture
def mock_jwt_token(monkeypatch):
    jwt_token = MagicMock()
    jwt_token.return_value = "mocked.jwt.token"
    monkeypatch.setattr("app.services.auth_service._create_jwt_token", jwt_token)
    return jwt_token


@pytest.fixture
def make_mock_jwt_decode(monkeypatch):
    def _make(user_id: str):
        mock_jwt_decode = MagicMock()
        mock_jwt_decode.return_value = {"sub": user_id}
        monkeypatch.setattr("app.services.auth_service.jwt.decode", mock_jwt_decode)
        return mock_jwt_decode
    return _make
