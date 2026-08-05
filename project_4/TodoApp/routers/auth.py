from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,Body,Query
from pydantic import BaseModel
from TodoApp.database import SessionDep
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlmodel import Session, select
from TodoApp.models import Users
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import status

router= APIRouter(
    prefix="/auth",
    tags=["auth"]
)


outh2_scheme= OAuth2PasswordBearer(tokenUrl='auth/token')
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

password_hash= PasswordHash.recommended()

class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str
    phone_number:str
    
class Token(BaseModel):
    access_token:str
    token_type: str
    
def authenticate_user(user_name:str, password:str,session_db:Session):
    statement= select(Users).where(Users.username==user_name)
    user= session_db.exec(statement).first()
    if not user:
        return False
    if not password_hash.verify(password, user.hashed_password):
        return False
    return user
    
def create_access_token(username:str, user_id:int, role:str, expires_delta:timedelta):
    encode={"sub":username, "id":user_id, "role":role}
    expires= datetime.now(timezone.utc)+ expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(outh2_scheme)]):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username= payload.get("sub")
        user_id= payload.get("id")
        role= payload.get("role")
        if username ==None or user_id==None:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"})
        return{"username":username, "id":user_id, "role":role}
    except InvalidTokenError:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"})

        
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    creat_user_request:CreateUserRequest, db: SessionDep):
    create_user_model=Users(
        email=creat_user_request.email,
        username=creat_user_request.username,
        first_name=creat_user_request.first_name,
        last_name=creat_user_request.last_name,
        role=creat_user_request.role,
        hashed_password=password_hash.hash(creat_user_request.password),
        is_active=True,
        phone_number=creat_user_request.phone_number
    )
    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    
@router.post("/token",response_model=Token)
async def login_for_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  session:SessionDep
):
    user=authenticate_user(form_data.username, form_data.password, session_db=session)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token= create_access_token(user.username, user.id, user.role,expires_delta=timedelta(minutes=20))
    return{"access_token": access_token, "token_type":"bearer"}
        
 
    
    
    
    