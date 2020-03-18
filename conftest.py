import pytest
import sys
sys.path.append('./src')
import app

@pytest.fixture("session")
def client():
  client = app.create_app("Testing").test_client()
  yield client


