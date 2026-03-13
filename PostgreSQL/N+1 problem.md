The **N+1 problem** is a very common **database performance issue** that happens when an application executes **one query to fetch a list of records, and then executes an additional query for each record** to fetch related data.

It is especially common in **ORM frameworks** like:

* Laravel Eloquent
* Django ORM
* Ruby on Rails ActiveRecord
* Hibernate
* Entity Framework
* Sequelize

---

# 1. Basic Idea of the N+1 Problem

Suppose you want to get:

* All **posts**
* The **author of each post**

### What you expect

You expect the system to use **2 queries**:

1 query → fetch posts
1 query → fetch authors

### What actually happens (N+1)

1 query → fetch posts
N queries → fetch author for each post

Total queries = **N + 1**

If there are **100 posts**, the system executes:

```
1 + 100 = 101 queries
```

This is the **N+1 problem**.

---

# 2. Example

### Tables

**posts**

| id | title  | author_id |
| -- | ------ | --------- |
| 1  | Post A | 1         |
| 2  | Post B | 2         |
| 3  | Post C | 1         |

**authors**

| id | name  |
| -- | ----- |
| 1  | John  |
| 2  | Alice |

---

# 3. Code That Causes N+1

Example (Laravel / ORM style)

```php
$posts = Post::all();

foreach ($posts as $post) {
    echo $post->author->name;
}
```

### What the ORM does internally

Query 1:

```
SELECT * FROM posts;
```

Then for each post:

```
SELECT * FROM authors WHERE id = 1;
SELECT * FROM authors WHERE id = 2;
SELECT * FROM authors WHERE id = 1;
```

If there are **N posts**, this results in **N additional queries**.

---

# 4. Visualization

Example with **5 posts**

| Step | Query                    |
| ---- | ------------------------ |
| 1    | SELECT posts             |
| 2    | SELECT author for post 1 |
| 3    | SELECT author for post 2 |
| 4    | SELECT author for post 3 |
| 5    | SELECT author for post 4 |
| 6    | SELECT author for post 5 |

Total queries:

```
N + 1
5 + 1 = 6 queries
```

---

# 5. Why N+1 Happens

The reason is **lazy loading**.

Lazy loading means:

> Related data is fetched **only when accessed**.

Example:

```
$post->author
```

When the code accesses `author`, the ORM executes a **new query**.

---

# 6. Lazy Loading vs Eager Loading

## Lazy Loading (causes N+1)

Load data **only when accessed**

```
posts
   └── author (query executed later)
```

Example:

```php
$post->author
```

Each access = new query.

---

## Eager Loading (solution)

Load related data **in advance**

Example:

```php
$posts = Post::with('author')->get();
```

Now the queries become:

Query 1

```
SELECT * FROM posts;
```

Query 2

```
SELECT * FROM authors WHERE id IN (1,2);
```

Total queries = **2**

Instead of **101 queries**.

---

# 7. SQL Version (JOIN)

Another solution is using **JOIN**.

```sql
SELECT posts.*, authors.name
FROM posts
JOIN authors ON posts.author_id = authors.id;
```

Now everything comes in **one query**.

---

# 8. Real Example (Huge Impact)

Imagine:

* 500 products
* each product has a category

Bad code:

```
1 query → products
500 queries → categories
```

Total:

```
501 queries
```

Correct approach:

```
1 query → products
1 query → categories
```

or

```
1 JOIN query
```

Huge performance improvement.

---

# 9. Types of N+1 Problems

### 1️⃣ Simple N+1

Example:

```
Posts → Author
```

---

### 2️⃣ Nested N+1

Example:

```
Posts → Comments → User
```

Bad queries:

```
1 query posts
N queries comments
N queries users
```

This can become:

```
1 + N + N²
```

Very dangerous.

---

### 3️⃣ Hidden N+1

Occurs when the ORM **implicitly loads relationships inside loops**.

Example:

```
foreach users
   foreach orders
```

Queries explode.

---

# 10. Detecting N+1

Common tools:

### Laravel

```
Laravel Debugbar
Clockwork
Telescope
```

---

### Django

```
django-debug-toolbar
```

---

### General

Log queries and count them.

---

# 11. How to Fix N+1

### 1️⃣ Eager Loading

Laravel

```php
Post::with('author')->get();
```

Django

```
select_related()
prefetch_related()
```

---

### 2️⃣ Use JOIN

SQL join instead of ORM lazy loading.

---

### 3️⃣ Batch Loading

Load data using **IN queries**

```
SELECT * FROM authors WHERE id IN (...)
```

---

### 4️⃣ Cache Results

Use caching for repeated queries.

---

# 12. Real Production Impact

N+1 can cause:

* slow APIs
* high DB load
* server crashes
* bad scaling
* timeouts

Example:

```
10 users → 11 queries
100 users → 101 queries
1000 users → 1001 queries
```

---

# 13. Quick Mental Rule

Whenever you see:

```
for item in items:
    item.related
```

⚠️ Possible **N+1 problem**

---

# 14. Simple Summary

| Concept | Meaning                     |
| ------- | --------------------------- |
| N       | number of records           |
| +1      | initial query               |
| Problem | extra query for each record |
| Cause   | lazy loading                |
| Fix     | eager loading or joins      |

---

# 15. One-Line Definition

**N+1 problem = executing one query to get N records and then executing N additional queries to fetch related data.**

