import pytest
from unittest.mock import patch
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, bcrypt, User
import requests

@pytest.fixture
def _test_client():
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = True
    with app.test_client() as client:
        yield client
        
@pytest.fixture
def test_user(monkeypatch):
    """Test user so I can use current_user.id in tests w/o logging in."""
    class testUser:
        def __init__(self, id):
            self.id = str(id)
            self.is_authenticated = True

    user = testUser(ObjectId())
    monkeypatch.setattr("app.current_user", user)
    return user

@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock post request to mock calling the ML API"""
    def _mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return [{"name": "Test Recipe"}]
            def raise_for_status(self):
                pass
        return MockResponse()
    
    monkeypatch.setattr(requests, "post", _mock_post)
    return _mock_post


@patch("app.recommendations")
@patch("app.db")
def test_login_success(mock_db, mock_recommendations, _test_client):
    mock_user_id = ObjectId()
    hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")

    mock_db.users.find_one.return_value = {
        "_id": mock_user_id,
        "username": "testuser",
        "email": "test@example.com",
        "password": hashed_pw,
    }

    # Mock recommendations so home() doesn't hit MongoDB
    mock_recommendations.find_one.return_value = None
    mock_db.ingredients.find.return_value = []

    response = _test_client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200




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


@patch("app.db")
def test_my_pantry_shows_user_ingredients(mock_db, _test_client, test_user):
    """my_pantry should show ingredients on the page."""
    mock_db.ingredients.find.return_value = [{"_id": ObjectId(), "user_id": ObjectId(), "name": "chicken", "quantity": "2", "notes": "",}]
    resp = _test_client.get("/my-pantry")

    assert resp.status_code == 200
    assert b"chicken" in resp.data
    assert b"My Pantry" in resp.data


@patch("app.db")
def test_add_ingredient_inserts_and_redirects(mock_db, _test_client, test_user):
    """POST /my-pantry/add should add a new ingredient."""
    resp = _test_client.post("/my-pantry/add", data={"name": "lettuce", "quantity": "3", "notes": ""}, follow_redirects=False,)

    assert resp.status_code == 302
    assert "/my-pantry" in resp.headers["Location"]

    mock_db.ingredients.insert_one.assert_called_once()
    inserted = mock_db.ingredients.insert_one.call_args[0][0]
    assert inserted["name"] == "lettuce"
    assert inserted["quantity"] == "3"
    assert inserted["notes"] == ""


@patch("app.db")
def test_edit_ingredient_get_renders_form(mock_db, _test_client, test_user):
    """GET /my-pantry/<id>/edit should show the edit form with previous added data."""
    ingredient_id = ObjectId()
    mock_db.ingredients.find_one.return_value = {"_id": ingredient_id, "user_id": ObjectId(), "name": "olive oil", "quantity": "1", "notes": "",}
    resp = _test_client.get(f"/my-pantry/{ingredient_id}/edit")

    assert resp.status_code == 200
    assert b"olive oil" in resp.data
    assert b"1" in resp.data 


@patch("app.db")
def test_edit_ingredient_post_updates_and_redirects(mock_db, _test_client,test_user):
    """POST /my-pantry/<id>/edit should update ingredient and redirect to pantry."""
    ingredient_id = ObjectId()
    mock_db.ingredients.find_one.return_value = {"_id": ingredient_id, "user_id": ObjectId(), "name": "olive oil", "quantity": "1", "notes": "",}
    resp = _test_client.post(f"/my-pantry/{ingredient_id}/edit", data={"name": "extra virgin olive oil", "quantity": "2", "notes": "good",}, follow_redirects=False,)

    assert resp.status_code == 302
    assert "/my-pantry" in resp.headers["Location"]

    mock_db.ingredients.update_one.assert_called_once()
    filt, update = mock_db.ingredients.update_one.call_args[0]
    assert filt["_id"] == ingredient_id
    assert update["$set"]["name"] == "extra virgin olive oil"
    assert update["$set"]["quantity"] == "2"
    assert update["$set"]["notes"] == "good"


@patch("app.db")
def test_delete_ingredient_deletes_and_redirects(mock_db, _test_client, test_user):
    """POST /my-pantry/<id>/delete should delete ingredient and redirect to new pantry."""
    ingredient_id = ObjectId()
    resp = _test_client.post(f"/my-pantry/{ingredient_id}/delete", follow_redirects=False)

    assert resp.status_code == 302
    assert "/my-pantry" in resp.headers["Location"]

    mock_db.ingredients.delete_one.assert_called_once()
    filt = mock_db.ingredients.delete_one.call_args[0][0]
    assert filt["_id"] == ingredient_id


@patch("app.recommendations")
@patch("app.requests.post")
@patch("app.db")
def test_recommend_recipes(mock_db, mock_requests_post, mock_recommendations, _test_client, test_user): 
    """POST /home/recommendations should return recipes correct recipes."""
    ingredient_id = ObjectId()

    mock_db.ingredients.find.return_value = [
        {"_id": ingredient_id, "user_id": ObjectId(test_user.id), "name": "olive oil", "quantity": "1", "notes": "",},
        {"_id": ingredient_id, "user_id": ObjectId(test_user.id), "name": "chicken", "quantity": "1lb", "notes": "",}
    ]

    # Fake ML response 
    fake_recipes = [
        {"name": "Turbo Chicken", "image": "https://img.spoonacular.com/recipes/663971-312x231.jpg"},
        {"name": "Crispy Buttermilk Fried Chicken", "image": "https://img.spoonacular.com/recipes/640803-312x231.jpg"}
    ]

    # Mock requests.post call
    mock_res = mock_requests_post.return_value
    mock_res.json.return_value = fake_recipes 
    mock_res.raise_for_status.return_value = None
    res = _test_client.post("/recommendations", data={"top_n": 5})

    assert res.status_code == 200

    mock_db.ingredients.find.assert_called_once_with({"user_id": ObjectId(test_user.id)})

    # Assert ML API called correctly
    mock_requests_post.assert_called_once()
    sent = mock_requests_post.call_args[1]["json"]
    assert sent["ingredients"] == ["olive oil", "chicken"]
    assert sent["top_n"] == 5

    mock_recommendations.update_one.assert_called_once()
    assert b"Turbo Chicken" in res.data
    assert b"Crispy Buttermilk Fried Chicken" in res.data
