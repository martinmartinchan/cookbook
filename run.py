from src import app

if __name__ == '__main__':
  app = app.create_app("Development")
  app.run()