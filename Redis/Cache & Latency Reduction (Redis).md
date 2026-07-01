# Cache & Latency Reduction (Redis)
### Backend Engineering — Comprehensive Lecture

---

## Before We Start: Why Does Any of This Exist?

Imagine you own a restaurant. Every time a customer asks "what's on the menu?", you walk to the back kitchen, dig through a filing cabinet, photocopy the menu, and bring it back. That takes 30 seconds every single time.

Now imagine you just **put the menu on the table**. Same answer. Zero seconds.

That is literally what caching is. Stop doing expensive work over and over when the answer hasn't changed.

---

## Part 1: The Prerequisites — Concepts You MUST Understand First

### 1.1 — The Memory Hierarchy (The Speed Ladder)

Your computer has several places to store data. They differ in **speed** and **size**. Think of them as storage tiers:

```
FASTEST (nanoseconds)           SMALLEST (bytes–kilobytes)
        ↕
    CPU Registers         ← the CPU's own tiny notepad
        ↕
    CPU Cache (L1/L2/L3)  ← built into the chip, super fast
        ↕
    RAM (Memory)          ← your app lives here while running
        ↕
    SSD / Hard Disk       ← permanent storage, much slower
        ↕
    Network / Database    ← another machine entirely
        ↕
SLOWEST (milliseconds)          LARGEST (terabytes)
```

**The rule:** The faster the storage, the smaller and more expensive it is.

| Storage Type | Typical Speed | Example Cost |
|---|---|---|
| CPU Cache (L1) | ~1 ns | Built-in |
| RAM | ~100 ns | $10/GB |
| NVMe SSD | ~100 µs | $0.10/GB |
| Hard Disk (HDD) | ~10 ms | $0.02/GB |
| Network DB Call | ~50–200 ms | Per request |

**New term — nanosecond (ns):** One billionth of a second. Your CPU does billions of operations per second.

**New term — microsecond (µs):** One millionth of a second.

**New term — millisecond (ms):** One thousandth of a second. This is what humans start to *notice* as slowness.

---

### 1.2 — What Is Latency?

**Latency** is the time it takes to get a response after making a request.

"I asked for data. How long until I got it back?" — that gap is latency.

Examples:
- You hit an API endpoint → database query takes 200ms → user sees response in 200ms. **Latency = 200ms.**
- You hit the same endpoint → result is cached in RAM → user sees response in 2ms. **Latency = 2ms.**

**Why does latency matter?**
- Google research: 500ms slowdown → 20% drop in traffic
- Amazon: 100ms slowdown → 1% drop in revenue
- Users abandon pages that take more than 3 seconds

---

### 1.3 — What Is RAM (Memory)?

**RAM = Random Access Memory.** This is where your running program stores its working data.

When you start a Python script, your variables live in RAM. When your script ends, RAM is cleared. It's **temporary**.

Key property: **extremely fast** to read/write — microseconds.

**Analogy:** RAM is your desk. Your hard disk is a filing cabinet in another room. You keep the stuff you're actively working with on your desk. Everything else is in the cabinet.

---

### 1.4 — What Is a Hard Disk / Persistent Storage?

Your database (PostgreSQL, MySQL, etc.) stores data on **disk**. This means:
- Data survives when the server restarts ✅
- Reads/writes are **slow** compared to RAM ❌

Every time you run `SELECT * FROM products WHERE id=42`, PostgreSQL:
1. Reads from disk
2. Parses the query
3. Executes a query plan
4. Returns rows

That takes **50–300ms** depending on indexes, load, data size.

**New term — I/O (Input/Output):** Any operation that involves reading or writing to a storage device. "I/O bound" means your app is slow because of disk/network reads.

---

### 1.5 — What Is a Cache?

**A cache is a fast, temporary storage layer that holds copies of frequently requested data.**

It sits between your application and the slow data source (database, external API, file system).

```
Client Request
      ↓
  [Your App]
      ↓
  Check Cache  ──── HIT ──→  Return cached data (2ms) ✅
      ↓
   MISS
      ↓
  Query Database (200ms)
      ↓
  Store result in Cache
      ↓
  Return data to client
```

**Cache HIT:** Data was found in the cache. Fast. ✅
**Cache MISS:** Data was NOT in the cache. Had to go to the database. Slow. ❌

**Cache Hit Rate:** The percentage of requests that are cache hits. A good cache hit rate is 80–95%+.

---

### 1.6 — What Is TTL (Time To Live)?

Cached data can become **stale** (outdated). If a product's price changes in the database but your cache still has the old price, you'll serve wrong data.

**TTL (Time To Live)** is a timer on cached data. After TTL expires, the data is automatically deleted from the cache. The next request will be a cache miss, fetching fresh data from the database.

```
Cache entry created → TTL = 60 seconds → After 60s, entry deleted automatically
```

**Analogy:** Milk has an expiry date. After that date, you throw it out and buy fresh milk. TTL is the expiry date for cached data.

---

### 1.7 — What Is a Network Round Trip?

When your backend calls another service (a database, external API), data has to travel:
1. From your server → through network → to the database server
2. Database processes the request
3. Response travels back → through network → to your server

Each leg takes time. Even on a fast local network, that's **1–5ms per trip**. Over the internet, **50–300ms**.

If one user request triggers 10 database calls, you're paying that cost 10 times.

---

## Part 2: What Is Caching? (The Full Picture)

### 2.1 — The Core Problem Caching Solves

Your backend gets 10,000 requests per second for the same product page. Without caching:
- 10,000 database queries per second
- Database gets crushed
- Response times spike
- App crashes or users get errors

With caching:
- First request: cache miss → query DB → store in cache
- Next 9,999 requests: cache hit → serve from RAM in 1–2ms
- Database barely touched

**Caching is the single most impactful performance optimization in backend engineering.**

---

### 2.2 — What Data Is Worth Caching?

Good candidates for caching:
- **Expensive to compute:** Database joins, aggregations, ML model outputs
- **Read frequently, written rarely:** Product catalog, user profiles, config settings
- **Same result for many users:** Homepage, public API responses
- **Acceptable if slightly stale:** News feed, leaderboard, recommendations

Bad candidates for caching:
- **Changes every second:** Real-time prices, live scores
- **User-specific sensitive data:** Bank balance, medical records (cache carefully)
- **Write-heavy data:** Logs, events, transactions

---

### 2.3 — Types of Caching

| Type | Where | Example |
|---|---|---|
| **In-process** | Inside your app's RAM | Python dict, lru_cache |
| **Distributed Cache** | Separate server (Redis, Memcached) | Redis |
| **Database Query Cache** | Inside the DB | PostgreSQL's buffer pool |
| **CDN Cache** | Edge servers worldwide | CloudFront, Cloudflare |
| **Browser Cache** | User's browser | HTTP Cache-Control headers |

For backend engineering, **distributed cache (Redis)** is what you'll use in production.

---

### 2.4 — Cache Eviction Policies

What happens when your cache is full and new data needs to be stored?

**Eviction** = removing old entries to make room for new ones.

Common policies:

| Policy | Meaning | Use when |
|---|---|---|
| **LRU** (Least Recently Used) | Remove data not accessed recently | General purpose — most common |
| **LFU** (Least Frequently Used) | Remove least-accessed data overall | When some data is permanently hot |
| **FIFO** (First In First Out) | Remove oldest entry | Simple queues |
| **TTL-based** | Remove expired entries | When freshness matters |

**Redis default:** LRU (configurable).

---

## Part 3: Redis — The Most Popular Cache in the World

### 3.1 — What Is Redis?

**Redis = Remote Dictionary Server**

It's an **in-memory data structure store** — meaning it holds data in RAM, not on disk. This is what makes it so fast.

Key facts:
- Open-source, written in C
- Single-threaded (but blazing fast — handles 100,000+ ops/second)
- Supports rich data structures, not just key-value strings
- Optional persistence (can write to disk for durability)
- Used by Twitter, GitHub, Stack Overflow, Airbnb, and millions more

**New term — data structure store:** Unlike a traditional database that stores rows/columns, Redis stores data in flexible structures like strings, lists, sets, hashes, and sorted sets. More on this below.

---

### 3.2 — How Redis Compares to a Database

| Feature | PostgreSQL | Redis |
|---|---|---|
| Storage | Disk | RAM (primarily) |
| Speed | 50–300ms per query | 0.1–1ms per operation |
| Data model | Tables, rows, columns | Key-value + rich structures |
| Durability | Fully durable | Optional (RDB / AOF) |
| Query language | SQL | Redis commands |
| Best for | Source of truth | Speed layer / cache |

**The relationship:** PostgreSQL is your filing cabinet (truth). Redis is your desk (speed). You don't replace one with the other. You use both.

---

### 3.3 — Installing Redis Locally

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
redis-cli ping   # should return PONG
```

**On Mac:**
```bash
brew install redis
brew services start redis
redis-cli ping
```

**Via Docker (cleanest for dev):**
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

**Default port:** 6379

---

### 3.4 — The Redis CLI — Your First Commands

Open the Redis CLI:
```bash
redis-cli
```

**Basic SET and GET:**
```
127.0.0.1:6379> SET name "Ali"
OK
127.0.0.1:6379> GET name
"Ali"
```

**SET with TTL (expire in 60 seconds):**
```
127.0.0.1:6379> SET session:user123 "active" EX 60
OK
127.0.0.1:6379> TTL session:user123
(integer) 57   ← seconds remaining
```

**Delete a key:**
```
127.0.0.1:6379> DEL name
(integer) 1
```

**Check if a key exists:**
```
127.0.0.1:6379> EXISTS name
(integer) 0   ← 0 means not found
```

---

## Part 4: Redis Data Structures

This is where Redis gets powerful. It's not just key → string. It supports 6 core data structures.

---

### 4.1 — Strings

The simplest type. Key maps to a single string value. Can store text, numbers, or JSON blobs.

```bash
SET product:42:price "29.99"
GET product:42:price         # "29.99"

# Increment a number atomically
SET page:views 0
INCR page:views              # returns 1
INCR page:views              # returns 2
INCRBY page:views 10         # returns 12
```

**New term — atomically:** Happens as one indivisible operation. No other command can interrupt it. Critical for counters, rate limiters.

**Use cases:** Caching API responses (as JSON strings), counters, feature flags, session tokens.

---

### 4.2 — Hashes

A key maps to a **dictionary** (field → value pairs). Like a row in a database table but in Redis.

```bash
HSET user:1001 name "Ali" email "ali@example.com" role "admin"
HGET user:1001 name          # "Ali"
HGET user:1001 email         # "ali@example.com"
HGETALL user:1001            # all fields and values
HMSET user:1001 name "Usman" role "staff"   # update multiple fields
HDEL user:1001 role          # delete one field
```

**Use cases:** Storing user sessions, object metadata, settings per entity.

**Why not just store JSON as a string?** With a hash, you can update one field without re-serializing the whole object. More efficient.

---

### 4.3 — Lists

An ordered sequence of strings. Like a Python list. You can push/pop from both ends.

```bash
RPUSH queue:emails "email1@x.com"   # push to right
RPUSH queue:emails "email2@x.com"
LPUSH queue:emails "urgent@x.com"   # push to left (front)

LRANGE queue:emails 0 -1            # get all items
# 1) "urgent@x.com"
# 2) "email1@x.com"
# 3) "email2@x.com"

LPOP queue:emails                   # pop from left
# "urgent@x.com"

LLEN queue:emails                   # length = 2
```

**Use cases:** Message queues, activity feeds, recent items list, task queues.

---

### 4.4 — Sets

An **unordered collection of unique strings**. No duplicates allowed.

```bash
SADD tags:product:42 "electronics" "sale" "featured"
SADD tags:product:42 "electronics"   # duplicate — ignored

SMEMBERS tags:product:42             # all members
SISMEMBER tags:product:42 "sale"     # 1 (yes, it's in the set)
SCARD tags:product:42                # 3 (count)

# Set operations
SADD tags:product:99 "sale" "new"
SINTER tags:product:42 tags:product:99   # intersection: "sale"
SUNION tags:product:42 tags:product:99   # union: all tags
```

**Use cases:** Tags, unique visitors tracking, friend lists, deduplication.

---

### 4.5 — Sorted Sets (ZSets)

Like a set, but each member has a **score** (a floating-point number). Members are automatically sorted by score.

```bash
ZADD leaderboard 9500 "Ali"
ZADD leaderboard 8800 "Ahmed"
ZADD leaderboard 9200 "Sara"

ZRANGE leaderboard 0 -1 WITHSCORES       # ascending order
# Ahmed 8800, Sara 9200, Ali 9500

ZREVRANGE leaderboard 0 2 WITHSCORES     # top 3 descending
# Ali 9500, Sara 9200, Ahmed 8800

ZINCRBY leaderboard 300 "Ahmed"          # Ahmed's score → 9100
ZRANK leaderboard "Ali"                  # rank (0-indexed)
```

**Use cases:** Leaderboards, rate limiting (using timestamps as scores), priority queues, trending content.

---

### 4.6 — Summary: Which Structure For What?

| Structure | Think of it as | Best for |
|---|---|---|
| String | Single value | Cached responses, counters, flags |
| Hash | Object / dictionary | User sessions, entity data |
| List | Ordered queue | Task queues, feeds |
| Set | Unique bag | Tags, deduplication |
| Sorted Set | Ranked list | Leaderboards, rate limiting |

---

## Part 5: Cache Strategies

### 5.1 — Cache-Aside (Lazy Loading)

**The most common pattern.** Your application code handles cache logic manually.

```
1. Request comes in
2. App checks Redis: is this data cached?
   - YES (HIT) → return from Redis
   - NO (MISS) → fetch from DB → store in Redis → return to client
```

```python
def get_product(product_id: int):
    cache_key = f"product:{product_id}"
    
    # 1. Try cache
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)   # cache HIT
    
    # 2. Cache MISS — fetch from DB
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # 3. Store in cache for 5 minutes
    redis.setex(cache_key, 300, json.dumps(product.to_dict()))
    
    return product
```

**Pros:** Simple. Only caches what's actually requested. DB is the source of truth.
**Cons:** First request after cache miss is always slow. Cache can become stale.

---

### 5.2 — Write-Through

Every time data is **written** to the database, it's also written to the cache at the same time.

```
Write request → Write to DB AND write to cache simultaneously
```

```python
def update_product_price(product_id: int, new_price: float):
    # 1. Write to DB
    product = db.query(Product).get(product_id)
    product.price = new_price
    db.commit()
    
    # 2. Write to cache immediately
    cache_key = f"product:{product_id}"
    redis.setex(cache_key, 300, json.dumps({"price": new_price, ...}))
```

**Pros:** Cache is always up to date. No stale reads.
**Cons:** Every write costs double (DB + cache). Cache fills up with data that may never be read.

---

### 5.3 — Write-Behind (Write-Back)

Write to cache first, return success to the user. Write to DB **asynchronously** in the background.

```
Write request → Write to cache → Return success → DB write happens later
```

**Pros:** Super fast writes. User doesn't wait for DB.
**Cons:** Risk of data loss if cache crashes before DB write. Complexity.

**Use in:** High-write, high-throughput systems where brief DB inconsistency is acceptable (analytics, counters, event logging).

---

### 5.4 — Cache Invalidation

**The hardest problem in caching.** When data changes in the DB, how do you make sure the cache doesn't serve stale data?

Strategies:

**1. TTL-based:** Cache expires automatically after N seconds. Simple but data can be stale up to TTL period.

**2. Delete on write:** When you update the DB, explicitly delete the cache key. Next read will be a cache miss and fetch fresh data.
```python
def update_user(user_id, new_data):
    db.update(user_id, new_data)
    redis.delete(f"user:{user_id}")   # invalidate cache
```

**3. Event-based:** Use DB triggers or message queues to signal cache invalidation.

> There are only two hard things in Computer Science: cache invalidation and naming things.
> — Phil Karlton

---

## Part 6: Redis in Python

### 6.1 — Installing the Redis Client

```bash
pip install redis
```

For async (used with FastAPI):
```bash
pip install redis[asyncio]
```

---

### 6.2 — Synchronous Redis Client

```python
import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Basic operations
r.set("greeting", "hello world")
print(r.get("greeting"))   # "hello world"

# With TTL
r.setex("session:abc", 3600, "user_id=42")   # expires in 1 hour

# Hash
r.hset("user:1", mapping={"name": "Ali", "email": "ali@test.com"})
print(r.hgetall("user:1"))   # {'name': 'Ali', 'email': 'ali@test.com'}

# Store JSON
data = {"id": 1, "name": "Laptop", "price": 999.99}
r.setex("product:1", 300, json.dumps(data))
result = json.loads(r.get("product:1"))
```

---

### 6.3 — Async Redis Client (For FastAPI)

```python
import redis.asyncio as aioredis
import json

# In your FastAPI startup
redis_client = aioredis.Redis(host='localhost', port=6379, decode_responses=True)

async def get_product_cached(product_id: int):
    cache_key = f"product:{product_id}"
    
    cached = await redis_client.get(cache_key)
    if cached:
        print(f"Cache HIT for {cache_key}")
        return json.loads(cached)
    
    print(f"Cache MISS for {cache_key}")
    # ... fetch from DB
    product_data = {"id": product_id, "name": "Laptop"}
    
    await redis_client.setex(cache_key, 300, json.dumps(product_data))
    return product_data
```

---

### 6.4 — Full FastAPI + Redis Integration Example

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import redis.asyncio as aioredis
import json

app = FastAPI()
redis_client = aioredis.Redis(host="localhost", port=6379, decode_responses=True)

# --- API Layer ---
@app.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    return await product_service.get_product(product_id, db, redis_client)

# --- Service Layer ---
class ProductService:
    async def get_product(self, product_id: int, db: Session, cache):
        cache_key = f"product:{product_id}"
        
        # 1. Check cache
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 2. Fetch from DB
        product = product_repo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Not found")
        
        # 3. Cache it (5 minutes TTL)
        product_dict = {"id": product.id, "name": product.name, "price": product.price}
        await cache.setex(cache_key, 300, json.dumps(product_dict))
        
        return product_dict
    
    async def update_product_price(self, product_id: int, new_price: float, db, cache):
        # Update DB
        product = product_repo.update_price(db, product_id, new_price)
        
        # Invalidate cache
        await cache.delete(f"product:{product_id}")
        
        return product

product_service = ProductService()
```

---

## Part 7: Advanced Redis Patterns

### 7.1 — Rate Limiting with Redis

**Problem:** Prevent a user from making more than 100 API calls per minute.

**Solution:** Use Redis counters with TTL.

```python
async def check_rate_limit(user_id: str, limit: int = 100, window: int = 60) -> bool:
    key = f"rate_limit:{user_id}:{int(time.time() // window)}"
    
    count = await redis_client.incr(key)
    
    if count == 1:
        # First request in this window — set TTL
        await redis_client.expire(key, window)
    
    if count > limit:
        return False  # Rate limit exceeded
    
    return True  # OK

# In your FastAPI endpoint
@app.get("/api/search")
async def search(query: str, user_id: str):
    if not await check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    # ... proceed
```

**How it works:**
- Key is `rate_limit:user123:28500` (where 28500 = current minute bucket)
- INCR atomically increments the counter
- After 60 seconds, key expires automatically → counter resets

---

### 7.2 — Session Storage

Redis is perfect for storing user sessions (authentication state).

```python
import secrets

async def create_session(user_id: int) -> str:
    session_token = secrets.token_hex(32)
    session_data = json.dumps({"user_id": user_id, "logged_in": True})
    
    # Session lasts 24 hours
    await redis_client.setex(f"session:{session_token}", 86400, session_data)
    
    return session_token

async def get_session(token: str) -> dict | None:
    data = await redis_client.get(f"session:{token}")
    return json.loads(data) if data else None

async def delete_session(token: str):
    await redis_client.delete(f"session:{token}")   # logout
```

---

### 7.3 — Leaderboard with Sorted Sets

```python
async def submit_score(user: str, score: int):
    await redis_client.zadd("game:leaderboard", {user: score})

async def get_top_10():
    results = await redis_client.zrevrange("game:leaderboard", 0, 9, withscores=True)
    return [{"user": user, "score": int(score)} for user, score in results]

async def get_user_rank(user: str):
    rank = await redis_client.zrevrank("game:leaderboard", user)
    return rank + 1 if rank is not None else None  # 1-indexed
```

---

### 7.4 — Pub/Sub (Publish / Subscribe)

Redis can act as a **message broker** — one service publishes messages, others subscribe and react.

```
Publisher (Service A) → Redis Channel → Subscriber (Service B, C, D)
```

```python
# Publisher (when an order is placed)
async def on_order_placed(order_id: int):
    message = json.dumps({"order_id": order_id, "event": "order_placed"})
    await redis_client.publish("orders", message)

# Subscriber (email service listening)
async def email_listener():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("orders")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            await send_confirmation_email(data["order_id"])
```

**Use cases:** Real-time notifications, microservice communication, event-driven architectures.

---

## Part 8: Redis Persistence (Making RAM Durable)

Redis is in-memory, but you don't always want to lose everything on restart. Redis offers two persistence modes:

### 8.1 — RDB (Redis Database Snapshots)

Redis takes a full snapshot of all data and saves to disk at intervals.

```
# In redis.conf
save 900 1      # Save if at least 1 key changed in 900 seconds
save 300 10     # Save if at least 10 keys changed in 300 seconds
save 60 10000   # Save if at least 10000 keys changed in 60 seconds
```

**Pros:** Small file size. Fast restarts.
**Cons:** You can lose data between snapshots (up to 15 min).

### 8.2 — AOF (Append-Only File)

Redis logs every write command to a file. On restart, it replays all commands.

```
# In redis.conf
appendonly yes
appendfsync everysec   # Sync to disk every second
```

**Pros:** Near-zero data loss (max 1 second).
**Cons:** Larger file. Slower restart.

**For caching:** Neither is critical (cache miss is acceptable). For sessions/critical data: use AOF.

---

## Part 9: Redis in Production

### 9.1 — Key Naming Conventions

Bad key names cause chaos in production. Use **namespaced, hierarchical keys**:

```
# Pattern: service:entity:id:field
product:detail:42
product:detail:42:reviews
user:session:abc123
rate_limit:user:42:minute:28500
cache:api:search:q=laptop
```

**Rules:**
- Use `:` as separator
- Keep keys descriptive but not too long
- Use consistent naming across the codebase

---

### 9.2 — Connection Pooling

Opening a new Redis connection per request is expensive. Use a **connection pool**.

```python
# Shared pool — create once at app startup
redis_pool = aioredis.ConnectionPool.from_url(
    "redis://localhost:6379",
    max_connections=50,
    decode_responses=True
)
redis_client = aioredis.Redis(connection_pool=redis_pool)
```

**New term — connection pool:** A pre-created set of connections that are reused instead of opening a new connection every time. Saves ~10ms per request.

---

### 9.3 — Redis Environment Config

```python
# config.py
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

---

## Part 10: Common Mistakes & Anti-Patterns

### ❌ Mistake 1: Caching Everything

Not everything needs to be cached. Caching adds complexity. Only cache what's slow and frequently accessed.

### ❌ Mistake 2: No TTL on Cache Keys

```python
# BAD — this key lives forever
redis.set("product:42", json.dumps(data))

# GOOD — expires in 5 minutes
redis.setex("product:42", 300, json.dumps(data))
```

Keys without TTL pile up and exhaust memory.

### ❌ Mistake 3: Caching Large Blobs

Redis is RAM. Storing 1MB JSON objects in Redis is wasteful. Cache only what's needed.

### ❌ Mistake 4: Not Handling Cache Miss Gracefully

Your app must still work when Redis is down. Always have a fallback to the DB.

```python
async def get_product(product_id):
    try:
        cached = await redis_client.get(f"product:{product_id}")
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"Redis error: {e}")  # log but don't crash
    
    # Always fall back to DB
    return db.query(Product).get(product_id)
```

### ❌ Mistake 5: Cache Stampede

**Cache stampede (thundering herd):** Cache key expires → 1,000 simultaneous requests all miss and hit the DB at once.

**Solution:** Use a lock (Redis `SET NX`) or probabilistic early expiration.

---

## Part 11: Quick Reference

### Commands Cheat Sheet

```bash
# Strings
SET key value
GET key
SETEX key seconds value
DEL key
EXISTS key
TTL key
INCR key
INCRBY key amount

# Hashes
HSET key field value
HGET key field
HGETALL key
HDEL key field
HMSET key field1 v1 field2 v2

# Lists
RPUSH key value     # push right
LPUSH key value     # push left
RPOP key            # pop right
LPOP key            # pop left
LRANGE key 0 -1     # get all
LLEN key

# Sets
SADD key member
SMEMBERS key
SISMEMBER key member
SCARD key
SINTER key1 key2    # intersection

# Sorted Sets
ZADD key score member
ZRANGE key 0 -1 WITHSCORES   # ascending
ZREVRANGE key 0 -1            # descending
ZRANK key member
ZINCRBY key amount member
```

---

## Summary: The Mental Model

```
User Request
    ↓
FastAPI Endpoint
    ↓
Service Layer → Check Redis (1–2ms) → HIT? Return immediately ✅
    ↓
   MISS
    ↓
Repository Layer → Query PostgreSQL (50–200ms)
    ↓
Store result in Redis with TTL
    ↓
Return to user
```

**Redis is not a replacement for your database.** It's a speed layer on top of it.

**The stack:**
- **PostgreSQL** → source of truth, durable, queryable
- **Redis** → speed layer, temporary, fast
- **Your app** → decides what to cache, when to invalidate

---

## Revision Notes

**Key terms to memorize:**

| Term | One-line definition |
|---|---|
| Latency | Time from request to response |
| Cache | Fast temporary storage layer |
| Cache HIT | Data found in cache |
| Cache MISS | Data not in cache, went to DB |
| TTL | Expiry time on a cache entry |
| Eviction | Removing old data when cache is full |
| LRU | Evict least recently used data |
| Cache-aside | App manually handles cache logic |
| Write-through | Write to DB and cache simultaneously |
| Cache invalidation | Removing stale data from cache |
| Redis | In-memory data structure store |
| Sorted Set | Redis structure for ranked data |
| Pub/Sub | Message broadcast via Redis channels |
| Rate limiting | Restricting requests per time window |
| Connection pool | Reusable pre-opened connections |

---

*End of Lecture — Cache & Latency Reduction (Redis)*