[![Web App CI/CD](https://github.com/swe-students-fall2025/5-final-galls/actions/workflows/web-app.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-galls/actions/workflows/web-app-ci.yml)

[![ML Recommender CI/CD](https://github.com/swe-students-fall2025/5-final-galls/actions/workflows/ml-recommender.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-galls/actions/workflows/ml-recommender.yml)

# Pantry Pal
### Smart Recipe Reccomendations Based on What You Already Have!

Pantry Pal is an intelligent recipe recommendation system that helps you discover delicious recipes using the ingredients you already have in your kitchen!

## Features
### Technical Features
- User data stored in MongoDB

### Intelligent Recipe Recommendations
- Instantly discover recipes you can make with what you have!
- Recipes ranked by how many ingredients you already own
- Clear list of what you need to buy to complete a recipe
- Access to 360,000+ recipes from Spoonacular API

### Dietary Preferences and Restrictions
- Filter by vegetarian, vegan, gluten-free, keto, paleo, pescatarian, and primal
- Automatically exclude recipes with common intolerances
- Block specific ingredients you dislike
- Only see recipes that meet all your requirements!

## 📌 Overview

This repository contains a complete multi-container system with three main components:

### **🧠 Backend/ML Client**
- Calls the Spoonacular API to generate recipes + instructions based on ingredients received from the Web App
- Returns top recipes based on ingredient compatability
- Notes any dietary restrictions

### **🌐 Web App**
- Flask-based frontend
- Displays recipe options in your home page, allowing you to add/save them
- Sends pantry ingredients to the ML client

### **🗄️ MongoDB Database**
- Stores ingredients and recipes that are saved into "My Recipes"
- Shared and networked automatically inside Docker


## 👥 Team
- Grace He [github](https://github.com/gracehe04)
- Luna Suzuki [github](https://github.com/lunasuzuki)
- Aden Juda [github](https://github.com/yungsemitone)
- Lucy Hartigan [github](https://github.com/lucyhartigan)
- Sydney Nadeau [github](https://github.com/sen5217)

## Docker Images
[sen5217/web-app](https://hub.docker.com/r/sen5217/web-app)

[sen5217/ml-recommender](https://hub.docker.com/r/sen5217/ml-recommender)

## 🚀 Getting Started

This guide explains how to run the entire system on **Windows, macOS, or Linux**.

---

## ✔ 1. Prerequisites

Install the following:

- **Docker Desktop**
- **Git**

---

## ✔ 2. Clone the Repository


- git clone https://github.com/swe-students-fall2025/5-final-galls
- cd 5-final-galls

---

## ✔ 3. Create the Environment File
You can copy the example file:

- cp env.example .env
- Or create it manually:

- Use .env file provided in submission

---

## ✔ 4. Launch All Services
Build and start every container:


- docker compose up --build

---

## ✔ 5. Access the Web Interface
Once everything is running, open:

- http://localhost:5001

---

## ✔ 6. Running Tests Locally

Each subsystem has its own virtual environment managed with pipenv.

ML Client Tests
- cd ml-recommender
- pipenv install --dev
- pipenv run pytest --cov

Web App Tests
- cd web-app
- pipenv install --dev
- pipenv run pytest --cov

---
## ✔ 7. Developer Local-Run Instructions (Without Docker)

Web App Only
- cd web-app
- pipenv install
- pipenv run flask run --port 5001

Machine Learning Client Only
- cd ml-recommender
- pipenv install
- pipenv run flask run --port 5001


Make sure MongoDB is running locally on localhost:27017.

---