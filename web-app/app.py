from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

ingredients = db["ingredients"]
users = db["users"]

mockIngredients = [
    {"name": "Flour", "quantity": "1 lb", "notes": "half empty"},
    {"name": "Sugar", "quantity": "1/2 lb", "notes": ""},
    {"name": "Salt", "quantity": "1 oz", "notes": "full"},
]

@app.route("/")
def index():
    # ingredients = db.ingredients.find()
    # return render_template("home.html")
    return render_template("home.html", ingredients=mockIngredients)


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/my-recipes")
def my_recipes():
    return render_template("my_recipes.html")

@app.route("/my-pantry")
def my_pantry():
    return render_template("my_pantry.html")
    
@app.route("/my-pantry/add", methods=["GET", "POST"])
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
def delete_ingredient(ingredient_id):
    return redirect(url_for("my_pantry"))

@app.route("/add-recipe")
def add_recipe():
    return render_template("add_recipe.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
