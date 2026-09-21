import pytest
import main
from main import app
from moto import mock_aws
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def client():
    with mock_aws():
        import boto3
        
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="tasks",
            KeySchema=[{"AttributeName": "task_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "task_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        main.table = table

        yield TestClient(main.app)


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test task"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"

def test_get_tasks(client):
    # Create a task first
    client.post("/tasks", json={"title": "Test task"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    print(f"Tasks in list: {data}")
    assert len(data) == 1

def test_get_single_task(client):
    # Create a task first, then GET it by ID
    create_response = client.post("/tasks", json={"title": "Single task"})
    task_id = create_response.json()["task_id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single task"

def test_update_task(client):
    # Create, then update
    create_response = client.post("/tasks", json={"title": "Old title"})
    task_id = create_response.json()["task_id"]
    
    response = client.put(f"/tasks/{task_id}", json={"title": "New title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New title"

def test_delete_task(client):
    # Create, then delete
    create_response = client.post("/tasks", json={"title": "To delete"})
    task_id = create_response.json()["task_id"]
    
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404 or get_response.json().get("error")

def test_task_metrics(client):
    # Create one completed and one pending task
    client.post("/tasks", json={"title": "Done", "completed": True})
    client.post("/tasks", json={"title": "Pending", "completed": False})
    
    response = client.get("/tasks/metrics")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["pending"] == 1