from typing import Optional, Annotated
from fastapi import FastAPI, Path, Query, HTTPException, Body
from pydantic import BaseModel, Field
from starlette import status
from pydantic import AfterValidator
import random

app= FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: int|None = Field(description=" Id is not needed on create", default=None)
    title: str =Field(min_length=3)
    author : str = Field(min_length=1)
    description :str= Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=2020, lt=2031)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title":"The Hobbit",
                    "author": "J. R. R. Tolkien",
                    "description": "A very nice Book to read",
                    "rating": 5,
                    "published_date": 2021
                }
            ]
        }
    }
    

    
BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


@app.get("/books", status_code=status.HTTP_200_OK)
def show_the_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def  show_book_by_id(
    book_id:Annotated[int, Path(gt=0, description="id must be int and >0")]
    ):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=400, detail="Item not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def  show_book_by_rating(
    rating:Annotated[int, Query(gt=0, lt=6,description="rating is betwen 0 to 5")]
    ):
    books_to_return =[]
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    if not books_to_return:
        raise HTTPException(status_code=400, detail="Item not found")
    return books_to_return

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def show_books_by_publish_date(published_date:Annotated[int, Query(gt=1999, lt=2031)]):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


def assign_new_book_id(new_book:Book):
    existing_ids=[book.id for book in BOOKS]
    while new_book.id in existing_ids:
        new_book.id=random.randint(1,100)
    return new_book
        
        
        

@app.post("/create-book", status_code= status.HTTP_201_CREATED)
def create_book(book_request:BookRequest):
    new_book= Book(**book_request.model_dump())
    new_book=assign_new_book_id(new_book)
    BOOKS.append(new_book)
    return BOOKS

@app.put("/books/update-book", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def update_book(book:BookRequest):
    book_chaged= False
    for i in range(len(BOOKS)):
        if BOOKS[i].id==book.id:
            BOOKS[i]= Book(**book.model_dump())
            book_chaged= True
    if not book_chaged:
        raise HTTPException(status_code=404, detail="Item doen't exist")
    return BOOKS

# @app.delete("/book/delete", status_code=status.HTTP_204_NO_CONTENT)
# def delete_book(request_book:BookRequest):
#     for book in BOOKS:
#         if book.id==request_book.id:
#             BOOKS.remove(book)
#             return
#     raise HTTPException(status_code=404, detail="No Book found")
            
        
@app.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id:Annotated[int, Path(description="the id need to provided")]):
    for book in BOOKS:
        if book.id==book_id:
            BOOKS.remove(book)
            return 
    raise HTTPException(status_code=404, detail="No Book found")

    




