# FastAPI + Celery + Redis + PostgreSQL Order Processing App

This project demonstrates how **FastAPI**, **Celery**, **Redis**, and **PostgreSQL** work together to process time-taking tasks in the background.

The example use case is:

```text
User creates an order
↓
FastAPI saves the order in PostgreSQL
↓
FastAPI sends a background task to Celery
↓
Celery worker processes the order
↓
Celery updates the order status in PostgreSQL
↓
Frontend checks order status from the database
```

---

# 1. Project Structure

```text
order_task_app/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── celery_app.py
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   ├── schemas/
│   │   └── order_schema.py
│   ├── tasks/
│   │   └── order_tasks.py
│   └── routers/
│       └── order_router.py
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

# 2. What Each Part Does

## `app/main.py`

This is the FastAPI application entry point.

It creates the FastAPI app, creates database tables, and includes routers.

```python
app = FastAPI(title="Order Task Management App")

app.include_router(order_router)
```

---

## `app/database.py`

This file connects SQLAlchemy with PostgreSQL.

```python
DATABASE_URL = "postgresql://appuser:apppass@localhost:5432/taskdb"
```

It creates:

```text
engine
SessionLocal
Base
```

These are used by both FastAPI and Celery to communicate with the database.

---

## `app/models/`

Models define database tables.

Example:

```text
users table
products table
orders table
```

The order table stores permanent business data:

```text
order_id
user_id
product_id
quantity
status
total_price
created_at
```

Important:

```text
PostgreSQL is the permanent business source of truth.
```

---

## `app/schemas/`

Schemas define request and response validation using Pydantic.

Example:

```python
class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
```

Schemas are used for API input/output, not database table creation.

---

## `app/routers/order_router.py`

This file contains FastAPI endpoints.

Important endpoints:

```text
POST /orders
GET /orders/{order_id}
GET /tasks/{task_id}
```

The router receives HTTP requests from the frontend/client.

---

## `app/celery_app.py`

This file creates the Celery app and connects Celery with Redis.

```python
celery_app = Celery(
    "order_task_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)
```

Meaning:

```text
Redis DB 0 = Celery broker
Redis DB 1 = Celery result backend
```

---

## `app/tasks/order_tasks.py`

This file contains background tasks.

Example:

```python
@celery_app.task(name="process_order")
def process_order(order_id: int):
    ...
```

This task is executed by the Celery worker, not directly by FastAPI.

---

# 3. Main Concept

FastAPI and Celery are separate running processes.

```text
Process 1:
FastAPI app

Process 2:
Celery worker
```

They do not share memory.

They communicate through Redis.

```text
FastAPI
↓
Redis broker
↓
Celery worker
```

---

# 4. How FastAPI Coordinates With Redis and Celery

When the user creates an order:

```text
POST /orders
```

FastAPI does this:

```text
1. Validates user and product
2. Creates order in PostgreSQL with status = pending
3. Calls process_order.delay(order.id)
4. Returns response immediately
```

The important line is:

```python
task = process_order.delay(order.id)
```

This does not directly execute `process_order`.

Instead, it means:

```text
Create a task message
↓
Send that message to Redis DB 0 broker
↓
Return a task_id immediately
```

Conceptually, Redis DB 0 stores:

```text
Task name: process_order
Arguments: order_id = 15
```

Then the Celery worker, which is already running, reads the task from Redis DB 0.

The worker executes:

```python
process_order(15)
```

Inside the task, Celery opens its own database session:

```python
db = SessionLocal()
```

Then it updates the order in PostgreSQL:

```text
pending → processing → completed
```

or:

```text
pending → processing → failed
```

After the task finishes, Celery stores the technical task result in Redis DB 1 result backend.

---

# 5. Redis DB 0 vs Redis DB 1

Even if you run only one Redis server, Redis has multiple logical databases.

```text
redis://localhost:6379/0
redis://localhost:6379/1
```

These are two logical databases inside the same Redis server.

## Redis DB 0 — Broker

Used for pending tasks.

```text
FastAPI sends task here.
Celery worker reads task from here.
```

Example:

```text
process_order(15)
```

When the worker takes the task, it is removed/reserved from the broker queue.

---

## Redis DB 1 — Result Backend

Used for technical Celery task results.

Example:

```text
task_id = abc123
status = SUCCESS
result = {"order_id": 15, "status": "completed"}
```

This is temporary.

It is useful for debugging or checking Celery task status.

It should not be used as the permanent business source of truth.

---

# 6. PostgreSQL vs Redis

## PostgreSQL

Stores permanent business data.

Example:

```text
Order status
Total price
Failure reason
Stock changes
```

Frontend should normally check order status from PostgreSQL through:

```text
GET /orders/{order_id}
```

---

## Redis

Used for temporary task communication.

```text
Redis broker = pending task queue
Redis result backend = temporary technical task result
```

Redis does not replace PostgreSQL.

---

# 7. API Endpoints

## Create Order

```text
POST /orders
```

Example request:

```json
{
  "user_id": 1,
  "product_id": 2,
  "quantity": 3
}
```

Example response:

```json
{
  "message": "Order created and processing started",
  "order_id": 15,
  "task_id": "abc123"
}
```

Important:

The response should not say:

```text
Order completed
```

because Celery has not completed the task yet.

Correct message:

```text
Order received and processing started
```

---

## Get Order Status

```text
GET /orders/{order_id}
```

This reads from PostgreSQL.

Example response:

```json
{
  "order_id": 15,
  "status": "completed",
  "total_price": 500
}
```

This endpoint is best for frontend/user-facing status.

---

## Get Celery Task Status

```text
GET /tasks/{task_id}
```

This reads from Redis result backend.

Example response:

```json
{
  "task_id": "abc123",
  "status": "SUCCESS",
  "result": {
    "order_id": 15,
    "status": "completed",
    "total_price": 500
  }
}
```

This endpoint is useful for:

```text
learning
debugging
admin panels
checking technical Celery task status
```

For real user-facing order status, prefer:

```text
GET /orders/{order_id}
```

---

# 8. Order Status vs Task Status

These are different concepts.

## Order Status

Stored in PostgreSQL.

Business statuses:

```text
pending
processing
completed
failed
```

---

## Task Status

Stored temporarily in Redis result backend.

Celery technical statuses:

```text
PENDING
STARTED
SUCCESS
FAILURE
RETRY
```

Example:

```text
Order status = failed
Task status = SUCCESS
```

This can happen when Celery successfully ran the task, but the business logic failed.

Example:

```text
Celery checked stock successfully.
Stock was not enough.
Order was marked as failed.
The task itself completed successfully.
```

---

# 9. Running Without Docker Compose

Use this option if you want to run services manually.

## Step 1: Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Linux/macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3: Run Redis Manually

If Redis is installed locally:

```bash
redis-server
```

Or run Redis manually with Docker:

```bash
docker run --name redis-celery -p 6379:6379 redis:7
```

Redis will be available at:

```text
localhost:6379
```

---

## Step 4: Run PostgreSQL Manually

If PostgreSQL is installed locally, create:

```text
database: taskdb
user: appuser
password: apppass
```

Or run PostgreSQL manually with Docker:

```bash
docker run --name postgres-taskdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=taskdb \
  -p 5432:5432 \
  postgres:15
```

The database URL used by the app is:

```text
postgresql://appuser:apppass@localhost:5432/taskdb
```

---

## Step 5: Run FastAPI

Open one terminal:

```bash
uvicorn app.main:app --reload
```

FastAPI will run at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

## Step 6: Run Celery Worker

Open another terminal:

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
```

This starts the Celery worker.

The worker listens to Redis DB 0 and processes tasks.

---

## Step 7: Test the Flow

Create an order:

```text
POST /orders
```

Check business status:

```text
GET /orders/{order_id}
```

Check technical task status:

```text
GET /tasks/{task_id}
```

---

# 10. Running With Docker Compose

Use this option if you want Redis and PostgreSQL to run through Docker Compose.

## docker-compose.yml

```yaml
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: taskdb
    ports:
      - "5432:5432"
```

Start services:

```bash
docker compose up
```

Then run FastAPI manually:

```bash
uvicorn app.main:app --reload
```

Then run Celery manually:

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
```

This setup uses Docker only for Redis and PostgreSQL.

FastAPI and Celery run manually from your terminal.

---

# 11. Full Docker Compose Option

If you want everything to run inside Docker Compose, you can also add FastAPI and Celery services.

Example:

```yaml
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: taskdb
    ports:
      - "5432:5432"

  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://appuser:apppass@postgres:5432/taskdb
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - postgres

  worker:
    build: .
    command: celery -A app.celery_app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://appuser:apppass@postgres:5432/taskdb
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - postgres
```

Important:

When running inside Docker Compose, services communicate by service name:

```text
redis://redis:6379/0
postgresql://appuser:apppass@postgres:5432/taskdb
```

When running manually on your machine, they use localhost:

```text
redis://localhost:6379/0
postgresql://appuser:apppass@localhost:5432/taskdb
```

---

# 12. Recommended Environment Variable Setup

Instead of hardcoding URLs, use environment variables.

## `app/database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://appuser:apppass@localhost:5432/taskdb"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
```

## `app/celery_app.py`

```python
import os
from celery import Celery

BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0"
)

RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/1"
)

celery_app = Celery(
    "order_task_app",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
)
```

This makes the same code work for both manual and Docker Compose setups.

---

# 13. Final Complete Flow

```text
User
↓
POST /orders
↓
FastAPI router receives request
↓
FastAPI validates user and product
↓
FastAPI creates order in PostgreSQL with status = pending
↓
FastAPI calls process_order.delay(order_id)
↓
Celery client code sends task message to Redis DB 0 broker
↓
FastAPI immediately returns order_id and task_id
↓
Celery worker reads task from Redis DB 0
↓
Celery worker executes process_order(order_id)
↓
Celery opens its own PostgreSQL session
↓
Celery updates order status = processing
↓
Celery checks product stock
↓
Celery updates order status = completed or failed
↓
Celery commits changes to PostgreSQL
↓
Celery stores technical result in Redis DB 1 result backend
↓
Frontend calls GET /orders/{order_id}
↓
FastAPI reads latest order status from PostgreSQL
↓
User sees completed or failed status
```

---

# 14. Best Production Rule

```text
FastAPI = receives HTTP requests
Celery = runs slow background tasks
Redis DB 0 = broker / task queue
Redis DB 1 = temporary result backend
PostgreSQL = permanent business data
/orders/{order_id} = user-facing status
/tasks/{task_id} = developer/debugging task status
```

---

# 15. One-Line Summary

FastAPI receives the request and saves business data in PostgreSQL. Celery receives only a task instruction through Redis, performs the slow work in the background, updates PostgreSQL with the final business status, and optionally stores a temporary technical result in Redis.