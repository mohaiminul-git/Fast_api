from .utils import *
from ..database import get_session
from ..routers.auth import authenticate_user, get_current_user, create_access_token, SECRET_KEY, ALGORITHM
from ..models import Todos
from sqlmodel import Session,select
from datetime import timedelta
import pytest
from fastapi import status







app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_currenr_user


def test_read_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('username') == 'fastapi coding'
    assert response.json().get('email') == "techrandom@gmail.com"
    assert response.json().get('first_name') == "tech"
    assert response.json().get('last_name') == "random"
    assert response.json().get('phone_number') == "+4917687807049"
    
def test_change_passwoord(test_user):
    request_data={
        'password': 'testpassword',
        'new_password':'newpassword'
    }
    response= client.put("/user/password", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with Session(engine) as db:
        model = db.exec(select(Users).where(Users.id == 1)).first()
        assert password_hash.verify("newpassword", model.hashed_password)
        
        
def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={"password": "wrong_password",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on passwowd change'} 