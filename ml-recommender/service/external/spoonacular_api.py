from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import os

API_KEY = os.getenv("SPOONACULAR_API_KEY", "1630fb1bb80c4451896924049cf16ebf")
if not API_KEY:
    raise ValueError("SPOONACULAR_API_KEY is not set in environment variables")

BASE_URL = "https://api.spoonacular.com"
COMPLEX_SEARCH_URL = f"{BASE_URL}/recipes/complexSearch"

app = FastAPI()

class RecommendationRequest(BaseModel):
    ingredients: List[str]
    top_n: int = 5
    dietary: Optional[List[str]] = None
    include_instructions: Optional[bool] = False


def get_recipes_by_ingredients(ingredients: List[str], top_n: int, dietary: Optional[List[str]] = None):
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
        raise HTTPException(status_code=500, detail=f"Error fetching recipes: {e}")


def get_recipe_instructions(recipe_id: int, step_breakdown: bool = True):
    url = f"{BASE_URL}/recipes/{recipe_id}/analyzedInstructions"
    
    params = {
        "apiKey": API_KEY,
        "stepBreakdown": step_breakdown
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching instructions for recipe {recipe_id}: {e}")
        return None


def format_instructions(analyzed_instructions):
    """Format analyzed instructions into a cleaner structure."""
    if not analyzed_instructions:
        return []
    
    formatted = []
    
    for instruction_set in analyzed_instructions:
        section = {
            'name': instruction_set.get('name', 'Main Recipe'),
            'steps': []
        }
        
        for step in instruction_set.get('steps', []):
            step_info = {
                'number': step.get('number'),
                'instruction': step.get('step'),
                'ingredients': [ing.get('name') for ing in step.get('ingredients', [])],
                'equipment': [eq.get('name') for eq in step.get('equipment', [])],
            }
            
            if 'length' in step:
                step_info['time'] = step['length']
            
            section['steps'].append(step_info)
        
        formatted.append(section)
    
    return formatted


@app.post("/recommendations")
def recommend(request: RecommendationRequest):
    recipes = get_recipes_by_ingredients(request.ingredients, request.top_n, request.dietary)

    simplified = []
    for r in recipes:
        used = [i["name"] for i in r.get("usedIngredients", [])]
        missed = [i["name"] for i in r.get("missedIngredients", [])]

        recipe_data = {
            "id": r.get("id"),
            "name": r.get("title"),
            "matched_ingredients": len(used),
            "missing_ingredients": missed,
            "image": r.get("image"),
            "dietary_tags": r.get("diets", [])
        }
        
        if request.include_instructions:
            instructions = get_recipe_instructions(r.get("id"))
            recipe_data["instructions"] = format_instructions(instructions)
        
        simplified.append(recipe_data)

    return simplified


@app.get("/recipe/{recipe_id}/instructions")
def get_instructions(recipe_id: int):
    instructions = get_recipe_instructions(recipe_id)
    
    if instructions is None:
        raise HTTPException(status_code=404, detail="Instructions not found")
    
    return format_instructions(instructions)
