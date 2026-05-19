# Database Migrations — Practice Task Curriculum

No solutions. Just tasks. You figure it out, you learn it.

---

## PHASE 1 — Getting Your Hands Dirty

**Goal:** Understand what a migration actually is and feel the core loop.

---

**Task 1.1 — Environment Setup**
Set up a fresh FastAPI project with SQLAlchemy and Alembic. Connect Alembic to a PostgreSQL database. Your only success condition is running `alembic current` without errors.

---

**Task 1.2 — First Migration**
Create a `User` model with just `id` and `email`. Generate your first migration using autogenerate. Inspect the generated file and understand every single line before you run it. Apply it. Verify the table exists in your database.

---

**Task 1.3 — The Downgrade**
Downgrade that migration. Verify the table is gone from the database. Upgrade again. Do this cycle 3 times until it feels natural.

---

**Task 1.4 — The Version Table**
Open your database client and find the `alembic_version` table. Understand what it stores and why. What happens if you delete that row manually and then run `alembic upgrade head`?

---

**Task 1.5 — Named Migrations**
Create 3 more migrations one by one, each adding a column to the `User` table. Name each migration meaningfully. After all three, run `alembic history` and read the output. Understand the chain.

---

## PHASE 2 — Schema Operations

**Goal:** Get comfortable with every type of schema change.

---

**Task 2.1 — Add and Remove**
Add a `bio` column to users. Verify. Then write a new migration to drop it. Verify again. Understand why you should never edit an already-applied migration file.

---

**Task 2.2 — Constraints**
Create a `Post` model with a foreign key to `User`. Write the migration manually this time — do not use autogenerate. Apply it. Break it intentionally by inserting a post with a non-existent user ID and observe the database error.

---

**Task 2.3 — Indexes**
Add an index on `User.email`. Then add a unique index on `Post.slug`. Use `alembic upgrade head`. Now check your database — confirm both indexes exist.

---

**Task 2.4 — Column Type Change**
Change a column's type — for example, an `Integer` age field to `String`. Figure out what problems this causes. Research how to handle existing data during a type change.

---

**Task 2.5 — Autogenerate Limits**
Make a change to your model that autogenerate cannot detect. Run `alembic revision --autogenerate` and observe that the generated file is empty or wrong. Write that migration manually. Understand the gap between what Alembic sees and what your database actually needs.

---

## PHASE 3 — Data Migrations

**Goal:** Learn to move and transform real data safely inside migrations.

---

**Task 3.1 — Seed Data via Migration**
Write a migration that inserts default rows into a `roles` table (e.g., `admin`, `user`, `moderator`). Make sure the downgrade deletes exactly those rows and nothing else.

---

**Task 3.2 — Column Split**
You have a `full_name` column on `User`. Split it into `first_name` and `last_name` inside a migration. Existing data must be preserved. The old column must be removed. The downgrade must reconstruct `full_name` from the two new columns.

---

**Task 3.3 — The ORM Trap**
Try writing a data migration using your SQLAlchemy ORM models directly inside the migration file. Apply it. Then change your model and apply another migration. Now try to run all migrations from scratch on a fresh database and observe what breaks. Understand why you should never use ORM models inside migration files.

---

**Task 3.4 — Backfill with Batching**
You have 1 million rows (simulate this with a script that inserts bulk data). Write a migration that updates a column on every row. Do it in batches of 1000 rows so it doesn't lock the table. Research why this matters in production.

---

## PHASE 4 — Team Scenarios

**Goal:** Handle the messy reality of multiple developers working simultaneously.

---

**Task 4.1 — Simulate Two Developers**
Create two Git branches from the same base revision. On branch A, add a `posts` table. On branch B, add a `comments` table. Both will have the same `down_revision`. Merge both branches. Observe what `alembic heads` shows. Fix it.

---

**Task 4.2 — The Merge Migration**
Resolve the conflict from Task 4.1 using `alembic merge`. Understand what the generated merge migration looks like and why it has two parents. Apply it successfully.

---

**Task 4.3 — Stamp Recovery**
Manually create a table in your database without using Alembic (raw SQL). Now write a migration for that same table. Alembic will try to create it again and fail. Use `alembic stamp` to resolve this without data loss. Understand exactly what stamping does and does not do.

---

**Task 4.4 — Squashing History**
You have 15 small migrations on a feature branch that hasn't been merged. Squash them into a single clean migration before merging. Research the correct way to do this without breaking the chain.

---

## PHASE 5 — Production Thinking

**Goal:** Think about what happens when real users are on the system.

---

**Task 5.1 — Locking Research**
Research which DDL operations in PostgreSQL take an `ACCESS EXCLUSIVE` lock (the dangerous one that blocks reads and writes). List them. Then research which operations are safe to run on a live table. This is purely research — no code — but it's critical knowledge.

---

**Task 5.2 — Nullable First Pattern**
Rename a column from `username` to `handle` without any downtime. You cannot do this in a single migration. Figure out the multi-step expand/contract pattern and implement it across three separate migrations, each deployable independently.

---

**Task 5.3 — Startup Migration**
Configure your FastAPI app to run `alembic upgrade head` automatically on startup. Test that it works in a fresh environment. Then think about what happens if two instances of your app start simultaneously — research this problem and write down your findings.

---

**Task 5.4 — Environment-Driven Config**
Remove the hardcoded database URL from `alembic.ini`. Drive it entirely from environment variables. Make sure `alembic upgrade head` works from both the command line and from inside the app with no code changes between environments.

---

**Task 5.5 — Destructive Migration Safety**
Write a migration that drops a column that still has data in it. Before running it in "production" (your local DB with seeded data), figure out: How do you verify data is safe to drop? What is a safe checklist before running a destructive migration on a live system?

---

## PHASE 6 — Senior Level

**Goal:** Handle the patterns that separate mid-level from senior engineers.

---

**Task 6.1 — Test Your Migrations**
Write automated tests that do the following: upgrade to head, verify the schema is exactly what you expect, then downgrade to base, and verify everything is gone. Every migration must be reversible and your test suite must enforce it.

---

**Task 6.2 — Multi-Schema Migrations**
Design a system where each tenant gets their own PostgreSQL schema (e.g., `tenant_acme`, `tenant_globex`). Write an `env.py` that runs every migration across all tenant schemas in a single `alembic upgrade head` call.

---

**Task 6.3 — Trigger via Migration**
Write a migration that creates a PostgreSQL audit trigger — whenever a `User` row is updated, it logs the old and new values into an `audit_log` table. The downgrade must cleanly remove both the trigger and the function. No ORM, raw SQL only.

---

**Task 6.4 — Migration That Cannot Be Undone**
Some migrations are genuinely irreversible (e.g., you've deleted data that cannot be reconstructed). Write a migration where `downgrade()` raises an explicit error with a clear message explaining why the rollback is not possible. Research when this is the right decision.

---

**Task 6.5 — Performance Migration**
Your `posts` table has 5 million rows (simulate it). You need to add a `NOT NULL` column with a default value. A naive `ADD COLUMN ... NOT NULL DEFAULT` will rewrite the entire table and lock it. Research the PostgreSQL-safe way to do this and implement it across the correct number of migration steps.

---

**Task 6.6 — Full CI Pipeline**
Set up a GitHub Actions workflow (or any CI) that does the following on every pull request: spins up a test PostgreSQL instance, runs all migrations from base to head, runs all migrations from head back to base, and fails the PR if any step fails. No migration merges without passing this pipeline.

---

## The Order Is Non-Negotiable

```
Do not skip ahead.
Do not read solutions before attempting.
If you are stuck for more than 30 minutes, research — don't ask for the answer immediately.
The stuck feeling is where the learning happens.
```

Start with Task 1.1. Come back when you're done with a phase and we'll review your approach before you move on.