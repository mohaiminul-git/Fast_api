from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from pydantic import BaseModel
from TodoApp.database import SessionDep
from .auth import get_current_user
from TodoApp.models import Todos, Users
from sqlmodel import Field, select
from pwdlib import PasswordHash


router = APIRouter(
    prefix="/user",
    tags=["user"]       
)

user_dependency = Annotated[dict, Depends(get_current_user)]
password_hash= PasswordHash.recommended()

class User_verification(BaseModel):
    password:str
    new_password:str= Field(min_length=6, max_length=20)
    
    
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency, db:SessionDep):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    statement= select(Users).where(Users.id==user.get("id"))
    user_model= db.exec(statement).first()
    return user_model
    
  
    
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency, db:SessionDep,
                          user_verification:User_verification):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication failed")
    statement= select(Users).where(Users.id==user.get("id"))
    user_model= db.exec(statement).first()
    if not password_hash.verify(user_verification.password, user_model.hashed_password):
       raise HTTPException(status_code=401, detail="Error on passwowd change")
    user_model.hashed_password=password_hash.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    