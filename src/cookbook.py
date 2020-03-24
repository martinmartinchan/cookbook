import json
import mysql.connector
from passlib.apps import custom_app_context as pwManager
from functools import wraps

def connection_needed(f):
  ''' Decorator function for all function that connects to the database.
  '''
  @wraps(f)
  def dbConnect(*args, **kwargs):
    config = args[0].config #Get the current config
    db = mysql.connector.connect(
      host = config["HOST"],
      user = config["USER"],
      passwd = config["PASSWORD"],
      database = config["DATABASE"]
    )
    cursor = db.cursor()
    try:
      fReturn = f(*args, cursor)
      db.commit()
    finally:
      cursor.close()
      db.close()
    return fReturn
  return dbConnect

class Cookbook():
  def __init__(self, config):
    self.config = config

  @connection_needed
  def authenticate(self, password, cursor):
    ''' Checks whether the password provided is valid or not.
    '''
    cursor.execute("SELECT * FROM passwords")
    for dbPassword in cursor.fetchall():
      if pwManager.verify(password, dbPassword[0]):
        return True
    return False

  def checkRecipeValidity(self, recipe):
    ''' Checks whether a given recipe contains a name, description, ingredient list, and servings.
    '''
    return all (keys in recipe for keys in ("name", "description", "ingredients", "servings", "instructions"))

  @connection_needed
  def checkRecipeNameExists(self, recipeName, cursor):
    ''' Checks whether a recipe name exists in the cookbook
    '''
    cursor.execute("SELECT recipe_name FROM recipes")
    result = cursor.fetchall()
    for name in result:
      if recipeName.lower() == name[0].lower():
        return True
    return False
    
  def checkIngredientValidity(self, ingredient):
    ''' Checks whether a given ingredient contains a name, unit, and amount.
    '''
    return all (keys in ingredient for keys in ("name", "unit", "amount"))

  @connection_needed
  def addRecipe(self, recipe, cursor):
    ''' Adds a recipe to the cookbook.
        Returns True if it was successully inserted, else False.
        Returns a message that describes what has happened.
    '''
    if not self.checkRecipeValidity(recipe):
      return (False, "Recipe must contain name, description, number of servings, ingredient list, and instructions")
    
    #Try to insert values into the recipes table
    recipeName = recipe['name']
    if self.checkRecipeNameExists(recipeName):
      return (False, "Recipe with name " + recipeName + " already exists")

    description = recipe['description']
    servings = recipe['servings']

    #Then try to insert the recipe, ingredients and instructions into the tables
    try:
      cursor.execute("INSERT INTO recipes (recipe_name, recipe_description, servings) VALUES (%s, %s, %s)", (recipeName, description, servings))
      ingredients = []
      for ing in recipe['ingredients']:
        ingredients.append((recipeName, ing['name'], ing['unit'], ing['amount']))
      cursor.executemany("INSERT INTO recipes_ingredients (recipe_name, ingredient, unit, amount) VALUES (%s, %s, %s, %s)", (ingredients))
      instructions = []
      for instruction in recipe['instructions']:
        instructions.append((recipeName, instruction['step'], instruction['instruction']))
      cursor.executemany("INSERT INTO recipes_instructions (recipe_name, step, instruction) VALUES (%s, %s, %s)", (instructions))
      return (True, "Successfully added " + recipeName + " into the cookbook.")
    except:
      return (False, "Something went wrong. Could not insert recipe into cookbook.")

  @connection_needed
  def removeRecipeByName(self, recipeName, cursor):
    ''' Removes a recipe given the name of the recipe.
        Returns True if recipe was successfully removed, else False.
        Returns the removed recipe as a dict if it was removed, else an empty dict.
        Returns a message describing what has happened.
    '''
    recipeExists = self.checkRecipeNameExists(recipeName)
    if recipeExists:
      try:
        #Must delete ingredients and instructions first as they rely on recipes table with foreign key
        cursor.execute("DELETE FROM recipes_ingredients WHERE recipe_name = \'" + recipeName + "\'")
        cursor.execute("DELETE FROM recipes_instructions WHERE recipe_name = \'" + recipeName + "\'")
        cursor.execute("DELETE FROM recipes WHERE recipe_name = \'" + recipeName + "\'")
        return (True, "Succesfully removed " + recipeName + " from the cookbook.")
      except:
        return(False, "An error occured. Could not remove " + recipeName + " from the cookbook.")
    else:
      return (False, "Recipe with name " + recipeName + " does not exist in the cookbook.")

  @connection_needed
  def getRecipeByName(self, recipeName, cursor):
    ''' Searches for a recipe in the cookbook given the recipe name.
        Returns True if at least one recipe was found, else False
        Returns the recipe as a dict if found, else an empty dict is returned.
        Returns a message describing what has happened
    '''
    if self.checkRecipeNameExists(recipeName):
      try:
        #Fetch everything from the recipes, recipe_ingredients, recipe_instructions tables with recipe name matching the input parameter
        cursor.execute("SELECT recipe_name, recipe_description, servings FROM recipes WHERE recipe_name = \'" + recipeName + "\'")
        recipesResult = cursor.fetchall()[0]
        cursor.execute("SELECT ingredient, unit, amount FROM recipes_ingredients WHERE recipe_name = \'" + recipeName + "\'")
        ingredientsResult = cursor.fetchall()
        cursor.execute("SELECT step, instruction FROM recipes_instructions WHERE recipe_name = \'" + recipeName + "\' ORDER BY step ASC")
        instructionsResult = cursor.fetchall()

        #Build the recipe to return
        recipe = {}
        recipe['name'] = recipesResult[0]
        recipe['description'] = recipesResult[1]
        recipe['servings'] = recipesResult[2]
        recipe['ingredients'] = []
        recipe['instructions'] = []

        for ing in ingredientsResult:
          newIngredient = {
            'name': ing[0],
            'unit': ing[1],
            'amount': ing[2]
          }
          recipe['ingredients'].append(newIngredient)

        for inst in instructionsResult:
          newInstruction = {
            'step': inst[0],
            'instruction': inst[1]
          }
          recipe['instructions'].append(newInstruction)
        
        return(True, recipe, "Successfully retrieved recipe with name " + recipeName + " from the cookbook.")
      except:
        return(False, {}, "Could not connect to the database.")
    else:
      return (False, {}, "Could not found recipe with name " + recipeName + " in the cookbook.")
    

  @connection_needed
  def getAllRecipes(self, cursor):
    ''' Gets all the recipe in the cookbook.
        Returns True if at least one recipe was found, else False
        Returns an array containing all recipes (This is empty is none was found)
        Returns a message describing what has happened
    '''
    try:
      #Fetch everything from the recipes, recipe_ingredients, recipe_instructions tables
      cursor.execute("SELECT recipe_name, recipe_description, servings FROM recipes")
      recipesResult = cursor.fetchall()
      cursor.execute("SELECT recipe_name, ingredient, unit, amount FROM recipes_ingredients")
      ingredientsResult = cursor.fetchall()
      cursor.execute("SELECT recipe_name, step, instruction FROM recipes_instructions ORDER BY step ASC")
      instructionsResult = cursor.fetchall()

      #Initiate recipes as a dict to store the recipes
      recipesDict = {}

      #Create the recipes in the dictionary using recipesResult with tuples = (recipe_name, recipe_description, servings)
      for recipe in recipesResult:
        newRecipe = {}
        newRecipe['name'] = recipe[0]
        newRecipe['description'] = recipe[1]
        newRecipe['servings'] = recipe[2]
        newRecipe['ingredients'] = []
        newRecipe['instructions'] = []
        recipesDict[newRecipe['name']] = newRecipe
      
      #Input the ingredients to the recipes using ingredientsResult with tuples (recipe_name, ingredient, unit, amount)
      for ing in ingredientsResult:
        newIngredient = {
          'name': ing[1],
          'unit': ing[2],
          'amount': ing[3]
        }
        recipesDict[ing[0]]['ingredients'].append(newIngredient)

      #Input the instructions to the recipes using instructionsResult with tuples (recipe_name, step, instruction)
      for inst in instructionsResult:
        newInstruction = {
          'step': inst[1],
          'instruction': inst[2]
        }
        recipesDict[ing[0]]['instructions'].append(newInstruction)
      
      #Convert the recipes struct to a list
      recipes = []
      for recipe in recipesDict:
        recipes.append(recipesDict[recipe])
      
      if len(recipes):
        return (True, recipes, "Successfully retrieved all recipes.")
      else:
        return(False, [], "There are no recipes in the cookbook.")
    except:
      return(False, [], "Could not connect to the database.")

  @connection_needed
  def editRecipe(self, oldRecipeName, newRecipe, cursor):
    ''' Overwrites all the information in a recipe given the recipe name
        Returns True if the recipe was edited, else False
        Returns what has happened during the editing of the recipe
    '''
    if not self.checkRecipeNameExists(oldRecipeName):
      return (False, "Recipe with name " + oldRecipeName + " does not exist in the cookbook.")
    
    if not self.checkRecipeValidity(newRecipe):
      return (False, "Recipe must contain name, description, number of servings, ingredient list, and instructions.")

    if (newRecipe['name'].lower() != oldRecipeName.lower()) and (self.checkRecipeNameExists(newRecipe['name'])):
      return (False, "The edited recipe name already exists in the cookbook.")
    
    (success, messageRemoveOld) = self.removeRecipeByName(oldRecipeName)
    if success:
      (successAddNew, messageAddNew) = self.addRecipe(newRecipe)
      if successAddNew:
        return (True, "Succesfully updated recipe")
      else:
        #This should never happen.
        return (False, "Something went terribly wrong. Could not edit the recipe and it was instead removed...")
    else:
      return (False, "Could not edit the recipe you are looking for. Message: " + messageRemoveOld)
