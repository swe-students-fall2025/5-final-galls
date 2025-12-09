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
DB_NAME = os.getenv("DB_NAME", "ingredients")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

ingredients = db["ingredients"]
users = db["users"]
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
def index():
    user_ingredients = list(db.ingredients.find({"user_id": current_user.id}))
    return render_template("home.html", user=current_user,ingredients=user_ingredients)
    # ingredients = db.ingredients.find()
    # return render_template("home.html")


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
        return redirect(url_for("index"))

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
            error= "Account with this email already exists."
            return render_template("register.html", error=error)

        user_doc = {
            "email": email,
            "password": hashed_password,
            "username": username
        }
        db.users.insert_one(user_doc)

        user = User(user_doc)
        login_user(user)

        return redirect(url_for("index"))

    return render_template("register.html")

@app.route("/my-recipes")
@login_required
def my_recipes():
    return render_template("my_recipes.html")

@app.route("/my-pantry")
@login_required
def my_pantry():
    user_ingredients = list(db.ingredients.find({"user_id": current_user.id}))
    ingredient_names = [i["name"] for i in user_ingredients]
    return render_template("my_pantry.html", ingredients=user_ingredients, ingredient_names=ingredient_names, suggestion_api_url=SUGGESTION_API_URL)

@app.route("/my-pantry/add", methods=["GET", "POST"])
@login_required
def add_ingredient():
    if request.method == "POST":
        return redirect(url_for("my_pantry"))

    return render_template("add_ingredient.html")

@app.route("/my-pantry/<ingredient_id>/edit", methods=["GET", "POST"])
def edit_ingredient(ingredient_id):
    if request.method == "POST":
        return redirect(url_for("my_pantry"))

    return render_template("edit_ingredient.html")

@app.route("/my-pantry/<ingredient_id>/delete", methods=["POST"])
@login_required
def delete_ingredient(ingredient_id):
    return redirect(url_for("my_pantry"))

@app.route("/add-recipe")
@login_required
def add_recipe():
    return render_template("add_recipe.html")

SUGGESTION_API_URL = os.getenv("ML_RECOMMENDER_URL", "http://localhost:8000/recommendations")

@app.route("/recommendations", methods=["POST"])
@login_required
def recommend_recipes():
    # Get pantry ingredients from your DB
    user_ingredients = list(db.ingredients.find({"user_id": current_user.id}))
    ingredient_names = [i["name"] for i in user_ingredients]

    # Optional: get dietary preferences from frontend form
    dietary = request.form.getlist("dietary")

    payload = {
        "ingredients": ingredient_names,
        "top_n": 5,
        "dietary": dietary
    }

    try:
        response = requests.post(SUGGESTION_API_URL, json=payload)
        response.raise_for_status()
        recipes = response.json()
    except Exception as e:
        print("Error calling ML Recommender:", e)
        recipes = []

    # Pass recipes to a template for display
    return render_template("recommendations.html", recipes=recipes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
