from fastapi import FastAPI, Body, Path, HTTPException, Query
from typing import Annotated


app = FastAPI()



BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

@app.get("/")
def home():
    return {"message": "Hello World. Welcome to the FastAPI Books API! go to /docs to see the API documentation."}



@app.get("/books")
async def real_all_books():
    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title: Annotated[str,Path(title="The title of the Book", example="Title One")]):
    for book in BOOKS:
        if book.get('title').casefold()==book_title.casefold():
            return book
        else:
            raise HTTPException(status_code=400, detail= "Item not found")
    
@app.get("/books/")
async def read_books_by_category(
    category: Annotated[str,Query(description= "the category of the books", openapi_examples="science")]):
    list_of_books = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            list_of_books.append(book)
    return list_of_books


@app.get("/books/author/{by_author}")
async def read_books_by_author_and_category(
    by_author:Annotated[str, Path(description="search book by author and category")],
    category: Annotated[str|None, Query(max_length=10)]=None  
):
    list_of_books=[]
    if category:
        for book in BOOKS:
            if book.get("category").casefold()==category.casefold() and \
                book.get("author").casefold()==by_author.casefold():
                list_of_books.append(book)
    else:
        for book in BOOKS:
            if book.get("author").casefold()==by_author.casefold():
                list_of_books.append(book)
    
    if not list_of_books:
        raise HTTPException(status_code=400, detail= "Item not found")    
    
    return list_of_books  


@app.post("/books/create_books")

async def creat_books(new_book:Annotated[dict,Body(description="request Body")]):
    BOOKS.append(new_book)
    return BOOKS


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
    
    
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: Annotated[str, Path(description="the books to delete")]):
    for book in BOOKS:
        if book.get("title").casefold()==book_title.casefold():
            BOOKS.remove(book)
    return BOOKS
        
                
            
        