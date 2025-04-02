from app.schemas.auth import LoginRequest
from app.services.auth_service import register_user


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
