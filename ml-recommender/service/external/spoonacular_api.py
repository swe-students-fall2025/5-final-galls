from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import requests
import os

API_KEY = os.getenv("SPOONACULAR_API_KEY", "395ad339be8b4de3bb48c175e8c890c4")
FIND_BY_INGREDIENTS_URL = "https://api.spoonacular.com/recipes/findByIngredients"
COMPLEX_SEARCH_URL = "https://api.spoonacular.com/recipes/complexSearch"

app = FastAPI()
# -------- Request Model -------
class RecommendationRequest(BaseModel):
    ingredients: List[str]
    top_n: int = 5
    dietary: Optional[List[str]] = None

# ------- Helper Functions -------
def get_recipes_by_ingredients(pantry: List[str], number: int = 10, dietary: List[str] = None) -> List[dict]:
    # find receipes with used/missed ingredients
    params = {
        "apiKey": API_KEY,
        "ingredients": ",".join(pantry),
        "number": number,
        "ranking": 1,
        "ignorePantry": False
    }
    resp = requests.get(FIND_BY_INGREDIENTS_URL, params=params)
    resp.raise_for_status()
    return resp.json()

def filter_recipes_by_diet(recipes: List[dict], dietary: List[str]):
    if not dietary:
        return recipes

    diet_query = ",".join(dietary)
    params = {
        "apiKey": API_KEY,
        "diet": diet_query,
        "number": 100  # get enough recipes for filtering
    }
    resp = requests.get(COMPLEX_SEARCH_URL, params=params)
    resp.raise_for_status()
    valid_ids = {r["id"] for r in resp.json().get("results", [])}

    # Keep only recipes that match dietary tags
    return [r for r in recipes if r["id"] in valid_ids]

# ------- API Endpoint -------
@app.post("/recommendations")
def recommend(request: RecommendationRequest):
    # Step 1: Get recipes by ingredients
    recipes = get_recipes_by_ingredients(request.ingredients, number=request.top_n * 5)

    # Step 2: Filter by dietary tags if provided
    recipes_filtered = filter_recipes_by_diet(recipes, request.dietary)

    # Step 3: Sort by matched ingredient count
    recipes_sorted = sorted(recipes_filtered, key=lambda r: r["usedIngredientCount"], reverse=True)

    # Step 4: Return top N recipes
    results = []
    for r in recipes_sorted[:request.top_n]:
        results.append({
            "name": r["title"],
            "matched_ingredients": r["usedIngredientCount"],
            "missing_ingredients": [i["name"] for i in r.get("missedIngredients", [])],
            "image": r.get("image"),
            "dietary_tags": request.dietary or []
        })

    return results