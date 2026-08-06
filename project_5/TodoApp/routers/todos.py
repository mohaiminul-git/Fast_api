import token
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel
from TodoApp.database import SessionDep
from .auth import get_current_user,get_current_user_from_cookie
from TodoApp.models import Todos
from sqlmodel import Field, select
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse


templates = Jinja2Templates(directory= "./templates")



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
    
    
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: SessionDep):

    user = await get_current_user_from_cookie(request)  

    print("USER:", user)
    if user is None:
        return redirect_to_login()
    try:
        todos = db.exec(
            select(Todos).where(
                Todos.owner_id == user.get("id")
            )
        ).all()

        print("TODOS:", todos)
        return templates.TemplateResponse(
        request=request,
        name="todo.html",
        context={
        "request": request,
        "todos": todos,
        "user": user
    }
)
    except:
        return redirect_to_login()

@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user_from_cookie(request)

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(
            request=request,
            name="add-todo.html",
            context={"request": request, "user": user}
        )

    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: SessionDep):
    try:
        user = await get_current_user_from_cookie(request)

        if user is None:
            return redirect_to_login()

        todo = db.exec(select(Todos).where(Todos.id == todo_id)).first()

        return templates.TemplateResponse(
            request=request,
            name="edit-todo.html",
            context={"request": request, "user": user, "todo": todo}
        )

    except:
        return redirect_to_login()



### Endpoints ###
    
    


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
    
        
    
    
    