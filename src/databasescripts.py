import mysql.connector
from passlib.apps import custom_app_context as pwManager

def initiateDatabase(cursor):
  ''' Creates all tables needed for the cookbook
  '''
  # Creates the recipes table containing the recipe name, recipe description, and number of servings
  cursor.execute("CREATE TABLE recipes (recipe_name VARCHAR(255), recipe_description TEXT, servings INT, PRIMARY KEY(recipe_name))")

  # Creates the recipes_ingredients table linking the number of units of ingredients to each recipe
  # Note that the key pair recipe_id and ingredient is NOT unique which means a recipe can have several instances of the same ingredient
  # Amount is chosen to be VARCHAR as one can have 1/2 or "a million" as value there.
  cursor.execute("CREATE TABLE recipes_ingredients (recipe_name VARCHAR(255), ingredient VARCHAR(255), unit VARCHAR(255), amount VARCHAR(255), FOREIGN KEY (recipe_name) REFERENCES recipes(recipe_name))")

  # Creates the recipes_instructions table linking the instructions and step to each recipe
  cursor.execute("CREATE TABLE recipes_instructions (recipe_name VARCHAR(255), step INT, instruction TEXT, FOREIGN KEY (recipe_name) REFERENCES recipes(recipe_name), UNIQUE KEY recipe_to_step (recipe_name, step))")

  #Creates the passwords table that shall store the passwords
  cursor.execute("CREATE TABLE passwords (password_hash CHAR(77) UNIQUE)")

def resetDatabase(cursor):
  ''' Resets the database removing all recipes, ingredients, passwords
  '''
  # Disable check for foreign keys as resetting recipes_ingredients wont go through otherwise
  cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
  cursor.execute("TRUNCATE recipes_ingredients")
  cursor.execute("TRUNCATE recipes")
  cursor.execute("TRUNCATE recipes_instructions")
  cursor.execute("TRUNCATE passwords")
  cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def resetRecipesOnly(cursor):
  ''' Resets only the recipes, recipes_ingredients, and recipes_instructions table. Keep the information in passwords
  '''
  # Disable check for foreign keys as resetting recipes_ingredients wont go through otherwise
  cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
  cursor.execute("TRUNCATE recipes")
  cursor.execute("TRUNCATE recipes_ingredients")
  cursor.execute("TRUNCATE recipes_instructions")
  cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def addPassword(cursor, password):
  ''' Adds a password to the database
  '''
  sql = "INSERT INTO passwords (password_hash) VALUES (%s)"
  val = (pwManager.hash(password),)
  cursor.execute(sql, val)

if __name__ == "__main__":
  ''' This script is only run manually. Choose the function from above.
  '''
  db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "Aweki2235zxc",
    database = "testcookbook"
    )
  cursor = db.cursor()

  resetRecipesOnly(cursor)
  '''
  cursor.execute("SHOW TABLES")
  
  data = cursor.fetchall()
  print(data)
  '''

  db.commit()
  cursor.close()
  db.close()
