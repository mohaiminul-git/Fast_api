from sqlmodel import Field, Session, SQLModel, create_engine, select
from ..models import Todos, Users
from ..main import app
import pytest
from fastapi.testclient import TestClient
from ..routers.auth import password_hash





sqlite_url= "sqlite:///./test.db"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SQLModel.metadata.create_all(engine)


def override_get_session():
    with Session(engine) as session:
        yield session
        

def override_get_currenr_user():
    return{'username':'codingwithsqlmodel','id':1,'role':'admin'}


client=TestClient(app)

@pytest.fixture
def test_todo():
    todo= Todos(
        title="learn to code!",
        description="Need to finish fast api",
        priority=1,
        complete=False,
        owner_id=1
    )
    with Session(engine) as session:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        
    yield todo
    
    with Session(engine) as session:
        todos= session.exec(select(Todos)).all()
        
        for todo in todos:
            session.delete(todo)
        session.commit()
        
        
@pytest.fixture
def test_user():
    user= Users(
        username="fastapi coding",
        email="techrandom@gmail.com",
        first_name="tech",
        last_name="random",
        hashed_password=password_hash.hash("testpassword"),
        role= "admin",
        phone_number="+4917687807049"
    )
    
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        
    yield user
    
    with Session(engine) as session:
        users= session.exec(select(Users)).all()
        
        for user in users:
            session.delete(user)
            
        session.commit()
            
            
        