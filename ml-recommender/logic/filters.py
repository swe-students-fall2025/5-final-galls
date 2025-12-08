from typing import List, Dict, Any

#takes a list of recipies and filters them based on the users dietary restrictions
def filter_recipes(recipes: List[Dict[str, Any]], user_restrictions: Dict[str, Any]) -> List[Dict[str, Any]]:
    filtered = recipes
    
    if user_restrictions.get('diet'):
        filtered = [r for r in filtered if meets_diet(r, user_restrictions['diet'])]
    
    if user_restrictions.get('intolerances'):
        filtered = [r for r in filtered if not has_intolerance(r, user_restrictions['intolerances'])]
    
    if user_restrictions.get('excluded_ingredients'):
        filtered = [r for r in filtered if not has_excluded(r, user_restrictions['excluded_ingredients'])]
    
    return filtered


# checks if the recipie has the ingredients the user is intolerant to
def has_intolerance(recipe: Dict[str, Any], intolerances: List[str]) -> bool:
    ingredients = get_ingredients(recipe)
    intolerances = [i.lower().strip() for i in intolerances]
    
    keywords = {
        'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'whey', 'casein'],
        'egg': ['egg', 'mayonnaise'],
        'gluten': ['wheat', 'flour', 'gluten', 'barley', 'rye', 'bread', 'pasta'],
        'grain': ['wheat', 'rice', 'oat', 'barley', 'corn', 'quinoa'],
        'peanut': ['peanut'],
        'soy': ['soy', 'tofu', 'edamame', 'tempeh'],
        'shellfish': ['shrimp', 'crab', 'lobster', 'prawn', 'crayfish'],
        'seafood': ['fish', 'salmon', 'tuna', 'cod', 'tilapia'],
        'tree nut': ['almond', 'walnut', 'pecan', 'cashew', 'pistachio', 'hazelnut'],
        'nuts': ['almond', 'walnut', 'pecan', 'cashew', 'pistachio', 'hazelnut', 'nut'],
        'sesame': ['sesame', 'tahini'],
        'sulfite': ['sulfite'],
        'wheat': ['wheat', 'flour'],
    }
    
    for intolerance in intolerances:
        words = keywords.get(intolerance, [intolerance])
        for ingredient in ingredients:
            if any(word in ingredient for word in words):
                return True
    
    return False

#if the user has specific ingredients they want to exclude
def has_excluded(recipe: Dict[str, Any], excluded: List[str]) -> bool:
    ingredients = get_ingredients(recipe)
    excluded = [e.lower().strip() for e in excluded]
    
    for ingredient in ingredients:
        if any(ex in ingredient for ex in excluded):
            return True
    
    return False


#gets all the ingredients from the recipie
def get_ingredients(recipe: Dict[str, Any]) -> List[str]:
    ingredients = []
    
    if 'extendedIngredients' in recipe:
        for ing in recipe['extendedIngredients']:
            name = ing.get('name') or ing.get('originalName') or ing.get('original', '')
            if name:
                ingredients.append(name.lower())
    
    elif 'ingredients' in recipe:
        for ing in recipe['ingredients']:
            if isinstance(ing, str):
                ingredients.append(ing.lower())
            elif isinstance(ing, dict):
                name = ing.get('name') or ing.get('originalName') or ing.get('original', '')
                if name:
                    ingredients.append(name.lower())
    
    return ingredients

#clean format
def validate_restrictions(restrictions: Dict[str, Any]) -> Dict[str, Any]:
    valid = {}
    
    valid_diets = [
        'vegetarian', 'vegan', 'gluten free', 'ketogenic', 
        'dairy free', 'paleo', 'pescatarian', 'primal', 
        'whole30', 'low fodmap'
    ]
    
    valid_intolerances = [
        'dairy', 'egg', 'gluten', 'grain', 'peanut', 'seafood',
        'sesame', 'shellfish', 'soy', 'sulfite', 'tree nut', 'wheat', 'nuts'
    ]
    
    if 'diet' in restrictions and restrictions['diet']:
        diet = restrictions['diet']
        if isinstance(diet, str):
            diet = diet.lower().strip()
            if diet in valid_diets:
                valid['diet'] = diet
        elif isinstance(diet, list):
            valid['diet'] = [d.lower().strip() for d in diet if d.lower().strip() in valid_diets]
    
    if 'intolerances' in restrictions and restrictions['intolerances']:
        intolerances = restrictions['intolerances']
        if isinstance(intolerances, list):
            valid['intolerances'] = [i.lower().strip() for i in intolerances 
                                    if i.lower().strip() in valid_intolerances]
    
    if 'excluded_ingredients' in restrictions and restrictions['excluded_ingredients']:
        excluded = restrictions['excluded_ingredients']
        if isinstance(excluded, list):
            valid['excluded_ingredients'] = [e.strip() for e in excluded if e.strip()]
    
    return valid