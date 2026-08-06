from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from TodoApp.database import SessionDep
from .auth import get_current_user
from TodoApp.models import Todos
from sqlmodel import Field, select



router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str=Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int =Field(gt=0, lt=6)
    complete: bool 


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db:SessionDep):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    return db.exec(select(Todos).where(Todos.owner_id==user.get("id"))).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency, db:SessionDep, todo_id:Annotated[int, Path(gt=0)]):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication failed")
    statement= (
        select(Todos).where(Todos.id==todo_id)
        .where(Todos.owner_id==user.get("id")) 
        )
    todo_model= db.exec(statement).first()
    if todo_model is None:
        raise(HTTPException(status_code=400, detail="Authentication Error"))
    return todo_model

@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def creat_todo(
    user:user_dependency,
    db:SessionDep,
    todo_request:TodoRequest
    ):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication Error")
    todo_model=Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user:user_dependency,
    db:SessionDep,
    todo_request:TodoRequest,
    todo_id:Annotated[int, Path(gt=0)]
):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication Error")
    statement= (
        select(Todos)
        .where(Todos.id==todo_id)
        .where(Todos.owner_id==user.get("id"))
    )
    todo_model= db.exec(statement).first()
    todo_model.title=todo_request.title
    todo_model.description=todo_request.description
    todo_model.priority=todo_request.priority
    todo_model.complete=todo_request.complete
    db.add(todo_model)
    db.commit()
    
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user:user_dependency,
    db:SessionDep,
    todo_id:Annotated[int, Path(gt=0)]
):
    if user is None:
        raise HTTPException(status_code=400, detail="Authentication Error")
    statement= (
        select(Todos)
        .where(Todos.id==todo_id)
        .where(Todos.owner_id==user.get("id"))
    )
    todo_model= db.exec(statement).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
    
        
    
    
    