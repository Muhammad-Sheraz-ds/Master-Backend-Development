# Queueing & Task Management (Celery)
### Backend Engineering — Comprehensive Lecture

---




Yes. We’ll ignore the code in the `.md` file and learn the **concepts step by step**. Your file is about Celery, queues, workers, brokers, result backends, retries, Beat, etc. 

## Step 1: Why queueing exists

Imagine a user clicks **“Register”**.

Bad way:

```text
User waits → backend saves user → backend sends email → response returns
```

If email takes 3 seconds, user waits 3 seconds.

Better way:

```text
User waits → backend saves user → backend puts “send email” task in queue → response returns
```

Then later:

```text
Worker takes task from queue → sends email
```

So the main idea is:

**Your web app should handle the user request quickly. Slow work should be done later by background workers.**

## Mental model

```text
FastAPI / Django app = creates tasks
Queue / broker = holds tasks
Celery worker = performs tasks
```

Example:

```text
User signs up
  ↓
App says: “send welcome email later”
  ↓
Task goes into queue
  ↓
Worker picks it up
  ↓
Email gets sent
```

## Learn this first

A **task** is just a job you want done later.

Examples of tasks:

```text
send email
generate PDF
resize image
send notification
import CSV
call external API
```

A **queue** is a waiting line for those tasks.

A **worker** is the thing that takes tasks from the queue and executes them.

## Tiny exercise

Answer this in your own words:

**Why should we not send a slow email directly inside the user’s request?**



## Before We Start: Why Does Any of This Exist?

Imagine you run a post office. A customer walks in and hands you a package. You have two choices:

**Option A:** Make the customer stand at the counter while you personally drive the package across the city, deliver it, come back, and then say "okay, you're done." The customer waits 45 minutes.

**Option B:** Accept the package, hand them a receipt, put the package on a conveyor belt, let your delivery team handle it later. The customer is done in 10 seconds.

Option B is a **task queue**. Your backend accepts the job, hands it off, and immediately tells the user "got it." The heavy work happens in the background, separately, at its own pace.

That is Celery.

---

## Part 1: The Prerequisites — Concepts You Must Understand First

### 1.1 — Synchronous vs Asynchronous Execution

**New term — Synchronous:** One thing happens, waits to finish, then the next thing starts. Like standing in a queue at a bank. You wait your turn, get served, leave. Nothing else happens while you wait.

**New term — Asynchronous:** You start something, don't wait for it to finish, move on to other things. Like ordering food at a restaurant. You order, go sit down, talk to friends, food arrives when it's ready.

**In your FastAPI backend:**

```
Synchronous (bad for slow tasks):
Client → POST /send-email → [waits 3 seconds for email to send] → Response

Asynchronous with queue (correct):
Client → POST /send-email → [immediately] → Response: "Email queued"
                                  ↓
                         [Background worker sends email 3 seconds later]
```

The client got their response in 50ms instead of 3 seconds. They don't care that the email sends later. They just needed to know it was accepted.

---

### 1.2 — What Is a Process?

**New term — Process:** A running instance of a program. When you run `python app.py`, that's a process. Your operating system gives it RAM, CPU time, and an isolated memory space.

Multiple processes can run at the same time on the same machine. They don't share memory.

**Why does this matter?** Celery workers are separate processes from your FastAPI app. They run independently, in parallel, potentially on entirely different machines.

---

### 1.3 — What Is a Thread?

**New term — Thread:** A unit of execution within a process. One process can have multiple threads. Threads inside the same process **share memory**.

Think of a process as a restaurant kitchen. Threads are the individual chefs inside. They all share the same fridge, the same counter, the same equipment.

**Thread vs Process:**
| | Process | Thread |
|---|---|---|
| Memory | Isolated (own space) | Shared (within process) |
| Startup cost | Higher | Lower |
| Crash isolation | Good (one crash = that process dies) | Poor (one crash can kill all threads) |
| Communication | Message passing / queues | Shared variables (careful!) |

---

### 1.4 — What Is a Message Queue?

**New term — Message Queue:** A data structure (running as a service) where one part of your system can **send messages** and another part can **receive and process** those messages — without the two parts needing to talk to each other directly.

Think of it as a mailbox:
- Your FastAPI app drops a letter (task) in the mailbox
- The worker picks up letters and processes them
- The app doesn't wait for the worker. It dropped the letter and moved on.

Key properties:
- **Decoupling:** Producer and consumer don't know about each other
- **Persistence:** Messages survive if the worker crashes (they're still in the queue)
- **Buffering:** If 10,000 tasks arrive at once, the queue holds them. Workers process them at their own pace.

---

### 1.5 — What Is a Broker?

**New term — Broker:** The service that runs the message queue. It receives tasks from your app and holds them until a worker picks them up.

Common brokers:
| Broker | Notes |
|---|---|
| **Redis** | Easiest to set up, we already know it, great for most use cases |
| **RabbitMQ** | More powerful, built specifically for messaging, more complex |
| **Amazon SQS** | Managed cloud queue, AWS ecosystem |

For our stack: **Redis as broker** is the standard starting point.

---

### 1.6 — What Is a Worker?

**New term — Worker:** A separate process that runs your task functions. Workers watch the queue, pick up tasks, execute them, and report results.

```
[FastAPI App]  →  drops task into queue  →  [Redis Broker]
                                                   ↓
                                          [Celery Worker Process]
                                          picks up task, runs it
                                          logs result to backend
```

You can run **multiple workers** for parallel processing. You can run workers on **different machines** for scale.

---

### 1.7 — What Is a Result Backend?

**New term — Result Backend:** Where Celery stores the result of a completed task, so your app can retrieve it later if needed.

Without a result backend: task runs, result disappears into the void. ✅ Fine for fire-and-forget tasks.
With a result backend (Redis or DB): task runs, result stored. Your app can query "did task X finish? what was the result?" ✅ Required for status polling.

---

### 1.8 — What Is a Producer / Consumer Pattern?

One of the most fundamental patterns in distributed systems.

**Producer:** Creates work and puts it in the queue (your FastAPI app).
**Consumer:** Takes work from the queue and processes it (Celery worker).

They are **decoupled** — the producer doesn't know or care how many consumers exist or how fast they work. Consumers don't know how the producer generates work.

```
Producer (FastAPI) → [Queue] → Consumer (Celery Worker 1)
                              → Consumer (Celery Worker 2)
                              → Consumer (Celery Worker 3)
```

---

### 1.9 — What Is Concurrency in This Context?

**New term — Concurrency:** Multiple tasks making progress at the same time. Not necessarily simultaneously, but interleaved.

**New term — Parallelism:** Multiple tasks running at the exact same instant on multiple CPU cores.

With Celery, you can run:
- **Concurrent workers:** Multiple worker processes, each handling one task at a time
- **Concurrent within a worker:** Using threads or async within a single worker

For now: just know that running 4 Celery workers means 4 tasks can be processed simultaneously.

---

## Part 2: What Is Celery?

### 2.1 — The Definition

**Celery** is an open-source, distributed task queue library for Python.

It lets you:
1. Define Python functions as "tasks"
2. Send those tasks to a queue (broker) instead of running them immediately
3. Have separate worker processes pick up and execute those tasks
4. Optionally track task status and retrieve results

**Official description:** "An asynchronous task queue/job queue based on distributed message passing."

**Key facts:**
- Written in Python
- Works with Django, FastAPI, Flask — any Python backend
- Broker: Redis or RabbitMQ
- Battle-tested — used at Instagram, Dropbox, Mozilla, and millions of others
- Handles tens of millions of tasks per day in production systems

---

### 2.2 — When Do You Actually Use Celery?

**Use Celery for tasks that are:**

| Scenario | Why queue it? |
|---|---|
| Sending emails | SMTP can take 2–5 seconds. User shouldn't wait. |
| Sending SMS / push notifications | Same — external API calls, slow |
| Generating PDFs or reports | CPU-heavy, can take 10–30 seconds |
| Image/video processing | Very slow, shouldn't block the request |
| Data import/export (CSV, Excel) | Can take minutes |
| Calling slow third-party APIs | Unpredictable timing |
| Scraping data | Slow + can fail + needs retries |
| Sending webhooks | Fire-and-forget with retry logic |
| Machine learning inference | Slow computation |
| Scheduled jobs (cron-style) | Nightly reports, cleanup, sync |

**Do NOT use Celery for tasks that:**
- Must return a result to the user immediately
- Take under 50ms
- Require real-time guarantees

---

### 2.3 — The Architecture in One Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Your Application                   │
│  (FastAPI / Django / any Python backend)             │
│                                                      │
│   task.delay() → sends task to broker                │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Message Broker (Redis)                  │
│                                                      │
│   Queue: [task_1] [task_2] [task_3] [task_4] ...    │
│   (tasks wait here until a worker picks them up)    │
└────────────────────────┬────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌─────────────────────┐   ┌─────────────────────┐
│   Celery Worker 1   │   │   Celery Worker 2   │
│   (runs task_1)     │   │   (runs task_3)     │
└─────────┬───────────┘   └──────────┬──────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────┐
│             Result Backend (Redis)                   │
│   task_1 result: "success"                          │
│   task_3 result: "email sent to ali@test.com"       │
└─────────────────────────────────────────────────────┘
```

---

## Part 3: Setting Up Celery

### 3.1 — Installation

```bash
pip install celery redis
```

For monitoring (Flower — a web UI for Celery):
```bash
pip install flower
```

---

### 3.2 — Project Structure

Following the 3-layer architecture you've been learning:

```
shopflow/
├── app/
│   ├── main.py               ← FastAPI app
│   ├── api/
│   │   └── orders.py         ← API layer
│   ├── services/
│   │   └── order_service.py  ← Service layer (calls tasks)
│   ├── workers/
│   │   ├── celery_app.py     ← Celery app instance
│   │   ├── email_tasks.py    ← Email-related tasks
│   │   ├── report_tasks.py   ← Report generation tasks
│   │   └── notification_tasks.py
│   └── config.py
├── docker-compose.yml
└── requirements.txt
```

---

### 3.3 — Creating the Celery App Instance

```python
# app/workers/celery_app.py

from celery import Celery
import os

# Where tasks are held until picked up
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Where task results are stored
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Create the Celery app
celery_app = Celery(
    "shopflow",            # app name
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

# Configuration
celery_app.conf.update(
    task_serializer="json",          # how tasks are serialized
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,         # track when a task starts (not just queues/finishes)
    result_expires=3600,             # results expire after 1 hour
)
```

**Important:** We use Redis database `0` for the broker and `1` for results. Redis supports 16 logical databases (0–15). They share the same Redis server but are isolated namespaces.

---

### 3.4 — Defining Your First Task

```python
# app/workers/email_tasks.py

from app.workers.celery_app import celery_app
import time

@celery_app.task(name="send_welcome_email")
def send_welcome_email(user_email: str, user_name: str):
    """
    Sends a welcome email to a newly registered user.
    This runs in a Celery worker, NOT in the FastAPI process.
    """
    print(f"Sending welcome email to {user_email}...")
    
    # Simulate email sending (replace with real SMTP logic)
    time.sleep(2)   # pretend this takes 2 seconds
    
    print(f"Email sent to {user_email}")
    return {"status": "sent", "recipient": user_email}
```

**The `@celery_app.task` decorator** is what makes a regular Python function into a Celery task. That's it.

---

### 3.5 — Calling the Task from FastAPI

```python
# app/api/auth.py

from fastapi import APIRouter
from app.workers.email_tasks import send_welcome_email

router = APIRouter()

@router.post("/register")
async def register_user(email: str, name: str):
    # 1. Save user to database (fast — stays in FastAPI)
    # user = await user_service.create_user(email, name)
    
    # 2. Queue the email task — don't wait for it
    task = send_welcome_email.delay(email, name)
    
    # 3. Return immediately — user gets response in ~20ms
    return {
        "message": "Registration successful. Welcome email will arrive shortly.",
        "task_id": task.id    # client can use this to check status later
    }
```

**`.delay()`** is how you send a task to the queue. The function doesn't run here. It gets queued in Redis. A worker will pick it up and run it.

The FastAPI endpoint returns **immediately**. The user doesn't wait 2 seconds for the email.

---

### 3.6 — Starting the Celery Worker

In a separate terminal (while your FastAPI app is running):

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

Breaking this down:
- `-A app.workers.celery_app` → where your Celery app instance lives
- `worker` → start a worker process
- `--loglevel=info` → show info-level logs

You'll see output like:
```
[config]
.> app:         shopflow:0x7f...
.> transport:   redis://localhost:6379/0
.> results:     redis://localhost:6379/1
.> concurrency: 4 (prefork)

[queues]
.> celery           exchange=celery(direct) key=celery
```

The worker is now watching the queue. Every time your FastAPI app queues a task, the worker grabs it and runs it.

---

## Part 4: Task States and Monitoring

### 4.1 — Task Lifecycle

Every task goes through these states:

```
PENDING → STARTED → SUCCESS
                  → FAILURE
                  → RETRY
                  → REVOKED (manually cancelled)
```

**PENDING:** Task sent to queue, waiting for a worker to pick it up.
**STARTED:** A worker picked it up and is currently running it.
**SUCCESS:** Task completed without errors. Result stored in backend.
**FAILURE:** Task raised an exception.
**RETRY:** Task failed and is being retried automatically.
**REVOKED:** Task was manually cancelled before execution.

---

### 4.2 — Checking Task Status

```python
from app.workers.celery_app import celery_app
from celery.result import AsyncResult

def get_task_status(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,          # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.ready() else None,
        "failed": result.failed(),
    }
```

**FastAPI endpoint to poll status:**

```python
@router.get("/tasks/{task_id}")
async def check_task(task_id: str):
    return get_task_status(task_id)
```

**Client workflow:**
1. POST /register → gets back `task_id: "abc-123"`
2. GET /tasks/abc-123 → `{"status": "PENDING"}`
3. GET /tasks/abc-123 (3 seconds later) → `{"status": "SUCCESS", "result": {"status": "sent"}}`

---

### 4.3 — Flower: The Celery Web UI

Flower gives you a browser-based dashboard to monitor workers, tasks, and queues in real-time.

```bash
celery -A app.workers.celery_app flower --port=5555
```

Open `http://localhost:5555` in your browser.

You'll see:
- Active workers and their status
- Tasks currently running
- Task history (succeeded, failed, retried)
- Queue lengths
- Worker resource usage

In production, Flower runs as a service, password-protected.

---

## Part 5: Retries and Error Handling

### 5.1 — Why Retries Matter

Tasks fail. Networks go down. External APIs return 500 errors. Your email server is momentarily overloaded. You don't want to silently drop the task and leave the user without their email.

Celery has built-in retry logic.

---

### 5.2 — Automatic Retries

```python
@celery_app.task(
    name="send_order_confirmation",
    bind=True,              # gives access to `self` (the task instance)
    max_retries=3,          # try up to 3 times after the first failure
    default_retry_delay=60  # wait 60 seconds before retrying
)
def send_order_confirmation(self, order_id: int, user_email: str):
    try:
        # Try to send email
        result = email_provider.send(
            to=user_email,
            subject=f"Order #{order_id} confirmed!",
            body="Your order is on the way."
        )
        return {"status": "sent", "order_id": order_id}
    
    except email_provider.TemporaryError as exc:
        # Retry on temporary errors (network issues, rate limits)
        raise self.retry(exc=exc, countdown=60)   # retry in 60 seconds
    
    except email_provider.PermanentError as exc:
        # Don't retry on permanent errors (invalid email, blocked)
        raise   # just fail
```

**`bind=True`** gives the task access to `self`, which is the task instance. This lets you call `self.retry()`.

**`countdown`** is how many seconds to wait before retrying.

---

### 5.3 — Exponential Backoff

Instead of retrying every 60 seconds (which might hammer a struggling service), use **exponential backoff** — wait longer with each retry.

```python
@celery_app.task(bind=True, max_retries=5)
def call_external_api(self, payload: dict):
    try:
        response = requests.post("https://api.partner.com/webhook", json=payload)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as exc:
        # Retry: 2^retry_number * 60 seconds
        # Retry 1: 60s, Retry 2: 120s, Retry 3: 240s, Retry 4: 480s
        countdown = 2 ** self.request.retries * 60
        raise self.retry(exc=exc, countdown=countdown)
```

**New term — Exponential backoff:** A retry strategy where the wait time doubles with each failed attempt. Prevents overloading a struggling service.

---

### 5.4 — Task Failure Callbacks

What should happen after all retries are exhausted and the task still fails?

```python
from celery import Task

@celery_app.task(
    bind=True,
    max_retries=3,
    on_failure=None   # we'll handle this in the task body
)
def send_invoice_email(self, invoice_id: int, user_email: str):
    try:
        # ... send email
        pass
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            # All retries exhausted — alert the team
            alert_ops_team(f"FAILED: Invoice email for {invoice_id} after all retries")
            # Could also write to a dead-letter table in your DB
        raise self.retry(exc=exc)
```

**New term — Dead letter queue:** A separate queue where permanently failed tasks land after exhausting all retries. Used for auditing and manual recovery.

---

## Part 6: Named Queues and Task Routing

### 6.1 — Why Multiple Queues?

By default, all tasks go into one queue called `celery`. This is fine for small apps.

In production, you want **separate queues** for different task priorities:

**Problem without routing:**
- A user requests a 30-minute PDF report generation
- That task fills the only worker
- 1,000 users can't get their welcome emails for 30 minutes

**Solution:** Separate queues with dedicated workers.

```
Queue: high_priority  → emails, SMS, notifications (fast, user-facing)
Queue: default        → general tasks
Queue: low_priority   → reports, exports, batch jobs (slow, background)
```

---

### 6.2 — Defining Named Queues

```python
# app/workers/celery_app.py
from kombu import Queue

celery_app.conf.task_queues = (
    Queue("high_priority"),
    Queue("default"),
    Queue("low_priority"),
)

celery_app.conf.task_default_queue = "default"
```

---

### 6.3 — Routing Tasks to Specific Queues

**Option 1: In task definition:**
```python
@celery_app.task(name="send_sms", queue="high_priority")
def send_sms_notification(phone: str, message: str):
    # ...
    pass

@celery_app.task(name="generate_report", queue="low_priority")
def generate_monthly_report(month: int, year: int):
    # ...
    pass
```

**Option 2: At call time:**
```python
# Override queue when calling
send_sms_notification.apply_async(
    args=["+92300...", "Your order shipped!"],
    queue="high_priority"
)

generate_monthly_report.apply_async(
    args=[6, 2026],
    queue="low_priority"
)
```

---

### 6.4 — Starting Workers for Specific Queues

```bash
# Worker only handles high-priority tasks (4 concurrent)
celery -A app.workers.celery_app worker -Q high_priority --concurrency=4 --loglevel=info

# Worker only handles low-priority tasks (1 concurrent — no rush)
celery -A app.workers.celery_app worker -Q low_priority --concurrency=1 --loglevel=info

# Worker handles both default and high-priority
celery -A app.workers.celery_app worker -Q default,high_priority --concurrency=2 --loglevel=info
```

Now your heavy report generation never blocks time-sensitive email/SMS tasks.

---

## Part 7: Scheduled Tasks (Celery Beat)

### 7.1 — What Is Celery Beat?

**Celery Beat** is a scheduler that comes with Celery. It lets you run tasks on a schedule — like cron jobs, but in Python.

**New term — Cron job:** A task scheduled to run automatically at specific times or intervals (e.g., every day at 2am, every Monday at 8am). Named after the Unix `cron` scheduler.

Celery Beat = a process that runs continuously, looks at a schedule, and sends tasks to the queue at the right time.

```
Celery Beat (scheduler) → at 2am every day → sends "generate_daily_report" to queue
                                                        ↓
                                              Celery Worker picks it up and runs it
```

---

### 7.2 — Defining a Schedule

```python
# app/workers/celery_app.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    
    # Run every 5 minutes
    "cleanup-expired-sessions": {
        "task": "cleanup_expired_sessions",
        "schedule": 300,  # seconds
    },
    
    # Run every day at 2:00 AM UTC
    "daily-report": {
        "task": "generate_daily_sales_report",
        "schedule": crontab(hour=2, minute=0),
    },
    
    # Run every Monday at 9:00 AM
    "weekly-digest": {
        "task": "send_weekly_digest_emails",
        "schedule": crontab(hour=9, minute=0, day_of_week="monday"),
    },
    
    # Run on the 1st of every month at midnight
    "monthly-invoice": {
        "task": "generate_monthly_invoices",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
}
```

---

### 7.3 — Crontab Quick Reference

```
crontab(minute=0, hour=0, day_of_week='*', day_of_month='*', month_of_year='*')

Every 30 minutes:           crontab(minute='*/30')
Every hour:                 crontab(minute=0)
Every day at midnight:      crontab(hour=0, minute=0)
Weekdays at 9am:            crontab(hour=9, minute=0, day_of_week='1-5')
Every Sunday at 10pm:       crontab(hour=22, minute=0, day_of_week='sunday')
```

---

### 7.4 — Starting Celery Beat

```bash
# Start the beat scheduler (separate process from the worker)
celery -A app.workers.celery_app beat --loglevel=info
```

**Important:** Beat and Worker are two separate processes. Beat puts tasks in the queue on schedule. Workers execute them. You need both running.

In production:
```bash
# Start beat + worker together (development only)
celery -A app.workers.celery_app worker --beat --loglevel=info

# In production, run them as separate systemd services
```

---

## Part 8: Real-World Task Examples

### 8.1 — Email Sending Task

```python
# app/workers/email_tasks.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.workers.celery_app import celery_app
import os

@celery_app.task(
    name="send_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="high_priority"
)
def send_email(self, to: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = os.getenv("EMAIL_FROM")
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(os.getenv("SMTP_HOST"), 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.sendmail(msg["From"], to, msg.as_string())
        
        print(f"[EMAIL] Sent to {to}: {subject}")
        return {"sent": True, "to": to}
    
    except smtplib.SMTPException as exc:
        print(f"[EMAIL] Failed for {to}: {exc}")
        raise self.retry(exc=exc)
```

---

### 8.2 — PDF Report Generation

```python
# app/workers/report_tasks.py
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import Order

@celery_app.task(
    name="generate_sales_report",
    queue="low_priority",
    time_limit=600   # kill task if it takes more than 10 minutes
)
def generate_sales_report(month: int, year: int, requester_email: str):
    print(f"[REPORT] Generating report for {month}/{year}")
    
    db = SessionLocal()
    try:
        # 1. Fetch data
        orders = db.query(Order).filter(
            Order.month == month,
            Order.year == year
        ).all()
        
        # 2. Generate PDF (using reportlab or weasyprint)
        pdf_path = f"/tmp/report_{year}_{month}.pdf"
        # ... generate PDF logic here ...
        
        # 3. Upload to S3 or storage
        # upload_to_s3(pdf_path, f"reports/{year}/{month}.pdf")
        
        # 4. Email the requester
        send_email.delay(
            to=requester_email,
            subject=f"Sales Report - {month}/{year} Ready",
            body=f"Your report is ready. Download here: ..."
        )
        
        print(f"[REPORT] Completed for {month}/{year}")
        return {"report": pdf_path, "orders_count": len(orders)}
    
    finally:
        db.close()
```

**Notice:** One task (report) calls another task (email) using `.delay()`. This is **task chaining** at its simplest.

---

### 8.3 — Bulk Notification Task

```python
# app/workers/notification_tasks.py
from app.workers.celery_app import celery_app

@celery_app.task(name="send_bulk_notification", queue="default")
def send_bulk_notification(user_ids: list[int], message: str):
    """
    Sends a notification to a large list of users.
    Dispatches individual tasks per user for parallelism.
    """
    print(f"[NOTIF] Dispatching to {len(user_ids)} users")
    
    # Instead of looping and blocking, dispatch individual tasks
    for user_id in user_ids:
        send_single_notification.delay(user_id, message)
    
    return {"dispatched": len(user_ids)}


@celery_app.task(name="send_single_notification", queue="default")
def send_single_notification(user_id: int, message: str):
    # fetch user push token from DB
    # send via FCM / APNs
    print(f"[NOTIF] Sent to user {user_id}")
    return {"user_id": user_id, "sent": True}
```

This pattern dispatches one task per user. All those tasks run in parallel across your workers. Sending to 10,000 users doesn't take 10,000x longer if you have multiple workers.

---

### 8.4 — Integration in FastAPI Service Layer

```python
# app/services/order_service.py
from app.workers.email_tasks import send_email
from app.workers.report_tasks import generate_sales_report
from app.models import Order
from sqlalchemy.orm import Session

class OrderService:
    
    def create_order(self, db: Session, order_data: dict) -> Order:
        # 1. Save order to DB (synchronous — must complete now)
        order = Order(**order_data)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 2. Queue confirmation email (async — do it later)
        send_email.delay(
            to=order_data["user_email"],
            subject=f"Order #{order.id} Confirmed",
            body=f"<h1>Thanks for your order!</h1><p>Order #{order.id}</p>"
        )
        
        return order
    
    def request_report(self, db: Session, month: int, year: int, email: str) -> dict:
        # Queue a slow background job, return immediately
        task = generate_sales_report.apply_async(
            args=[month, year, email],
            queue="low_priority"
        )
        
        return {
            "message": "Report generation started. You'll receive an email when ready.",
            "task_id": task.id
        }

order_service = OrderService()
```

---

## Part 9: `.delay()` vs `.apply_async()` — What's the Difference?

Both send tasks to the queue. `.delay()` is shorthand for `.apply_async()`.

```python
# These are identical:
send_email.delay("ali@test.com", "Subject", "Body")

send_email.apply_async(args=["ali@test.com", "Subject", "Body"])
```

Use `.apply_async()` when you need extra control:

```python
from datetime import datetime, timedelta

# Run task in 30 seconds
send_email.apply_async(
    args=["ali@test.com", "Subject", "Body"],
    countdown=30
)

# Run task at a specific time
send_email.apply_async(
    args=["ali@test.com", "Subject", "Body"],
    eta=datetime.utcnow() + timedelta(hours=1)  # run in 1 hour
)

# Override queue
send_email.apply_async(
    args=["ali@test.com", "Subject", "Body"],
    queue="high_priority",
    priority=9   # higher number = higher priority within queue
)

# Set a time limit
generate_sales_report.apply_async(
    args=[6, 2026, "ali@test.com"],
    time_limit=300,    # kill if takes more than 5 minutes
    soft_time_limit=240  # raise SoftTimeLimitExceeded at 4 min (lets task clean up)
)
```

---

## Part 10: Running Everything with Docker Compose

In production (and for consistent local dev), you run all components as separate services.

```yaml
# docker-compose.yml
version: "3.9"

services:
  # Your FastAPI application
  api:
    build: .
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - postgres

  # Celery worker — high priority tasks
  worker_high:
    build: .
    command: celery -A app.workers.celery_app worker -Q high_priority --concurrency=4 --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis

  # Celery worker — low priority tasks
  worker_low:
    build: .
    command: celery -A app.workers.celery_app worker -Q low_priority --concurrency=1 --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis

  # Celery Beat — scheduler
  beat:
    build: .
    command: celery -A app.workers.celery_app beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  # Flower — monitoring dashboard
  flower:
    build: .
    command: celery -A app.workers.celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis

  # Redis — broker + result backend
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # PostgreSQL — your main database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: shopflow
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: shopflow
    ports:
      - "5432:5432"
```

Start everything:
```bash
docker-compose up --build
```

You now have: FastAPI on :8000, Flower dashboard on :5555, Redis, Postgres, and multiple workers all running together.

---

## Part 11: Common Mistakes & Anti-Patterns

### ❌ Mistake 1: Passing Database Objects as Task Arguments

```python
# BAD — SQLAlchemy objects can't be serialized to JSON
user = db.query(User).get(1)
send_email.delay(user)   # will crash

# GOOD — pass primitive types only
send_email.delay(user.id, user.email, user.name)
```

**Rule:** Only pass JSON-serializable types to tasks: strings, ints, floats, lists, dicts.

---

### ❌ Mistake 2: Opening a DB Session in the Task Without Closing It

```python
# BAD — session never closed if exception occurs
@celery_app.task
def bad_task():
    db = SessionLocal()
    result = db.query(Order).all()
    # if exception here, db never closes

# GOOD — always use try/finally
@celery_app.task
def good_task():
    db = SessionLocal()
    try:
        result = db.query(Order).all()
        return len(result)
    finally:
        db.close()
```

---

### ❌ Mistake 3: One Giant Task

```python
# BAD — does too much in one task, hard to retry partially
@celery_app.task
def process_order(order_id):
    validate_payment()      # step 1 (fast)
    update_inventory()      # step 2 (medium)
    generate_invoice()      # step 3 (slow)
    send_confirmation()     # step 4 (can fail)
    notify_warehouse()      # step 5 (external API)
```

If step 5 fails, you retry from step 1 and might charge the customer twice.

```python
# GOOD — separate tasks per concern, chain them
@celery_app.task
def validate_payment(order_id): ...

@celery_app.task
def update_inventory(order_id): ...

# Call tasks sequentially, each retries independently
```

---

### ❌ Mistake 4: Running Workers with the Same Queue Name but Different Code

If you deploy a new version of your app but some workers still run the old code, tasks routed to them run the wrong version. Always coordinate deploys — restart workers when you deploy.

---

### ❌ Mistake 5: Not Setting `time_limit`

A buggy task can run forever, blocking a worker.

```python
# Always set a time limit on long-running tasks
@celery_app.task(time_limit=300, soft_time_limit=240)
def generate_report(...): ...
```

---

## Part 12: Quick Reference

### Task Definition Options

```python
@celery_app.task(
    name="task_name",           # explicit name (don't rely on auto-naming)
    bind=True,                  # access self.retry(), self.request
    max_retries=3,              # total retry attempts
    default_retry_delay=60,     # seconds between retries
    queue="high_priority",      # which queue this task goes to
    time_limit=300,             # hard kill after N seconds
    soft_time_limit=240,        # raise exception after N seconds (task can clean up)
    ignore_result=True,         # don't store result (fire and forget)
    acks_late=True,             # only ack (remove from queue) after task completes
)
def my_task(self, arg1, arg2):
    pass
```

**New term — ack (acknowledge):** Confirmation sent to the broker that a message was received and processed. By default, tasks are acked when received (not when completed). With `acks_late=True`, they're acked only after completion — safer for critical tasks.

---

### Calling Tasks

```python
# Fire and forget
my_task.delay(arg1, arg2)

# With options
my_task.apply_async(args=[arg1, arg2], countdown=30, queue="high_priority")

# Get result (blocks until complete — use sparingly)
result = my_task.delay(arg1, arg2)
output = result.get(timeout=10)

# Check without blocking
result = my_task.delay(arg1, arg2)
if result.ready():
    print(result.result)
```

---

### CLI Commands

```bash
# Start a worker
celery -A app.workers.celery_app worker --loglevel=info

# Start worker with specific queue and concurrency
celery -A app.workers.celery_app worker -Q high_priority --concurrency=4

# Start beat scheduler
celery -A app.workers.celery_app beat

# Start flower monitoring
celery -A app.workers.celery_app flower --port=5555

# Inspect active workers
celery -A app.workers.celery_app inspect active

# Inspect registered tasks
celery -A app.workers.celery_app inspect registered

# Purge all tasks from queue (careful in production)
celery -A app.workers.celery_app purge
```

---

## Summary: The Mental Model

```
[User Request]
      ↓
[FastAPI Endpoint]
      ↓
[Service Layer] → task.delay() → [Redis Broker Queue]
      ↓                                  ↓
[Return 200 immediately]      [Celery Worker picks up task]
                                          ↓
                               [Task runs in background]
                                          ↓
                               [Result stored in Redis]
                               [Email sent / PDF generated / etc.]
```

**FastAPI** handles the request cycle. It's fast, non-blocking, and user-facing.

**Celery** handles the slow, deferred, or scheduled work. It's separate, scalable, and retry-aware.

**Redis** is the glue — it's both the broker (holds pending tasks) and the result backend (stores completed results).

**The rule:** If it takes more than a second, don't do it in the request/response cycle. Queue it.

---

## Revision Notes

**Key terms to memorize:**

| Term | One-line definition |
|---|---|
| Synchronous | Wait for task to finish before moving on |
| Asynchronous | Start task, move on, result comes later |
| Message Queue | Holds tasks until a worker picks them up |
| Broker | Service that runs the queue (Redis, RabbitMQ) |
| Worker | Separate process that picks up and executes tasks |
| Result Backend | Where task results are stored after completion |
| Producer | Creates and sends tasks (your FastAPI app) |
| Consumer | Picks up and executes tasks (Celery worker) |
| `.delay()` | Shorthand to send a task to the queue |
| `.apply_async()` | Full method to send task with advanced options |
| Retry | Re-running a failed task automatically |
| Exponential backoff | Wait longer between each retry |
| Dead letter queue | Where permanently failed tasks go |
| Celery Beat | Scheduler that runs tasks on a time schedule |
| Cron job | A task that runs on a recurring time schedule |
| Named queues | Separate queues for different task priorities |
| Concurrency | Multiple tasks running at the same time |
| ack | Confirmation that a task was received and processed |
| Flower | Web UI dashboard for monitoring Celery |
| `time_limit` | Maximum seconds a task is allowed to run |

---

*End of Lecture — Queueing & Task Management (Celery)*