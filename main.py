from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

app = FastAPI()
task_id = 1

# Define prometheus metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])



class Task(BaseModel):
    title: str
    description: str = "some description"

tasks = []

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
    global task_id
    new_task = {"id": task_id, **task.dict()}
    tasks.append(new_task)
    task_id += 1
    return new_task

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return {"error": "Task not found"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks[i] = {"id": task_id, **task.dict()}
            return tasks[i]
    return {"error": "Task not found"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return {"message": "Task deleted"}
    return {"error": "Task not found"}


# Expose metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)