# FastAPI + Celery + Redis + Database — Real Production Flow

## 1. Main Idea

In a backend application, some tasks are fast and some tasks are slow.

Fast tasks can be completed during the normal request-response cycle.

Examples:

```text
Create user
Save order
Fetch profile
Validate input
```

Slow tasks should not block the user request.

Examples:

```text
Send email
Generate invoice
Process order
Resize image
Call third-party API
Generate report
Send notifications
```

For slow tasks, we use Celery.

The main idea is:

```text
FastAPI handles the user request quickly.
Celery handles slow background work separately.
Redis works as the communication bridge.
PostgreSQL stores permanent business data.
```

---

## 2. Why We Do Not Complete Everything Inside FastAPI

Without Celery:

```text
User sends request
↓
FastAPI saves order
↓
FastAPI processes order
↓
FastAPI sends email
↓
FastAPI generates invoice
↓
User waits until everything is complete
```

This is bad because the user may wait many seconds.

With Celery:

```text
User sends request
↓
FastAPI saves order
↓
FastAPI sends background task to Celery
↓
FastAPI immediately returns response
↓
Celery completes slow work in background
```

This is better because the user gets a fast response.

---

## 3. Important Mental Model

FastAPI and Celery are not the same running program.

They are two separate processes.

```text
Process 1:
FastAPI application

Process 2:
Celery worker
```

FastAPI is started with:

```bash
uvicorn app.main:app --reload
```

Celery worker is started separately with:

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
```

They do not share memory.

They do not directly call each other as running processes.

They communicate through Redis.

---

## 4. Role of Redis

Redis is used in two ways.

```text
Redis DB 0 = Broker
Redis DB 1 = Result Backend
```

Even though we start only one Redis server, Redis has multiple logical databases.

Example:

```text
redis://localhost:6379/0
redis://localhost:6379/1
```

These are not two Redis servers.

They are two logical databases inside the same Redis server.

---

## 5. Redis DB 0 — Broker

The broker stores pending tasks.

When FastAPI runs:

```python
process_order.delay(order_id)
```

Celery creates a task message and stores it in Redis DB 0.

Conceptually, Redis stores something like:

```text
Task name: process_order
Arguments: order_id = 15
```

Redis DB 0 is like a task waiting room.

```text
Redis DB 0 Broker

-------------------------
process_order(15)
-------------------------
send_email(22)
-------------------------
generate_invoice(10)
-------------------------
```

The actual order data is not stored in Redis.

Only the instruction to run the task is stored there.

---

## 6. Redis DB 1 — Result Backend

The result backend stores technical Celery task results.

When Celery finishes a task, it stores something like this in Redis DB 1:

```text
task_id: abc123
status: SUCCESS
result: {"order_id": 15, "status": "completed"}
```

This is useful for checking whether the Celery task finished, failed, or is still pending.

But this data is temporary.

It is not the permanent source of truth.

---

## 7. PostgreSQL — Permanent Business Truth

PostgreSQL stores the real business data.

For an order system, PostgreSQL stores:

```text
Order ID
User ID
Product ID
Quantity
Order status
Total price
Failure reason
Created time
```

Example order statuses:

```text
pending
processing
completed
failed
```

This is the data the user should normally see.

Redis is temporary.

PostgreSQL is permanent.

Best rule:

```text
Redis = temporary task coordination
PostgreSQL = permanent business data
```

---

## 8. Full Order Flow

When a user creates an order:

```text
POST /orders
```

FastAPI does this:

```text
1. Validate user
2. Validate product
3. Create order in PostgreSQL with status = pending
4. Send Celery task: process_order.delay(order_id)
5. Return response immediately
```

Example response:

```json
{
  "order_id": 15,
  "task_id": "abc123",
  "message": "Order received and processing started"
}
```

Important:

FastAPI should not say:

```text
Order completed
```

because the order is not completed yet.

It should say:

```text
Order received and processing started
```

---

## 9. What Happens After FastAPI Returns?

After FastAPI returns the response, the HTTP request is finished.

FastAPI is no longer processing that order.

Now Redis and Celery maintain the background work.

The Celery worker is already running separately.

It keeps listening to Redis DB 0.

When it finds a task:

```text
process_order(15)
```

it takes the task and executes it.

---

## 10. How Celery Updates the Database

Inside the Celery task, the worker opens its own database session.

Example:

```python
@celery_app.task(name="process_order")
def process_order(order_id: int):
    db = SessionLocal()

    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        order.status = "processing"
        db.commit()

        # Do slow work here

        order.status = "completed"
        db.commit()

    finally:
        db.close()
```

Celery updates the database directly.

This is why the order status changes from:

```text
pending → processing → completed
```

or:

```text
pending → processing → failed
```

The `db.commit()` call saves the changed status permanently into PostgreSQL.

---

## 11. What Happens If the Task Fails?

If the task fails because of business logic, for example not enough stock, Celery should update the order in PostgreSQL.

Example:

```python
order.status = "failed"
order.failure_reason = "Not enough stock"
db.commit()
```

Then the frontend can show:

```json
{
  "order_id": 15,
  "status": "failed",
  "reason": "Not enough stock"
}
```

So even if the background task fails, the user can still know the final result by checking the order status from the database.

---

## 12. How the User Knows Success or Failure

FastAPI does not automatically notify the user when Celery finishes.

The frontend has to check the status.

The most common beginner-friendly method is polling.

Frontend receives:

```json
{
  "order_id": 15,
  "message": "Order received and processing started"
}
```

Then frontend calls:

```text
GET /orders/15
```

every few seconds.

If the response is:

```json
{
  "order_id": 15,
  "status": "processing"
}
```

the frontend keeps waiting.

If the response is:

```json
{
  "order_id": 15,
  "status": "completed"
}
```

the frontend shows success.

If the response is:

```json
{
  "order_id": 15,
  "status": "failed",
  "reason": "Not enough stock"
}
```

the frontend shows failure.

This process is called polling.

---

## 13. Real-World Ways to Inform Users

There are three common ways.

### 1. Polling

Frontend repeatedly checks:

```text
GET /orders/{order_id}
```

This is simple and common.

Good for:

```text
order status
report generation
file processing
payment checks
```

### 2. WebSockets

Frontend opens a live connection with the backend.

The backend pushes updates to the frontend.

Good for:

```text
live dashboards
chat apps
delivery tracking
progress bars
```

### 3. Notifications

Celery sends an email, SMS, push notification, or webhook when the task finishes.

Good when the user may leave the page.

Example:

```text
Your report is ready.
Your order has been completed.
Your invoice has been generated.
```

---

## 14. Purpose of `/orders/{order_id}` Endpoint

This endpoint checks the real business status.

It reads from PostgreSQL.

Example:

```text
GET /orders/15
```

Response:

```json
{
  "order_id": 15,
  "status": "completed",
  "total_price": 500
}
```

This endpoint should be used by the frontend for normal users.

It answers:

```text
What happened to my order?
Is my order completed?
Did it fail?
What is the total price?
```

---

## 15. Purpose of `/tasks/{task_id}` Endpoint

This endpoint checks the technical Celery task status.

It reads from Redis result backend.

Example:

```text
GET /tasks/abc123
```

Response:

```json
{
  "task_id": "abc123",
  "status": "SUCCESS",
  "result": {
    "order_id": 15,
    "status": "completed"
  }
}
```

This endpoint is useful for:

```text
development
debugging
admin panels
learning Celery
checking whether the worker executed the task
```

It answers:

```text
Did Celery run this task?
Is the task PENDING, STARTED, SUCCESS, or FAILURE?
Did the task crash?
```

But it should not be the main user-facing source of truth.

---

## 16. Why `/tasks/{task_id}` Is Not Best for Normal Users

Redis result backend stores task results temporarily.

After some time, the result can expire.

If the frontend depends only on:

```text
GET /tasks/{task_id}
```

then later it may get confusing output because the result may no longer exist in Redis.

That is why real apps usually show user-facing status from the database.

Use:

```text
GET /orders/{order_id}
```

for users.

Use:

```text
GET /tasks/{task_id}
```

for developers or debugging.

---

## 17. Important Difference Between Order Status and Task Status

Order status is business status.

Example:

```text
pending
processing
completed
failed
```

Task status is Celery technical status.

Example:

```text
PENDING
STARTED
SUCCESS
FAILURE
RETRY
```

These are not always the same.

Example:

```text
Order status = failed
Task status = SUCCESS
```

This can happen when the Celery task ran successfully, but the business process failed.

For example:

```text
Celery successfully checked stock.
Stock was not enough.
Order was marked as failed.
Task itself completed successfully.
```

So the task succeeded technically, but the order failed from a business point of view.

---

## 18. Final Production Rule

For production systems:

```text
Store permanent business status in PostgreSQL.
Use Redis broker only to queue background tasks.
Use Redis result backend only for temporary technical task tracking.
Use Celery worker to execute slow tasks and update the database.
Use /orders/{order_id} for frontend/user status.
Use /tasks/{task_id} for debugging/admin/developer status.
```

---

## 19. Final Complete Flow

```text
User
↓
POST /orders
↓
FastAPI
↓
Create order in PostgreSQL with status = pending
↓
Call process_order.delay(order_id)
↓
Celery client sends task message to Redis DB 0 broker
↓
FastAPI returns response immediately
↓
Celery worker reads task from Redis DB 0
↓
Celery worker runs process_order(order_id)
↓
Celery worker opens PostgreSQL session
↓
Celery updates order status = processing
↓
Celery performs slow work
↓
Celery updates order status = completed or failed
↓
Celery stores technical task result in Redis DB 1 result backend
↓
Frontend calls GET /orders/{order_id}
↓
FastAPI reads latest order status from PostgreSQL
↓
User sees completed or failed status
```

---

## 20. One-Line Summary

FastAPI handles the request quickly, Celery handles slow background work, Redis coordinates task messages and temporary task results, and PostgreSQL stores the permanent business truth.
