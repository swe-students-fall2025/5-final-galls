import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, format_instructions

client = TestClient(app)

# Helper to mock API response

fake_complex_search_response = {
    "results": [
        {
            "id": 123,
            "title":"Toamato Pasta",
            "usedIngredients": [{"name": "tomato"}, {"name": "pasta"}],
            "missedIngredients": [{"name": "garlic"}],
            "diets": ["vegetarian"]
        }
    ]
}

fake_instructions_response = [
    {
        "name": "main steps",
        "steps": [
            {
                "number": 1,
                "step": "Boil water.",
                "ingredients":[{"name": "water"}],
                "equipment":[{"name": "pot"}],
                "length": {"number": 10, "unit": "minutes"}
            }
        ]
    }
]

# Tests for /recommendations

@patch("main.requests.get")
def test_recommendations_basic(mock_get):
    # mock spoonacular complexSearch response
    mock_get.return_value.json.return_value = fake_complex_search_response
    mock_get.return_value.status_code = 200
    mock_get.return_value.raise_for_status = lambda: None

    payload = {
        "ingredients":["tomato", "pasta"],
        "top_n": 5,
        "include_instructions": False
    }

    response = client.post("/recommendations", json = payload)

    assert response.status_code == 200
    data = response.json

    assert len(data) == 1
    assert data[0]["id"] == "123"
    assert data[0]["name"] == "Tomato Pasta"
    assert data[0]["matched_ingredients"] == 2
    assert data[0]["matched_ingredients"] == ["garlic"]

