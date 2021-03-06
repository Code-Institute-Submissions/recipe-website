import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

""" Import the env.py file

where I used it for set up the environment variable for my local workspace
"""
from os import path

if path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MYDATABASE")
app.config["MONGO_URI"] = os.environ.get("MYMONGO_URI")

mongo = PyMongo(app)

# --------------- Recipe ----------------
""" Create index

This index is used for the search_recipe_name function.
Mentor advise me to put this code outside of the function.
"""
mongo.db.recipes.create_index([("recipe_name", "text")])


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    return render_template("recipes.html", recipes=mongo.db.recipes.find())


@app.route("/add_recipe")
def add_recipe():
    """ Add recipe form.

    Redirect the user to the recipe form page that will allow him to enter
    the information about the recipe then submit the data.
    """
    return render_template(
        "addrecipe.html",
        type=mongo.db.recipe_type.find().sort("type_name", 1)
    )


@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    """ Insert recipe to Mongo Database.

    Send all the data from the form to Mongo Database in a dictionary format.

    Then redirect the user to the get_recipes page.
    """
    recipes = mongo.db.recipes
    recipes.insert_one(request.form.to_dict())
    return redirect(url_for("get_recipes"))


@app.route("/recipe/<recipe_id>")
def recipe_description(recipe_id):
    """ Recipe description of the recipe selected.

    User redirect to the recipe page he selected from get_recipes page showing
    all the data related to the recipe.
    """
    one_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipedescription.html", recipe=one_recipe)


@app.route("/edit_recipe/<recipe_id>")
def edit_recipe(recipe_id):
    """ Edit the recipe

    User redirect to the edit page allowing him to edit the recipe
    he selected in the recipe description page.
    """
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    all_type = mongo.db.recipe_type.find().sort("type_name", 1)
    return render_template(
        "editrecipe.html", recipe=the_recipe, type=all_type
    )


@app.route("/update_recipe/<recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    """ Update the recipe.

    Send all the updated data to Mongo database.

    Then redirect the user to the get_recipes page.
    """
    recipe = mongo.db.recipes
    recipe.update(
        {"_id": ObjectId(recipe_id)},
        {
            "author_name": request.form.get("author_name"),
            "serving_number": request.form.get("serving_number"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "recipe_type": request.form.get("recipe_type"),
            "preparation_time": request.form.get("preparation_time"),
            "cooking_time": request.form.get("cooking_time"),
            "ingredients": request.form.get("ingredients"),
            "methods": request.form.get("methods"),
            "image_link": request.form.get("image_link"),
        },
    )
    return redirect(url_for("get_recipes"))


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    """ Delete the recipe

    User are able to delete the recipe selected.

    Then redirect to the get_recipes page.
    """
    recipe = mongo.db.recipes
    recipe.delete_one({"_id": ObjectId(recipe_id)})
    return redirect(url_for("get_recipes"))


@app.route("/search_recipe")
def search_recipe():
    """ Search recipe page

    User redirect to the search recipe page allowing him to search
    for the recipe name.

    Once the search is launch, the function search_recipe_name starts.
    """
    return render_template("searchrecipe.html")


@app.route("/search_recipe_name", methods=["POST"])
def search_recipe_name():
    """ Search recipe by name

    Ask Mongo to search for the term received in the form.
    Then redirect user to recipe found page.
    https://docs.mongodb.com/manual/text-search/ and https://docs.mongodb.com/manual/indexes/
    allowed me to understand how to write the function to find a recipe by his name
    """
    # Get the search term from the form
    search_term = request.form.get("recipe_name")

    # Find the search term
    recipe_found = mongo.db.recipes.find({"$text": {"$search": search_term}})

    return render_template("recipefound.html", recipe=recipe_found)


# --------------- Type ----------------

# Get recipe type
@app.route("/get_type")
def get_type():
    return render_template("type.html", type=mongo.db.recipe_type.find())


@app.route("/add_type")
def add_type():
    """ Add type form.

    Redirect the user to the type form page that will allow him
    to enter the type he wants then submit the data.
    """
    return render_template("addtype.html")


@app.route("/insert_type", methods=["POST"])
def insert_type():
    """ Insert type to Mongo Database.

    Send the data from the form to Mongo Database in a dictionary format.

    Then redirect the user to the get_type page.
    """
    recipe_type = mongo.db.recipe_type
    recipe_type.insert_one(request.form.to_dict())
    return redirect(url_for("get_type"))


# Delete recipe type
@app.route("/delete_type/<type_id>")
def delete_type(type_id):
    """ Delete the type

    User are able to delete the type selected.

    Then redirect to the get_type page.
    """
    recipe_type = mongo.db.recipe_type
    recipe_type.delete_one({"_id": ObjectId(type_id)})
    return redirect(url_for("get_type"))


if __name__ == "__main__":
    # This app.run is for heroku
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)

    # This app.run is for local vscode
    # app.run(debug=True)
