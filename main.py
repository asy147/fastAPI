from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Gauge, REGISTRY, generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from fastapi.responses import Response
import time
from uuid import uuid4
import boto3
import os
from botocore.exceptions import ClientError
from contextlib import asynccontextmanager

dynamodb = None
table = None

def create_table():
    global dynamodb, table
    
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")  # None in real AWS
    
    dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name="us-east-1")
    
    try:
        table = dynamodb.create_table(
            TableName="tasks",
            KeySchema=[{"AttributeName": "task_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "task_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            table = dynamodb.Table("tasks")
        else:
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once at startup
    create_table()
    yield
    # runs once at shutdown (optional cleanup)

app = FastAPI(lifespan=lifespan)


# Define prometheus metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])


tasks_total = Gauge('tasks_total', 'Total tasks', registry=REGISTRY)
tasks_completed = Gauge('tasks_completed', 'Completed tasks', registry=REGISTRY)
tasks_pending = Gauge('tasks_pending', 'Pending tasks', registry=REGISTRY)


class Task(BaseModel):
    title: str
    description: str = "some description"
    completed: bool = False

# Add middleware to track metrics
@app.middleware("http")
async def track_metrics(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    request_count.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    request_duration.labels(method=request.method, endpoint=request.url.path).observe(duration)
    
    return response

@app.post("/tasks")
def create_task(task: Task):
    new_task = {"task_id": str(uuid4()), **task.model_dump()}
    table.put_item(Item=new_task)
    return new_task

@app.get("/tasks/metrics")
def task_metrics():
    response = table.scan()
    items = response["Items"]
    total = len(items)
    completed = len([t for t in items if t.get("completed")])
    pending = total - completed
    
    tasks_total.set(total)
    tasks_completed.set(completed)
    tasks_pending.set(pending)
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    response = table.get_item(Key={"task_id": task_id})
    if "Item" not in response:
        return {"error": "Task not found"}
    return response["Item"]

@app.get("/tasks")
def get_tasks():
    response = table.scan()
    return response["Items"]

@app.get("/health")
async def health_check():
    return {"status": "looking good"}

@app.get("/debug/gauges")
def debug_gauges():
    return {
        "tasks_total": tasks_total._value.get(),
        "tasks_completed": tasks_completed._value.get(),
        "tasks_pending": tasks_pending._value.get()
    }

@app.put("/tasks/{task_id}")
def update_task(task_id: str, task: Task):
    response = table.get_item(Key={"task_id": task_id})
    if "Item" not in response:
        return {"error": "Task not found"}
    else:
        updated_task = {"task_id": task_id, **task.model_dump()}
        table.put_item(Item=updated_task)
        return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    response = table.get_item(Key={"task_id": task_id})
    if "Item" not in response:
        return {"error": "Task not found"}
    else:
        table.delete_item(Key={"task_id": task_id})
        return {"message": "Task deleted"}


# Expose metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)