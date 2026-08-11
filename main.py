from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
task_id = 1

class Task(BaseModel):
    title: str
    description: str = "some description"

tasks = []

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