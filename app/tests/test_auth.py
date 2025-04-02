from unittest.mock import patch

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas.auth import LoginRequest
from app.services.auth_service import register_user, login_user, get_current_user


def test_register_new_user(mock_db_session_user_not_found):
    email, password = "test@example.com", "abc12345"
    request = LoginRequest(email=email, password=password)

    response, status_code = register_user(request, mock_db_session_user_not_found)

    assert response["message"].startswith("User test@example.com registered")
    assert status_code == 201

    mock_db_session_user_not_found.add.assert_called_once()
    mock_db_session_user_not_found.commit.assert_called_once()


def test_register_existing_user(make_mock_db_session_user_exists):
    email, password = "test@example.com", "abc12345"
    request = LoginRequest(email=email, password=password)
    mock_db = make_mock_db_session_user_exists(email)

    response, status_code = register_user(request, mock_db)

    assert response["message"] == "User test@example.com already exists."
    assert status_code == 409

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_login_user_success(make_mock_db_session_user_exists, mock_pwd_context, mock_jwt_token):
    email, password = "test@example.com", "abc12345"
    mock_db = make_mock_db_session_user_exists(email)
    mock_pwd_context.verify.return_value = True

    request = LoginRequest(email=email, password=password)
    result, status = login_user(request, mock_db)

    assert status == 200
    assert result["access_token"] == "mocked.jwt.token"
    assert result["token_type"] == "bearer"

    mock_pwd_context.verify.assert_called_once()


def test_login_user_invalid_email(mock_db_session_user_not_found, mock_pwd_context, mock_jwt_token):
    email, password = "test@example.com", "abc12345"
    mock_pwd_context.verify.return_value = True

    request = LoginRequest(email=email, password=password)
    with pytest.raises(HTTPException) as exc_info:
        login_user(request, mock_db_session_user_not_found)

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value.detail)

    mock_pwd_context.verify.assert_not_called()


def test_login_user_invalid_password(make_mock_db_session_user_exists, mock_pwd_context, mock_jwt_token):
    email, password = "test@example.com", "abc12345"
    mock_db = make_mock_db_session_user_exists(email)
    mock_pwd_context.verify.return_value = False

    request = LoginRequest(email=email, password=password)
    with pytest.raises(HTTPException) as exc_info:
        login_user(request, mock_db)

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value.detail)

    mock_pwd_context.verify.assert_called_once()


def test_get_current_user_success(make_mock_db_session_user_exists, make_mock_jwt_decode):
    email, user_id = "test@example.com", 1
    mock_jwt_decode = make_mock_jwt_decode(str(user_id))
    mock_db = make_mock_db_session_user_exists(email=email, user_id=user_id)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-token")
    user = get_current_user(db=mock_db, authorization=credentials)

    assert user.id == user_id
    assert user.email == email

    mock_jwt_decode.assert_called_once()


def test_get_current_user_invalid_id(make_mock_db_session_user_exists, make_mock_jwt_decode):
    email, user_id = "test@example.com", None
    mock_jwt_decode = make_mock_jwt_decode(user_id)
    mock_db = make_mock_db_session_user_exists(email=email, user_id=user_id)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-token")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, authorization=credentials)

    assert exc_info.value.status_code == 401
    assert "Invalid token payload" in str(exc_info.value.detail)

    mock_jwt_decode.assert_called_once()


def test_get_current_user_not_found(mock_db_session_user_not_found, make_mock_jwt_decode):
    email, user_id = "test@example.com", 1
    mock_jwt_decode = make_mock_jwt_decode(user_id)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-token")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db_session_user_not_found, authorization=credentials)

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)

    mock_jwt_decode.assert_called_once()


@patch("app.services.auth_service.jwt.decode")
def test_get_current_user_jwt_error(mock_jwt_decode, make_mock_db_session_user_exists):
    email, user_id = "test@example.com", 1
    mock_db = make_mock_db_session_user_exists(email=email, user_id=user_id)
    mock_jwt_decode.side_effect = jwt.PyJWTError("Invalid token")

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-token")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, authorization=credentials)

    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in str(exc_info.value.detail)

    mock_jwt_decode.assert_called_once()
