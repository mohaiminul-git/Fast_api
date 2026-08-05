from sqlmodel import Field, SQLModel


from typing import Annotated




class Users(SQLModel, table=True):
    
    id: int=Field(primary_key=True, index=True)
    email: str =Field(unique=True)
    username:str= Field(unique=True)
    first_name:str
    last_name:str
    hashed_password:str
    is_active: bool=Field(default=True)
    role:str
    


class Todos(SQLModel, table=True):

    id :int =Field(primary_key=True, index=True)
    title:str
    description:str
    priority:int
    complete:bool=Field(default=False)
    owner_id: int=Field(foreign_key="users.id")