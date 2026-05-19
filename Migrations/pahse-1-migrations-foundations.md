# Phase 1 — Foundation: What Is a Migration and the Core Loop

---

## What Problem Does a Migration Solve?

Imagine you are building a backend application. You create a `users` table manually in your
local database. Your teammate does the same on their machine — but slightly differently. They
added an extra column. Now your schemas are out of sync. You deploy to production and it breaks
because production has a third version of the schema.

This is the problem migrations solve — in every language, every framework, every team.

A migration is a **file that describes a change to your database schema**, written in code,
stored in your repository, and applied in a controlled order. Every developer runs the same
migrations. Every environment ends up with the same schema. Nothing is done manually.

---

## Migration Tools Across the Ecosystem

Every major backend ecosystem has a dedicated migration tool. They all solve the same problem —
the tool name and syntax differ, but the concept is identical.

| Language / Framework | Migration Tool |
|----------------------|----------------|
| Python + SQLAlchemy / FastAPI | **Alembic** |
| Python + Django | **Django Migrations** (built-in, `manage.py migrate`) |
| Node.js + Sequelize | **Sequelize CLI** (`sequelize db:migrate`) |
| Node.js + TypeORM | **TypeORM Migrations** |
| Node.js + Prisma | **Prisma Migrate** (`prisma migrate deploy`) |
| Ruby on Rails | **Active Record Migrations** (built-in, `rails db:migrate`) |
| PHP + Laravel | **Laravel Migrations** (built-in, `php artisan migrate`) |
| Java + Spring Boot | **Flyway** or **Liquibase** |
| Go | **golang-migrate** or **GORM Migrations** |

When you read a job description mentioning "Flyway migrations" or "Prisma Migrate" — they are
all doing the same thing. The vocabulary you learn here transfers directly.

**In this curriculum, the tool is Alembic** — the standard migration tool for Python projects
using SQLAlchemy, which is the ORM used with FastAPI.

---

## What Is an ORM — and Why It Matters for Migrations

Before understanding Alembic, you need to understand where it fits.

An **ORM (Object Relational Mapper)** is a library that lets you define your database tables
as Python classes instead of writing raw SQL. In Python, the most widely used ORM is
**SQLAlchemy**. FastAPI projects almost always use SQLAlchemy.

```
Your Python Class  →  SQLAlchemy ORM  →  Database Table
```

When you define a model class in SQLAlchemy, you are describing what a table should look like.
Alembic reads those class definitions, compares them to what currently exists in the database,
and generates migration files to close the gap.

In other ecosystems, the same relationship exists:
- In **Django**, you define models as Python classes — Django's built-in migration system reads them.
- In **Laravel**, you define models as PHP classes — Laravel migrations describe the schema changes.
- In **Prisma** (Node.js), you define a `schema.prisma` file — Prisma Migrate reads it.
- In **TypeORM** (Node.js), you define entity classes in TypeScript — TypeORM reads them.

The pattern is always: **define your schema in code → tool generates migration → migration
applies change to database.**

---

## The Git Analogy

The easiest way to understand migrations is to compare them to Git — a tool you already know.

| Git Concept | Migration Equivalent | Alembic Command |
|-------------|----------------------|-----------------|
| A commit | A migration file | `alembic revision` |
| Commit history | Migration history | `alembic history` |
| Checkout old commit | Revert to old schema | `alembic downgrade` |
| Apply latest commits | Apply pending migrations | `alembic upgrade head` |
| The latest commit | The latest migration | `head` |
| The very first state | Empty schema | `base` |

Just like Git tracks changes to your **code** over time, a migration tool tracks changes to
your **database schema** over time. Both give you a reproducible, reversible, auditable
history.

---

## Anatomy of a Migration File

This is what Alembic generates. Every migration tool generates something similar — the
structure differs but the two core functions exist everywhere.

```python
# Alembic migration file (Python)

revision = 'a1b2c3d4'        # this migration's unique ID
down_revision = 'z9y8x7w6'   # the ID of the migration before this one

def upgrade():
    # What to do when moving FORWARD (applying this change)
    # Example: create a table, add a column

def downgrade():
    # What to UNDO if you need to reverse this migration
    # Example: drop that table, remove that column
```

For comparison, the same concept looks like this in other tools:

- **Django** — generates a Python file with `operations = [migrations.CreateModel(...)]`
- **Prisma** — generates a `.sql` file with `CREATE TABLE` and tracks it automatically
- **Rails** — generates a Ruby file with `def change` containing `create_table :users`
- **Flyway** — you write a raw `.sql` file named `V1__create_users.sql`
- **TypeORM** — generates a TypeScript file with `up()` and `down()` methods

The underlying idea is always the same: **a versioned file describing one schema change,
with a way to apply it and a way to reverse it.**

---

## The Core Loop

This is the fundamental cycle you will repeat regardless of which migration tool you use.
In Alembic the commands look like this, but the loop itself is universal.

```
1. Change your model        →  edit your SQLAlchemy class (or Prisma schema, or Django model)
2. Generate migration       →  alembic revision --autogenerate -m "description"
3. Read the generated file  →  understand every line before running it
4. Apply it                 →  alembic upgrade head
5. Verify in the database   →  confirm the table / column actually exists
6. Reverse if needed        →  alembic downgrade -1
```

Step 3 is where most beginners skip and later regret it. Alembic's autogenerate is helpful
but not perfect — it cannot detect every type of change. Always read what it generated before
running it.

---

## What the Version Tracking Table Is

When you run your first migration, Alembic creates a special tracking table in your database
called `alembic_version`. It contains one row: the revision ID of the last migration applied.

```
alembic_version
───────────────
version_num
───────────────
a1b2c3d4
```

Every migration tool does this exact same thing — they each have their own tracking table:

| Tool | Tracking Table Name |
|------|---------------------|
| **Alembic** (Python / FastAPI) | `alembic_version` |
| **Django** (Python) | `django_migrations` |
| **Rails** (Ruby) | `schema_migrations` |
| **Flyway** (Java) | `flyway_schema_history` |
| **Liquibase** (Java) | `databasechangelog` |
| **Prisma** (Node.js) | `_prisma_migrations` |
| **TypeORM** (Node.js) | `migrations` |

This table is how the tool knows which migrations have already been applied and which ones
still need to run. When you run `alembic upgrade head`, Alembic reads this table, figures
out where the database currently is, and runs only the migrations that have not been applied
yet — in the correct order.

---

## What `alembic history` Shows You

Once you have several migrations, `alembic history` shows you the chain:

```
a1b2c3d4 -> b2c3d4e5 (head)   add_bio_to_users
z9y8x7w6 -> a1b2c3d4          add_name_to_users
<base>   -> z9y8x7w6          create_users_table
```

Each migration points to its parent via `down_revision`. This forms a linked list from the
very first migration (`<base>`) up to the most recent one (`head`).

- `head` = the latest migration. What your database should look like right now.
- `base` = no migrations applied at all. Completely empty schema.

Running `alembic upgrade head` takes your database from wherever it currently is all the way
up to `head` — applying every migration in between in the correct order.

In other tools this same concept is expressed differently:
- In **Django**: `python manage.py showmigrations`
- In **Rails**: `rails db:migrate:status`
- In **Prisma**: `prisma migrate status`

---

## Autogenerate vs Manual

Alembic can compare your SQLAlchemy models to what currently exists in the database and
generate a migration file automatically. This is called **autogenerate**.

```bash
alembic revision --autogenerate -m "create_users_table"
```

This is the same idea as:
- `python manage.py makemigrations` in Django
- `prisma migrate dev` in Prisma
- `rails generate migration AddEmailToUsers` in Rails
- `typeorm migration:generate` in TypeORM

Autogenerate works well for simple cases: creating tables, adding columns, dropping columns,
adding indexes.

It does **not** work for everything. It cannot detect:
- Changes inside stored procedures or triggers
- Server-side default values in many cases
- Data changes (autogenerate is for schema structure only)
- Some index and constraint variations

For anything autogenerate misses, you write the migration manually. This is true in every
tool — autogenerate is a starting point, not a guarantee.

---

## Why Downgrade Matters

Every migration you write should have a working `downgrade()`. Here is why.

You deploy a new feature to production. Something breaks. You need to roll back — not just
your code, but your database schema too. Without a working downgrade, your only option is
manual intervention on a live production database. That is a stressful, error-prone situation.

A working downgrade turns a crisis into a single command.

```bash
alembic downgrade -1    # go back one migration
alembic downgrade base  # go all the way back to empty schema
```

Every serious migration tool supports this:
- **Django**: `python manage.py migrate app_name 0001`
- **Rails**: `rails db:rollback STEP=1`
- **Flyway**: undo migrations (Flyway Teams feature)
- **Prisma**: does not support automatic downgrades — you write a new migration manually

The command differs. The principle is universal.

---

## Schema-First vs Code-First Migrations

There are two philosophies you will encounter across tools:

**Code-first (Alembic, Django, TypeORM)**
You define your schema as language classes. The tool reads your code and generates SQL.
You work at the Python/TypeScript layer — rarely write raw SQL yourself.

**SQL-first (Flyway, Liquibase)**
You write the SQL migration files yourself. The tool just tracks and applies them in order.
Common in Java and enterprise environments where DBAs own the schema.

**Schema-file-first (Prisma)**
You edit a single `schema.prisma` file describing your entire schema. The tool diffs it
against the current database and generates the SQL automatically.

**Alembic is code-first.** You define models in SQLAlchemy, run autogenerate, and Alembic
produces Python migration files that internally generate the correct SQL for your target
database — PostgreSQL, MySQL, SQLite, and others.

---

## The Mental Model in One Sentence

A migration is a versioned, reversible, code-reviewed change to your database schema that
every developer and every environment applies in exactly the same order — regardless of
which tool or language you use.

---

## What You Will Do in Phase 1 Practice Tasks

The five tasks in Phase 1 are designed to make this mental model physical and real.

- **Task 1.1** — Set up the environment. Connect Alembic to your database. Make `alembic current`
  run without errors.
- **Task 1.2** — Generate and apply your very first migration. See the table appear in the database.
- **Task 1.3** — Run the upgrade and downgrade cycle repeatedly until the loop feels natural.
- **Task 1.4** — Inspect the `alembic_version` table directly. Understand what Alembic is
  tracking under the hood and what happens if you tamper with it.
- **Task 1.5** — Build a short chain of migrations. Run `alembic history`. See the version
  chain grow.

By the end of Phase 1 you should be able to answer all of these without hesitation:

- What is a migration and why does it exist?
- What does `upgrade` do? What does `downgrade` do?
- What is stored in `alembic_version` and why?
- What is the difference between `head` and `base`?
- Why should you always read a generated migration before running it?
- If someone says "we use Flyway" or "run `prisma migrate deploy`" — what are they actually doing?