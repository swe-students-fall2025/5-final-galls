from utils import get_ingredients

def filter_recipes(recipes, user_restrictions):

    filtered = recipes
    
    if user_restrictions.get('diet'):
        filtered = [r for r in filtered if meets_diet(r, user_restrictions['diet'])]
    
    if user_restrictions.get('intolerances'):
        filtered = [r for r in filtered if not has_intolerance(r, user_restrictions['intolerances'])]
    
    if user_restrictions.get('excluded_ingredients'):
        filtered = [r for r in filtered if not has_excluded(r, user_restrictions['excluded_ingredients'])]
    
    return filtered


def meets_diet(recipe, diet):
    diets = [diet] if isinstance(diet, str) else diet
    diets = [d.lower().strip() for d in diets]
    
    if not diets:
        return True
    
    diet_fields = {
        'vegetarian': recipe.get('vegetarian', False),
        'vegan': recipe.get('vegan', False),
        'gluten free': recipe.get('glutenFree', False),
        'ketogenic': recipe.get('ketogenic', False),
        'dairy free': recipe.get('dairyFree', False),
        'paleo': recipe.get('paleo', False),
        'pescatarian': recipe.get('pescatarian', False),
        'primal': recipe.get('primal', False),
        'whole30': recipe.get('whole30', False),
        'low fodmap': recipe.get('lowFodmap', False),
    }
    
    if 'diets' in recipe:
        recipe_diets = [d.lower() for d in recipe['diets']]
        if any(diet in recipe_diets for diet in diets):
            return True
    
    return any(diet_fields.get(diet, False) for diet in diets)


def has_intolerance(recipe, intolerances):
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


def has_excluded(recipe, excluded):
    ingredients = get_ingredients(recipe)
    excluded = [e.lower().strip() for e in excluded]
    
    for ingredient in ingredients:
        if any(ex in ingredient for ex in excluded):
            return True
    
    return False

def validate_restrictions(restrictions):
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