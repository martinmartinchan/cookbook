from flask import Flask, jsonify, request
from functools import wraps
from flask_cors import CORS
import cookbook, configurations

def create_response(data: dict = None, status: int = 200, message: str = ""):
  response = {
      "code": status,
      "success": 200 <= status < 300,
      "message": message,
      "result": data,
  }
  return jsonify(response)

def authentication_required(cb):
  def authenticate_wrapper(f):
    @wraps(f)
    def authenticate(*args, **kwargs): 
      if 'password' in request.get_json():
        password = request.get_json()['password']
        if cb.authenticate(password):
          return f(*args, **kwargs)
        else:
          return create_response({}, 401, "Password is incorrect")
      else:
        return create_response({}, 401, "Authentication needed")
    return authenticate
  return authenticate_wrapper

def create_app(config=None):
  app = Flask(__name__)
  if config is None:
    app.config.from_object(configurations.ProductionConfig())
  elif config is "Development":
	  app.config.from_object(configurations.DevelopmentConfig())
  elif config is "Testing":
	  app.config.from_object(configurations.TestConfig())

  CORS(app)

  cb = cookbook.Cookbook(app.config)
  @app.route('/', methods=['GET'])
  @app.route('/recipes', methods=['GET'])
  def getAllRecipes():
    success = False
    recipes = []
    message = ""
    (success, recipes, message) = cb.getAllRecipes()
    if success:
      return create_response(recipes, 200, message)
    else:
      return create_response(recipes, 404, message)
    
  @app.route('/recipe')
  def getRecipeByName():
    recipeName = request.args.get('name', default = "", type = str)
    if recipeName == "":
      return create_response({}, 404, "No recipe name given")
    else:
      (success, recipe, message) = cb.getRecipeByName(recipeName)
      if success:
        return create_response(recipe, 200, message)
      else:
        return create_response({}, 404, message)

  @app.route('/addrecipe', methods=['POST'])
  @authentication_required(cb)
  def addRecipe():
    (success, message) = cb.addRecipe(request.get_json())
    if success:
      (successNotUsed, recipes, messageNotUsed) = cb.getAllRecipes()
      return create_response(recipes, 201, message)
    else:
      return create_response({}, 400, message)

  @app.route('/deleterecipe', methods=['DELETE'])
  @authentication_required(cb)
  def deleteRecipe():
    if 'name' in request.get_json():
      (success, message) = cb.deleteRecipe(request.get_json()['name'])
      if success:
        (successNotUsed, recipes, messageNotUsed) = cb.getAllRecipes()
        return create_response(recipes, 200, message)
      else:
        return create_response({}, 400, message)
    else:
      return create_response({}, 400, "Please provide name of the recipe you want to delete")

  @app.route('/editrecipe', methods=['PUT'])
  @authentication_required(cb)
  def editRecipe():
    if 'name' not in request.get_json():
      return create_response({}, 400, "Please provide name of the recipe you want to edit")
    if 'recipe' not in request.get_json():
      return create_response({}, 400, "Please provide new information you want to edit the recipe with")
    (success, message) = cb.editRecipe(request.get_json()['name'], request.get_json()['recipe'])
    if success:
      (successNotUsed, recipes, messageNotUsed) = cb.getAllRecipes()
      return create_response(recipes, 200, message)
    else:
      return create_response({}, 400, message)

  return app
