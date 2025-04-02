import pytest
from fastapi import HTTPException

from app.schemas.auth import LoginRequest
from app.services.auth_service import register_user, login_user


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
