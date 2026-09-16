import pytest
from fastapi.testclient import TestClient
from main import app, tasks


client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Reset app state before each test"""
    tasks.clear()
    import main
    main.task_id = 1
    yield

def test_create_task():
    response = client.post("/tasks", json={"title": "Test task"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"

def test_get_tasks():
    # Create a task first
    client.post("/tasks", json={"title": "Test task"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    print(f"Tasks in list: {data}")
    assert len(data) == 1

def test_get_single_task():
    # Create a task first, then GET it by ID
    create_response = client.post("/tasks", json={"title": "Single task"})
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single task"

def test_update_task():
    # Create, then update
    create_response = client.post("/tasks", json={"title": "Old title"})
    task_id = create_response.json()["id"]
    
    response = client.put(f"/tasks/{task_id}", json={"title": "New title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New title"

def test_delete_task():
    # Create, then delete
    create_response = client.post("/tasks", json={"title": "To delete"})
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404 or get_response.json().get("error")

def test_task_metrics():
    # Create one completed and one pending task
    client.post("/tasks", json={"title": "Done", "completed": True})
    client.post("/tasks", json={"title": "Pending", "completed": False})
    
    response = client.get("/tasks/metrics")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["pending"] == 1