from fastapi import FastAPI
from TodoApp.models import Users, Todos
from sqlmodel import Field, Session, SQLModel
from TodoApp.routers import auth,users,todos,admin
from TodoApp.database import engine

app = FastAPI()

SQLModel.metadata.create_all(engine)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)