import pytest
import os, sys
os.path.abspath('..')
from app import app

@pytest.fixture("session")
def client():
  client = app.test_client()
  yield client


