import mysql.connector
from passlib.apps import custom_app_context as pwManager

def initiateDatabase():
  ''' Creates all tables needed for the cookbook
  '''
  db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "Aweki2235zxc",
    database = "cookbook"
  )
  cursor = db.cursor()

  # Creates the recipes table containing the recipe ID, recipe name, recipe description, and number of servings
  cursor.execute("CREATE TABLE recipes (recipe_id INT AUTO_INCREMENT, recipe_name VARCHAR(255), recipe_description TEXT, servings INT, PRIMARY KEY(recipe_id))")

  # Creates the ingredients table containing all the ingredient names, which are unique
  cursor.execute("CREATE TABLE ingredients (ingredient_name VARCHAR(255) UNIQUE)")

  # Creates the units table containing all the unit names, which are unique
  cursor.execute("CREATE TABLE units (unit_name VARCHAR(255) UNIQUE)")

  # Creates the recipes_ingredients table linking the number of units of ingredients to each recipe
  # Note that the key pair recipe_id and ingredient_name is NOT unique which means a recipe can have several instances of the same ingredient
  cursor.execute("CREATE TABLE recipes_ingredients (recipe_id INT, ingredient_name VARCHAR(255), unit_name VARCHAR(255), amount INT, FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY (ingredient_name) REFERENCES ingredients(ingredient_name), FOREIGN KEY (unit_name) REFERENCES units(unit_name))")

  #Creates the passwords table that shall store the passwords
  cursor.execute("CREATE TABLE passwords (password_hash CHAR(77) UNIQUE)")

  cursor.close()
  db.close()

def resetDatabase():
  ''' Resets everything in the database, erasing all recipes and all ingredients and units the cookbook knows about
  '''
  db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  passwd = "Aweki2235zxc",
  database = "cookbook"
  )
  cursor = db.cursor()

  # Disable check for foreign keys as resetting recipes_ingredients wont go through otherwise
  cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

  cursor.execute("TRUNCATE recipes_ingredients")

  cursor.execute("TRUNCATE recipes")

  cursor.execute("TRUNCATE ingredients")

  cursor.execute("TRUNCATE units")

  # Enable check for foreign keys again
  cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

  cursor.close()
  db.close()

def resetRecipesOnly():
  ''' Resets only the recipes and recipes_ingredients table. Keep the information in ingredients and units table
  '''
  db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  passwd = "Aweki2235zxc",
  database = "cookbook"
  )
  cursor = db.cursor()

  # Disable check for foreign keys as resetting recipes_ingredients wont go through otherwise
  cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

  cursor.execute("TRUNCATE recipes_ingredients")

  cursor.execute("TRUNCATE recipes")

  # Enable check for foreign keys again
  cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

  cursor.close()
  db.close()

if __name__ == "__main__":
  db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  passwd = "Aweki2235zxc",
  database = "testcookbook"
  )
  cursor = db.cursor()
  
  sql = "INSERT INTO passwords (password_hash) VALUES (%s)"
  val = (pwManager.hash("Troglodon5986"),)
  cursor.execute(sql, val)

  cursor.execute("SELECT * FROM passwords")

  for row in cursor.fetchall():
    print(row)

  cursor.close()
  db.close()