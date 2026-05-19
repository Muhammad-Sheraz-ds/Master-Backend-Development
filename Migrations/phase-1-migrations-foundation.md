# Phase 1 — Foundation: What Is a Migration and the Core Loop

## What Problem Does a Migration Solve?

Imagine you are building a FastAPI app. You create a `users` table manually in your local
database. Your teammate does the same on their machine — but slightly differently. They added
an extra column. Now your schemas are out of sync. You deploy to production and it breaks
because production has a third version of the schema.

This is the problem migrations solve.

A migration is a **file that describes a change to your database schema**, written in code,
stored in your repository, and applied in a controlled order. Every developer runs the same
migrations. Every environment ends up with the same schema. Nothing is done manually.

---

## The Git Analogy

The easiest way to understand migrations is to compare them to Git.

| Git | Alembic (Migrations) |
|-----|----------------------|
| `git commit` | `alembic revision` — create a new migration |
| `git log` | `alembic history` — see all migrations in order |
| `git checkout` | `alembic downgrade` — go back to a previous state |
| `git push` | `alembic upgrade head` — apply all pending migrations |

Just like Git tracks changes to your code over time, Alembic tracks changes to your database
schema over time.

---

## Anatomy of a Migration File

Every migration file has two functions and two identifiers.

```
revision = 'a1b2c3d4'        ← this migration's unique ID
down_revision = 'z9y8x7w6'   ← the ID of the migration before this one

def upgrade():
    # what to do when applying this migration (moving forward)

def downgrade():
    # what to undo if you need to reverse this migration (going back)
```

The `upgrade` function moves your schema forward. The `downgrade` function reverses it.
This reversibility is what separates migrations from just running raw SQL by hand.

---

## The Core Loop

This is the fundamental cycle you will repeat thousands of times as a backend engineer.

```
1. Change your model (add a column, create a table, etc.)
2. Generate a migration file  →  alembic revision --autogenerate -m "description"
3. Read the generated file    →  understand every line before running it
4. Apply it                   →  alembic upgrade head
5. Verify in the database     →  check the table/column actually exists
6. If needed, reverse it      →  alembic downgrade -1
```

Step 3 is where most beginners skip and later regret it. Alembic's autogenerate is helpful
but not perfect. It cannot detect every type of change. Always read what it generated.

---

## What `alembic_version` Is

When you run your first migration, Alembic creates a special table in your database called
`alembic_version`. It has one row with one column — the revision ID of the last migration
that was applied.

```
alembic_version
───────────────
version_num
───────────────
a1b2c3d4
```

Every time you run `alembic upgrade`, it reads this table, figures out which migrations have
not been applied yet, and runs them in order. Every time you run `alembic downgrade`, it
runs the `downgrade()` function and updates this table to the previous revision ID.

This table is how Alembic knows where your database currently is in the migration chain.

---

## What `alembic history` Shows You

Once you have several migrations, running `alembic history` shows you the chain:

```
a1b2c3d4 -> b2c3d4e5 (head)  add_bio_to_users
z9y8x7w6 -> a1b2c3d4         add_name_to_users
<base>   -> z9y8x7w6         create_users_table
```

Each migration points to its parent via `down_revision`. This forms a linked chain from
the very first migration (`<base>`) all the way to the latest one (`head`).

`head` always means the most recent migration. `base` means the beginning — no migrations
applied, empty schema.

---

## Autogenerate vs Manual

Alembic can compare your SQLAlchemy models to the actual database and generate a migration
automatically. This is called autogenerate.

```bash
alembic revision --autogenerate -m "create_users_table"
```

It works well for simple cases: creating tables, adding columns, dropping columns.

It does **not** work for everything. It cannot detect:
- Changes inside stored procedures or triggers
- Server-side default values in many cases
- Data changes (autogenerate is for schema only)
- Some index variations

For anything autogenerate misses, you write the migration manually.

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

---

## The Mental Model in One Sentence

A migration is a versioned, reversible, code-reviewed change to your database schema that
every developer and every environment applies in exactly the same order.

---

## What You Will Do in Phase 1 Practice Tasks

The five tasks in Phase 1 are designed to make this mental model physical and real.

- **Task 1.1** — you set up the environment and make Alembic aware of your database.
- **Task 1.2** — you generate and apply your very first migration and see it work.
- **Task 1.3** — you run the upgrade/downgrade cycle repeatedly until the loop feels natural.
- **Task 1.4** — you inspect the `alembic_version` table directly and understand what Alembic
  is actually tracking under the hood.
- **Task 1.5** — you build a short chain of migrations and read `alembic history` to see how
  the version chain grows.

By the end of Phase 1 you should be able to answer these questions without thinking:

- What is a migration and why does it exist?
- What does `upgrade` do? What does `downgrade` do?
- What is stored in `alembic_version` and why?
- What is the difference between `head` and `base`?
- Why should you always read a generated migration before running it?
