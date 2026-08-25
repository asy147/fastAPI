# Task Manager API

## Overview
Create an API for managing tasks. Utilize different types of API requests to read, write, delete, etc.. tasks.
Introduce Docker, Prometheus, and Grafana to a python environment in order to experiment with containerization and observability tools.

## Tech Stack
- FastAPI
- Docker
- Prometheus (metrics)
- Grafana (dashboards)
- Python 3.14

## Setup

### Local Development
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs on http://localhost:8000

### Docker
```bash
docker build -t task-manager-api .
docker run -p 8000:80 task-manager-api
```

## API Endpoints

### Create Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "From store"}'
```

### Read All Tasks
```bash
curl http://localhost:8000/tasks
```

### Read One Task
```bash
curl http://localhost:8000/tasks/1
```

### Update Task
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Run 5K", "description": "Early morning run"}'
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

## Development Notes
- Tasks are stored in-memory (no database). Data resets on server restart.
- Prometheus metrics exposed at `/metrics` endpoint.
