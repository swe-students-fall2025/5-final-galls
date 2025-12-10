# from fastapi.testclient import TestClient
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from service.main import app

# client = TestClient(app)


# def test_health_endpoint():
#     response = client.get("/health")
#     assert response.status_code in [200, 404]


# def test_api_exists():
#     assert app is not None

#start tests here
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.main import app
from unittest.mock import patch, Mock

client = TestClient(app)


def test_app_loads():
    assert app is not None

#test - returns data
@patch('service.external.spoonacular_api.requests.get')
def test_recommendations_endpoint_works(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "id": 123,
                "title": "Chicken Rice Bowl",
                "image": "https://example.com/image.jpg",
                "usedIngredients": [{"name": "chicken"}, {"name": "rice"}],
                "missedIngredients": [{"name": "soy sauce"}],
                "diets": ["gluten free"]
            }
        ]
    }
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["chicken", "rice"],
        "top_n": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

#test - dietary filters
@patch('service.external.spoonacular_api.requests.get')
def test_dietary_filtering_works(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "id": 456,
                "title": "Vegan Salad",
                "image": "https://example.com/salad.jpg",
                "usedIngredients": [{"name": "lettuce"}],
                "missedIngredients": [],
                "diets": ["vegan"],
                "vegetarian": True,
                "vegan": True
            }
        ]
    }
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["lettuce"],
        "top_n": 5,
        "dietary": ["vegan"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

#test - intolerances
@patch('service.external.spoonacular_api.requests.get')
def test_intolerance_filtering_works(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "id": 789,
                "title": "Dairy Free Pasta",
                "image": "https://example.com/pasta.jpg",
                "usedIngredients": [{"name": "pasta"}],
                "missedIngredients": [],
                "diets": []
            }
        ]
    }
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["pasta"],
        "top_n": 5,
        "intolerances": ["dairy"]
    })
    
    assert response.status_code == 200

#test - excluded ingredients
@patch('service.external.spoonacular_api.requests.get')
def test_excluded_ingredients_works(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["chicken"],
        "top_n": 5,
        "excluded_ingredients": ["mushrooms"]
    })
    
    assert response.status_code == 200

#test recs with multiple filters
@patch('service.external.spoonacular_api.requests.get')
def test_recommendations_with_all_filters(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["chicken", "rice"],
        "top_n": 5,
        "dietary": ["gluten free"],
        "intolerances": ["dairy", "nuts"],
        "excluded_ingredients": ["mushrooms", "cilantro"]
    })
    
    assert response.status_code == 200

#multiple dietary restrictions
@patch('service.external.spoonacular_api.requests.get')
def test_recommendations_multiple_dietary_filters(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["tofu"],
        "top_n": 5,
        "dietary": ["vegan", "gluten free", "low fodmap"]
    })
    
    assert response.status_code == 200

#multiple intolerances
@patch('service.external.spoonacular_api.requests.get')
def test_recommendations_multiple_intolerances(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    response = client.post("/recommendations", json={
        "ingredients": ["chicken"],
        "top_n": 5,
        "intolerances": ["dairy", "eggs", "gluten", "shellfish"]
    })
    
    assert response.status_code == 200
