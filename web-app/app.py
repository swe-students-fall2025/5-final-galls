from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = 't3@m5g@lsp@ssw0rd'
bcrypt = Bcrypt(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
DB_NAME = os.getenv("DB_NAME", "pantry-pal")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

ingredients = db["ingredients"]
users = db["users"]
recommendations = db["recommendations"]

SUGGESTION_API_URL = "http://ml-recommender:8000/recommendations"

'''
mockIngredients = [
    {"name": "Flour", "quantity": "1 lb", "notes": "half empty"},
    {"name": "Sugar", "quantity": "1/2 lb", "notes": ""},
    {"name": "Salt", "quantity": "1 oz", "notes": "full"},
]
'''

class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.email = user_doc["email"]
        self.password = user_doc["password"]
        self.username = user_doc["username"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.users.find_one({"_id": ObjectId(user_id)})
    return User(user_doc) if user_doc else None

@app.route("/")
@login_required
def home():
    # Get current user's ingredients
    user_ingredients = list(db.ingredients.find({"user_id": ObjectId(current_user.id)}))

    # Get existing recommendations, if any
    rec_doc = recommendations.find_one({"user_id": ObjectId(current_user.id)})
    recipes = rec_doc["recipes"] if rec_doc else []

    return render_template(
        "home.html",
        user=current_user,
        ingredients=user_ingredients,
        recipes=recipes
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_doc = db.users.find_one({"username": username})

        if not user_doc:
            error = "User not found. Create an account or try again."
            return render_template("login.html", error=error)

        if not bcrypt.check_password_hash(user_doc["password"], password):
            error = "Invalid username/password. Try again"
            return render_template("login.html", error=error)

        user = User(user_doc)
        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        existing = db.users.find_one({"email": email})
        if existing:
            error = "Account with this email already exists."
            return render_template("register.html", error=error)

        user_doc = {
            "email": email,
            "password": hashed_password,
            "username": username
        }

        # Insert once and get the inserted _id
        result = db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        user = User(user_doc)
        login_user(user)

        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/my-recipes")
@login_required
def my_recipes():
    return render_template("my_recipes.html")

@app.route("/my-pantry")
@login_required
def my_pantry():
    user_ingredients = list(db.ingredients.find({"user_id": ObjectId(current_user.id)}))
    ingredient_names = [i["name"] for i in user_ingredients]
    return render_template("my_pantry.html", ingredients=user_ingredients, ingredient_names=ingredient_names)

@app.route("/my-pantry/add", methods=["GET", "POST"])
@login_required
def add_ingredient():
    if request.method == "POST":
        name = request.form ["name"]
        quantity = request.form["quantity"]
        notes = request.form["notes"]

        # save to db
        db.ingredients.insert_one({
            "user_id": ObjectId(current_user.id),
            "name": name,
            "quantity": quantity,
            "notes": notes
        })

        return redirect(url_for("my_pantry"))

    return render_template("add_ingredient.html")

@app.route("/my-pantry/<ingredient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_ingredient(ingredient_id):
    ingredient = db.ingredients.find_one({
        "_id": ObjectId(ingredient_id),
        "user_id": ObjectId(current_user.id)
    })
    if ingredient is None:
        return redirect(url_for("my_pantry"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        quantity = request.form.get("quantity", "").strip()
        notes = request.form.get("notes", "").strip()

        db.ingredients.update_one({"_id": ObjectId(ingredient_id), "user_id": ObjectId(current_user.id),}, {"$set": {"name": name, "quantity": quantity, "notes": notes,}},)

        return redirect(url_for("my_pantry"))

    return render_template("edit_ingredient.html", ingredient=ingredient,)

@app.route("/my-pantry/<ingredient_id>/delete", methods=["POST"])
@login_required
def delete_ingredient(ingredient_id):
    db.ingredients.delete_one({"_id": ObjectId(ingredient_id), "user_id": ObjectId(current_user.id)})
    return redirect(url_for("my_pantry"))

@app.route("/add-recipe")
@login_required
def add_recipe():
    return render_template("add_recipe.html")

@app.route("/recommendations", methods=["POST"])
@login_required
def recommend_recipes():
    # Get current user's ingredients
    user_ingredients = list(db.ingredients.find({"user_id": ObjectId(current_user.id)}))
    ingredient_names = [i["name"] for i in user_ingredients]

    # Read top_n from form
    try:
        top_n = int(request.form.get("top_n", 5))
    except ValueError:
        top_n = 5

    payload = {
        "ingredients": ingredient_names,
        "top_n": top_n,
        "dietary": []
    }

    try:
        # Call ML service
        response = requests.post(SUGGESTION_API_URL, json=payload)
        response.raise_for_status()
        recipes = response.json()
        # print("ML Recommender response:", recipes, flush=True)

    except Exception as e:
        print("Error calling ML Recommender:", e, flush=True)
        recipes = []

    # Save/update recipes in MongoDB
    result = recommendations.update_one(
        {"user_id": ObjectId(current_user.id)},
        {"$set": {"recipes": recipes, "user_id": ObjectId(current_user.id)}},
        upsert=True
    )

    # Re-render home with updated recipes
    return render_template(
        "home.html",
        user=current_user,
        ingredients=user_ingredients,
        recipes=recipes
    )

@app.route("/recipes/<recipe_id>")
@login_required
def recipe_details(recipe_id):
    rec_doc = recommendations.find_one({"user_id": ObjectId(current_user.id)})
    if not rec_doc:
        return redirect(url_for("home"))

    recipe = next((r for r in rec_doc.get("recipes", []) if str(r.get("id")) == recipe_id), None)
    if not recipe:
        return redirect(url_for("home"))

    if "instructions" not in recipe or not recipe["instructions"]:
        try:
            resp = requests.get(f"http://ml-recommender:8000/recommendations")
            resp.raise_for_status()
            ml_recipes = resp.json()
            recipe_data = next((r for r in ml_recipes if r["id"] == int(recipe_id)), {})
            recipe["instructions"] = recipe_data.get("instructions", [])
        except Exception as e:
            print(f"Error fetching instructions for recipe {recipe_id}: {e}")
            recipe["instructions"] = []

    return render_template("recipe_details.html", recipe=recipe)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
