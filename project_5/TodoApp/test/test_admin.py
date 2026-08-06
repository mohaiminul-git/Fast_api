from .utils import *
from ..database import get_session
from ..routers.auth import get_current_user
from ..models import Todos
from ..main import app

app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_todos(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": test_todo.id,
            "title": test_todo.title,
            "description": test_todo.description,
            "priority": test_todo.priority,
            "complete": test_todo.complete,
            "owner_id": test_todo.owner_id
        }
    ]
    
def test_delete_todo(test_todo):
    response = client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code == 204
    
    with Session(engine) as session:
        todo = session.get(Todos, test_todo.id)
        assert todo is None

def test_delete_todo_not_found():
    response = client.delete("/admin/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}