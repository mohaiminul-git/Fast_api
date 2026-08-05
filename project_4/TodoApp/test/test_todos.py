from .utils import *
from ..database import get_session
from ..routers.auth import authenticate_user, get_current_user, create_access_token, SECRET_KEY, ALGORITHM
from ..models import Todos
from sqlmodel import Session,select
from datetime import timedelta
import jwt
import pytest
from fastapi import status


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_currenr_user

def test_read_todo(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
    "id": 1,
    "priority": 1,
    "owner_id": 1,
    "complete": False,
    "title": "learn to code!",
    "description": "Need to finish fast api"
}
    ]
    

def test_read_todo_by_id(test_todo):
    response= client.get("/todo/1")
    assert response.status_code==status.HTTP_200_OK
    assert response.json() ==  {
    "id": 1,
    "priority": 1,
    "owner_id": 1,
    "complete": False,
    "title": "learn to code!",
    "description": "Need to finish fast api"
}
    

def test_read_one_authenticated_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 400
    assert response.json() == {'detail': "Authentication Error"}
    
    
def test_create_todo(test_todo):
    request_data={
        'title': 'New Todo!',
        'description':'New todo description',
        'priority': 5,
        'complete': False,
    }

    response= client.post("/todo", json=request_data)
    assert response.status_code == 201
    with Session(engine) as db:
        model = db.exec(select(Todos).where(Todos.id == 2)).first()
    
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

        
def test_update_todo(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204
    with Session(engine) as db:
        model = db.exec(select(Todos).where(Todos.id == 1)).first()
        
    assert model.title == 'Change the title of the todo already saved!'
    
def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    with Session(engine) as db:
        model = db.exec(select(Todos).where(Todos.id == 1)).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}

