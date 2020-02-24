import pytest
from src import app

@pytest.fixture("session")
def client():
  client = app.create_app().test_client()
  yield client


