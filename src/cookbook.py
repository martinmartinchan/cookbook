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
    print(config)
    cursor = db.cursor()
    fReturn = f(*args, cursor)
    db.commit()
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

  def addIngredient(self, cursor, name):
    ''' Adds an ingredient to the ingredients table. Dont check if it is duplicated. It does not matter.
        Called by addRecipe.
    '''
    sql = "INSERT INTO ingredients (ingredient_name) VALUES (%s)"
    val = (name,)
    try:
      cursor.execute(sql, val)
    except:
      #Do nothing if it fails (probably due to duplicate entries)
      return

  def addUnit(self, cursor, name):
    ''' Adds a unit to the units table. Dont check if it is duplicated. It does not matter.
    Called by addRecipe.
    '''
    sql = "INSERT INTO units (unit_name) VALUES (%s)"
    val = (name,)
    try:
      cursor.execute(sql, val)
    except:
      #Do nothing if it fails (probably due to duplicate entries)
      return

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
    #First make sure the ingredients exists in the tables (Doesn't matter if this goes wrong)
    for ing in recipe['ingredients']:
      if not self.checkIngredientValidity(ing):
        return (False, "Ingredients must contain name, unit, and amount")
      self.addIngredient(cursor, ing['name'])
      self.addUnit(cursor, ing['unit'])
    #Then try to insert the recipe and ingredients into the tables
    try:
      cursor.execute("INSERT INTO recipes (recipe_name, recipe_description, servings) VALUES (%s, %s, %s)", (recipeName, description, servings))
      recipeID = cursor.lastrowid
      ingredients = []
      for ing in recipe['ingredients']:
        ingredients.append((recipeID, ing['name'], ing['unit'], ing['amount']))
      cursor.executemany("INSERT INTO recipes_ingredients (recipe_id, ingredient_name, unit_name, amount) VALUES (%s, %s, %s, %s)", (ingredients))
      instructions = []
      for instruction in recipe['instructions']:
        instructions.append((recipeID, instruction['step'], instruction['instruction']))
      cursor.executemany("INSERT INTO recipes_instructions (recipe_id, step, instruction) VALUES (%s, %s, %s)", (instructions))
      return (True, "Successfully added " + recipeName + " into the cookbook")
    except:
      return (False, "Something went wrong. Could not insert recipe into cookbook")

  @connection_needed
  def removeRecipeByName(self, recipeName, cursor):
    ''' Removes a recipe given the name of the recipe.
        Returns True if recipe was successfully removed, else False.
        Returns the removed recipe as a dict if it was removed, else an empty dict.
        Returns a message describing what has happened.
    '''
    removedRecipe = self.getRecipeByName(recipeName)
    if removedRecipe:
      cursor.execute("SELECT recipe_id FROM recipes WHERE recipe_name = \'" + recipeName + "\'")
      recipeID = cursor.fetchall()[0][0]
      try:
        #Must delete ingredients and instructions first as they rely on recipes table with foreign key
        cursor.execute("DELETE FROM recipes_ingredients WHERE recipe_id = " + str(recipeID))
        cursor.execute("DELETE FROM recipes_instructions WHERE recipe_id = " + str(recipeID))
        cursor.execute("DELETE FROM recipes WHERE recipe_id = " + str(recipeID))
        return (True, removedRecipe, "Succesfully removed " + recipeName + " from the cookbook")
      except:
        return(False, {}, "An error occured. Could not remove " + recipeName + " from the cookbook")
    else:
      return (False, {}, "Recipe with name " + recipeName + " does not exist in the cookbook")

  @connection_needed
  def getRecipeByName(self, recipeName, cursor):
    ''' Searches for a recipe in the cookbook given the recipe name.
        Returns the recipe as a dict if found, else an empty dict is returned.
    '''
    cursor.execute("SELECT recipe_description, servings, ingredient_name, unit_name, amount  FROM recipes_ingredients INNER JOIN recipes ON recipes_ingredients.recipe_id = recipes.recipe_id WHERE recipe_name = \'" + recipeName + "\'")
    result = cursor.fetchall()
    if len(result): #Recipe found
      description = result[0][0]
      servings = result[0][1]
      recipe = {
        'name': recipeName,
        'description': description,
        'servings': servings
        }
      ingredientList = []
      for ing in result:
        ingredientList.append({"name": ing[2], "unit": ing[3], "amount": ing[4]})
      recipe['ingredients'] = ingredientList

      #Retrieve the instructions 
      cursor.execute("SELECT step, instruction FROM recipes_instructions INNER JOIN recipes ON recipes_instructions.recipe_id = recipes.recipe_id WHERE recipe_name = \'" + recipeName + "\'")
      result = cursor.fetchall()
      instructionList = []
      for instruction in result:
        instructionList.append({"step": instruction[0], "instruction": instruction[1]})
      recipe['instructions'] = instructionList
      return recipe
    else:
      return {}

  @connection_needed
  def getAllRecipes(self, cursor):
    ''' Gets all the recipe in the cookbook.
        Returns True if at least one recipe was found, else False
        Returns an array containing all recipes (This is empty is none was found)
        Returns a message describing what has happened
    '''
    cursor.execute("SELECT * FROM recipes")
    result = cursor.fetchall()
    if len(result):
      recipes = []
      for recipe in result:
        recipes.append(self.getRecipeByName(recipe[1]))
      return (True, recipes, "Successfully retrieved all recipes.")
    else:
      return(False, [], "There are no recipes in the cookbook.")

  @connection_needed
  def editRecipe(self, oldRecipeName, newRecipe, cursor):
    ''' Overwrites all the information in a recipe given the recipe name
        Returns True if the recipe was edited, else False
        Returns what has happened during the editing of the recipe
    '''
    if not self.checkRecipeNameExists(oldRecipeName):
      return (False, "Recipe with name " + oldRecipeName + " does not exist in the cookbook")
    
    if not self.checkRecipeValidity(newRecipe):
      return (False, "Recipe must contain name, description, number of servings, ingredient list, and instructions")

    if (newRecipe['name'].lower() != oldRecipeName.lower()) and (checkRecipeNameExists(newRecipe['name'])):
      return (False, "The edited recipe name already exists in the cookbook")
    
    (success, removedRecipe, messageRemoveOld) = self.removeRecipeByName(oldRecipeName)
    if success:
      (successAddNew, messageAddNew) = self.addRecipe(newRecipe)
      if successAddNew:
        return (True, "Succesfully updated recipe")
      else:
        (successAddOld, messageAddOld) = self.addRecipe(removedRecipe)
        if successAddOld:
          return (False, "The new information in the new recipe is not good. See following message: " + messageAddNew)
        else:
          #This is when the old recipe is removed, and new couldn't be added and then old couldnt be added either. Critical error. Should never happen
          return (False, "Something went terribly wrong. Could not edit the recipe and it was instead removed... Message: " + messageAddOld)
    else:
      return (False, "Could edit the recipe you are looking for. Message: " + messageRemoveOld)
