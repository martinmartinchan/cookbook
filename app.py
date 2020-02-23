from flask import Flask, jsonify, request
from src import cookbook
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def create_response(data: dict = None, status: int = 200, message: str = ""):
    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response)

def authentication_required(f):
  @wraps(f)
  def authenticate(*args, **kwargs): 
    if 'password' in request.get_json():
      password = request.get_json()['password']
      if cookbook.authenticate(password):
        return f(*args, **kwargs)
      else:
        return create_response({}, 401, "Password is incorrect")
    else:
      return create_response({}, 401, "Authentication needed")
  return authenticate

@app.route('/', methods=['GET'])
def getAllData():
  success = False
  data = {}
  message = ""
  (success, recipes, message) = cookbook.getAllRecipes()
  if success:
    data['recipes'] = recipes
    return create_response(data, 200, message)
  else:
    return create_response(data, 404, message)

@app.route('/recipes', methods=['GET'])
def getAllRecipes():
  success = False
  recipes = []
  message = ""
  (success, recipes, message) = cookbook.getAllRecipes()
  if success:
    return create_response(recipes, 200, message)
  else:
    return create_response(recipes, 404, message)
  
@app.route('/addrecipe', methods=['POST'])
@authentication_required
def addRecipe():
  (success, message) = cookbook.addRecipe(request.get_json())
  if success:
    return create_response({}, 201, message)
  else:
    return create_response({}, 400, message)

@app.route('/removerecipe', methods=['PUT'])
@authentication_required
def removeRecipe():
  if 'name' in request.get_json():
    (success, removedRecipe, message) = cookbook.removeRecipeByName(request.get_json()['name'])
    if success:
      return create_response(removedRecipe, 200, message)
    else:
      return create_response({}, 400, message)
  else:
    return create_response({}, 400, "Please provide name of the recipe you want to remove")

@app.route('/editrecipe', methods=['PUT'])
@authentication_required
def editRecipe():
  if 'name' not in request.get_json():
    return create_response({}, 400, "Please provide name of the recipe you want to edit")
  if 'recipe' not in request.get_json():
    return create_response({}, 400, "Please provide new information you want to edit the recipe with")
  (success, message) = cookbook.editRecipe(request.get_json()['name'], request.get_json()['recipe'])
  if success:
    return create_response({}, 200, message)
  else:
    return create_response({}, 400, message)

if __name__ == '__main__':
  app.run()