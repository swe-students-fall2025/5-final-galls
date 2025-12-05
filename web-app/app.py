from flask import Flask, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["ingredients"]

@app.route("/")
def index():
    ingredients = db.ingredients.find()
    return render_template("index.html", ingredients=ingredients)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/my-recipes")
def my_recipes():
    return render_template("my_recipes.html")

@app.route("/my-pantry")
def my_pantry():
    return render_template("my_pantry.html")
    

@app.route("/add-recipe")
def add_recipe():
    return render_template("add_recipe.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
