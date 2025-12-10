"""Unit tests for the Flask app routes."""

import os
import sys
import json
from unittest.mock import patch, MagicMock
from app import app, bcrypt

# from requests.exceptions import RequestException

import pytest  # pylint: disable=import-error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # pylint: disable=C0413,E0401

def test_mock():
    assert True


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client



@patch("app.db.users.find_one")
@patch("app.db.users.insert_one")
def test_register_success(mock_insert, mock_find, client):
    # email doesnt exist
    mock_find.return_value = None

    response = client.post("/register", data={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }, follow_redirects=True)

    # Should call insert_one once
    assert mock_insert.called

    # Should redirect to home page
    assert response.status_code == 200
    assert b"My Pantry" in response.data or b"Home" in response.data

@patch("app.db.users.find_one")
def test_register_existing_email(mock_find, client):
    # Simulate email already exists
    mock_find.return_value = {"email": "test@example.com"}

    response = client.post("/register", data={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })

    assert b"Account with this email already exists." in response.data
    assert response.status_code == 200



@patch("app.db.users.find_one")
def test_login_success(mock_find, client):
    hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")
    mock_find.return_value = {"_id": "12345", "username": "testuser", "email": "test@example.com", "password": hashed_pw}

    response = client.post("/login", data={
        "username": "testuser",
        "password": "password123"
    }, follow_redirects=True)

    # Should redirect to home page
    assert response.status_code == 200
    assert b"My Pantry" in response.data or b"Home" in response.data

@patch("app.db.users.find_one")
def test_login_user_not_found(mock_find, client):
    mock_find.return_value = None

    response = client.post("/login", data={
        "username": "nonexistent",
        "password": "password123"
    })

    assert b"User not found" in response.data
    assert response.status_code == 200

@patch("app.db.users.find_one")
def test_login_invalid_password(mock_find, client):
    hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")
    mock_find.return_value = {"_id": "12345", "username": "testuser", "email": "test@example.com", "password": hashed_pw}

    response = client.post("/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert b"Invalid username/password" in response.data
    assert response.status_code == 200
