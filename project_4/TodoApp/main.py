from fastapi import FastAPI
from TodoApp.models import Users, Todos
from sqlmodel import Field, Session, SQLModel
from TodoApp.routers import auth,users,todos,admin
from TodoApp.database import engine

app = FastAPI()

SQLModel.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Hello. Welcome to the FastAPI TodoApp! go to /docs to see the API documentation."}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)