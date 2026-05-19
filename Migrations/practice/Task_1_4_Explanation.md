# 🎓 Conceptual Master-Class: The Version Table & Out-of-Sync Recovery (Task 1.4)

This textbook breaks down the single most critical table in database migrations: `alembic_version`. We will explore what it stores, why it exists, and the catastrophic results of manual tampering.

---

## 🏛️ 1. What is the `alembic_version` Table?

The `alembic_version` table is the **only source of truth** for Alembic.
* It is automatically created on your first upgrade.
* It contains exactly **one column**: `version_num` (VARCHAR).
* It contains exactly **one row**: the active revision ID of your schema.

```text
       migrations_practice Database
       ┌──────────────────────────────┐
       │ alembic_version              │
       ├──────────────────────────────┤
       │ version_num                  │
       ├──────────────────────────────┤
       │ fd0da25147e8                 │
       └──────────────────────────────┘
```

Alembic does **not** scan your physical tables (like checking if the `users` table exists) to determine what version the database is at. 
Instead, it simply queries `SELECT version_num FROM alembic_version;`. It trusts this single value blindly.

---

## 💥 2. What happens if you manually delete that row?

Imagine you open your database client and execute:
```sql
DELETE FROM alembic_version;
```
Or you drop the `alembic_version` table entirely. What happens when you run `alembic upgrade head`?

### The Sequence of Events:
1. **Empty Tracker Check:** Alembic connects to your database, queries `alembic_version`, and sees **nothing** (value is empty / state `<base>`).
2. **False Assumption:** Alembic assumes: *"Aha! This is a completely fresh database with zero tables created!"*
3. **Execution Collision:** It looks at your migration files, finds your very first migration (`318ebe7cffc8`), and tries to run its `upgrade()` function (which executes `CREATE TABLE users ...`).
4. **The Crash:** PostgreSQL immediately throws an error: `Relation "users" already exists`. The command fails.

### **The Lesson:**
If your `alembic_version` tracker becomes out of sync with your physical tables, **Alembic is blinded**. It will try to recreate things that already exist, resulting in crashes.

---

## 🛠️ 3. How do we repair this in the real world?

If a database version becomes out of sync manually, we use **`alembic stamp`**.
Running:
```powershell
alembic stamp fd0da25147e8
```
Does **not** run any DDL operations (it won't create or drop tables). It simply connects to the database and forces the value inside the `alembic_version` table to match the revision you specified. This "stamps" the version tracker to synchronize it back with reality!
