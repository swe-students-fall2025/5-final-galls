from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import os

API_KEY = os.getenv("SPOONACULAR_API_KEY", "3a09c46bac16494eabe50322b303b9a9")
if not API_KEY:
    raise ValueError("SPOONACULAR_API_KEY is not set in environment variables")

COMPLEX_SEARCH_URL = "https://api.spoonacular.com/recipes/complexSearch"

app = FastAPI()

class RecommendationRequest(BaseModel):
    ingredients: List[str]
    top_n: int = 5
    dietary: Optional[List[str]] = None  # optional dietary filter

def get_recipes_by_ingredients(ingredients: List[str], top_n: int, dietary: Optional[List[str]] = None):
    """Call Spoonacular API and return recipes based on ingredients and dietary filters."""
    params = {
        "apiKey": API_KEY,
        "includeIngredients": ",".join(ingredients),
        "number": top_n,
        "sort": "max-used-ingredients",
        "fillIngredients": "true",
        "addRecipeInformation": "true"
    }

    if dietary:
        params["diet"] = ",".join(dietary)

    try:
        resp = requests.get(COMPLEX_SEARCH_URL, params=params)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except requests.RequestException as e:
        print(e,e.response)
        raise HTTPException(status_code=500, detail=f"Error fetching recipes: {e}")

@app.post("/recommendations")
def recommend(request: RecommendationRequest):
    recipes = get_recipes_by_ingredients(request.ingredients, request.top_n, request.dietary)

    simplified = []
    for r in recipes:
        used = [i["name"] for i in r.get("usedIngredients", [])]
        missed = [i["name"] for i in r.get("missedIngredients", [])]

        simplified.append({
            "name": r.get("title"),
            "matched_ingredients": len(used),  # counting all used ingredients
            "missing_ingredients": missed,
            "image": r.get("image"),
            "dietary_tags": r.get("diets", [])
        })

    return simplified
