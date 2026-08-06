from .utils import *
from ..database import get_session
from ..routers.auth import authenticate_user, get_current_user, create_access_token, SECRET_KEY, ALGORITHM
from ..models import Todos
from ..main import app
from sqlmodel import Session
from datetime import timedelta
import jwt
import pytest


app.dependency_overrides[get_session] = override_get_session
#app.dependency_overrides[get_current_user] = override_get_currenr_user

def test_authenticate_user(test_user):
    with Session(engine) as session:
        user= authenticate_user(test_user.username,"testpassword", session)
    assert user is not None
    assert user.username == test_user.username
    
    no_existing_user= authenticate_user("non_existing_user", "password", session)
    assert no_existing_user is False    
    
    wrong_password= authenticate_user(test_user.username, "wrong_password", session)
    assert wrong_password is False
    
def test_create_access_token(test_user):
    expires_delta= timedelta(minutes=15)
    access_token= create_access_token(test_user.username, test_user.id, test_user.role, expires_delta)
    
    payload= jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    username= payload.get("sub")
    user_id= payload.get("id")
    role= payload.get("role")
    
    assert username == test_user.username
    assert user_id == test_user.id
    assert role == test_user.role
    
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode= {"sub":"codingwithsqlmodel", "id":1, "role":"admin"}
    token= jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user= await get_current_user(token)
    assert user is not None 
    assert user== {'username':'codingwithsqlmodel','id':1,'role':'admin'}
    
    
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode={"role": "admin"}
    token= jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(Exception) as exc_info:
        await get_current_user(token)
    assert str(exc_info.value.detail) == "Could not validate credentials"   