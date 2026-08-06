from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from TodoApp.models import Users, Todos
from sqlmodel import Field, Session, SQLModel
from TodoApp.routers import auth,users,todos,admin
from TodoApp.database import engine

app = FastAPI()

SQLModel.metadata.create_all(engine)


app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)




@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)