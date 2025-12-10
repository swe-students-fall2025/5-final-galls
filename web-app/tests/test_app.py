import pytest
from unittest.mock import patch
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, bcrypt, User


@pytest.fixture
def _test_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("app.db")
def test_login_success(mock_db, _test_client):
    """Test login with correct username and password."""
    # Create a valid ObjectId for the mock user
    mock_user_id = ObjectId()
    hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")

    # Mock the database find_one to return this user
    mock_db.users.find_one.return_value = {
        "_id": mock_user_id,
        "username": "testuser",
        "email": "test@example.com",
        "password": hashed_pw,
    }

    # Post login form
    response = _test_client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    # After successful login, the home page should contain the username
    assert b"testuser" in response.data


@patch("app.db")
def test_login_invalid_password(mock_db, _test_client):
    """Test login with correct username but wrong password."""
    mock_user_id = ObjectId()
    hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")

    mock_db.users.find_one.return_value = {
        "_id": mock_user_id,
        "username": "testuser",
        "email": "test@example.com",
        "password": hashed_pw,
    }

    response = _test_client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 200
    assert b"Invalid username/password" in response.data


@patch("app.db")
def test_login_user_not_found(mock_db, _test_client):
    """Test login with a username that does not exist."""
    mock_db.users.find_one.return_value = None

    response = _test_client.post(
        "/login",
        data={"username": "nonexistent", "password": "password123"},
    )

    assert response.status_code == 200
    assert b"User not found" in response.data

@patch("app.db")
def test_register_success(mock_db, _test_client):
    """Test successful user registration."""
    mock_db.users.find_one.return_value = None  # No existing user

    # Simulate insert_one returning an ObjectId
    mock_inserted_id = ObjectId()
    mock_db.users.insert_one.return_value.inserted_id = mock_inserted_id

    # POST to register without following redirects
    response = _test_client.post(
        "/register",
        data={"username": "newuser", "email": "new@example.com", "password": "password123"},
        follow_redirects=False,  # check redirect directly
    )

    # Registration should redirect to home
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")  # redirected to home





@patch("app.db")
def test_register_existing_email(mock_db, _test_client):
    """Test registration with an email that already exists."""
    mock_db.users.find_one.return_value = {"_id": ObjectId(), "email": "existing@example.com"}

    response = _test_client.post(
        "/register",
        data={"username": "newuser", "email": "existing@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert b"Account with this email already exists." in response.data


def test_logout_redirect(_test_client):
    """Test that logout redirects to login page."""
    response = _test_client.get("/logout", follow_redirects=True)

    # Should redirect to login page
    assert response.status_code == 200
    assert b"Login" in response.data

