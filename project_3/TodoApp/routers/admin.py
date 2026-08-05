from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from TodoApp.database import SessionDep
from .auth import get_current_user
from TodoApp.models import Todos
from sqlmodel import select


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(
    user: user_dependency,
    db: SessionDep
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Authentication Failed"
        )

    return db.exec(select(Todos)).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: SessionDep,
    todo_id: Annotated[int, Path(gt=0)]
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Authentication Failed"
        )

    statement = select(Todos).where(Todos.id == todo_id)
    todo_model = db.exec(statement).first()

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found."
        )

    db.delete(todo_model)
    db.commit()