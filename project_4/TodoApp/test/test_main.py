
from .utils import *


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello. Welcome to the FastAPI TodoApp! go to /docs to see the API documentation."}