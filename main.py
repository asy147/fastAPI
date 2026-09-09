from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Gauge, REGISTRY, generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from fastapi.responses import Response
import time

app = FastAPI()
task_id = 1

# Define prometheus metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])


tasks_total = Gauge('tasks_total', 'Total tasks', registry=REGISTRY)
tasks_completed = Gauge('tasks_completed', 'Completed tasks', registry=REGISTRY)
tasks_pending = Gauge('tasks_pending', 'Pending tasks', registry=REGISTRY)


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

@app.get("/tasks/metrics")
def task_metrics():
    tasks_total.set(100)
    tasks_completed.set(65)
    tasks_pending.set(35)
    return {
        "total": 100,
        "completed": 65,
        "pending": 35
    }

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return {"error": "Task not found"}

@app.get("/tasks")
def get_tasks():
    return tasks

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