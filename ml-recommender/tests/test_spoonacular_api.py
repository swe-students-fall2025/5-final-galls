import unittest
from fastapi.testclient import TestClient
from requests.exceptions import HTTPError
from unittest.mock import MagicMock, patch
from service.external.spoonacular_api import app, format_instructions

client = TestClient(app)

# Helper fake responses
fake_complex_search_response = {
    "results": [
        {
            "id": 123,
            "title": "Tomato Pasta",
            "usedIngredients": [{"name": "tomato"}, {"name": "pasta"}],
            "missedIngredients": [{"name": "garlic"}],
            "diets": ["vegetarian"]
        }
    ]
}

fake_instructions_response = [
    {
        "name": "Main Steps",
        "steps": [
            {
                "number": 1,
                "step": "Boil water.",
                "ingredients": [{"name": "water"}],
                "equipment": [{"name": "pot"}],
                "length": {"number": 10, "unit": "minutes"}
            }
        ]
    }
]

# -------------------- Tests --------------------

@patch("service.external.spoonacular_api.requests.get")
def test_recommendations_basic(mock_get):
    # Mock the complexSearch response
    mock_resp = MagicMock()
    mock_resp.json.return_value = fake_complex_search_response
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_get.return_value = mock_resp

    payload = {
        "ingredients": ["tomato", "pasta"],
        "top_n": 5,
        "include_instructions": False
    }

    response = client.post("/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 123
    assert data[0]["name"] == "Tomato Pasta"
    assert data[0]["matched_ingredients"] == 2
    assert data[0]["missing_ingredients"] == ["garlic"]


@patch("service.external.spoonacular_api.requests.get")
def test_recommendations_with_instructions(mock_get):
    # two consecutive calls: complexSearch and analyzedInstructions
    mock_resp_1 = MagicMock()
    mock_resp_1.json.return_value = fake_complex_search_response
    mock_resp_1.status_code = 200
    mock_resp_1.raise_for_status = lambda: None

    mock_resp_2 = MagicMock()
    mock_resp_2.json.return_value = fake_instructions_response
    mock_resp_2.status_code = 200
    mock_resp_2.raise_for_status = lambda: None

    mock_get.side_effect = [mock_resp_1, mock_resp_2]

    payload = {
        "ingredients": ["tomato", "pasta"],
        "include_instructions": True
    }

    response = client.post("/recommendations", json=payload)
    assert response.status_code == 200

    recipe = response.json()[0]
    assert "instructions" in recipe
    assert recipe["instructions"][0]["steps"][0]["instruction"] == "Boil water."


@patch("service.external.spoonacular_api.requests.get")
def test_get_instructions_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = fake_instructions_response
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_get.return_value = mock_resp

    response = client.get("/recipe/123/instructions")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Main Steps"


@patch("service.external.spoonacular_api.requests.get")
def test_get_instructions_not_found(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = HTTPError("404 Client Error")
    mock_get.return_value = mock_resp

    response = client.get("/recipe/999/instructions")
    assert response.status_code == 404

def test_format_instructions():
    formatted = format_instructions(fake_instructions_response)
    assert len(formatted) == 1
    assert formatted[0]["name"] == "Main Steps"
    assert formatted[0]["steps"][0]["instruction"] == "Boil water."
    assert formatted[0]["steps"][0]["ingredients"] == ["water"]
    assert formatted[0]["steps"][0]["equipment"] == ["pot"]
    assert formatted[0]["steps"][0]["time"] == {"number": 10, "unit": "minutes"}