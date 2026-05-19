# Database Migrations: Beginner to Senior — FastAPI/Alembic Masterplan

Here's your complete structured practice curriculum. Pure implementation, no fluff.

---

## 🗺️ The Map

```
PHASE 1 — Foundation        (Concepts + First Migration)
PHASE 2 — Core Operations   (CRUD on Schema, Data Migrations)
PHASE 3 — Team Workflows    (Branching, Merging, Conflicts)
PHASE 4 — Production Grade  (Zero-downtime, Rollbacks, CI/CD)
PHASE 5 — Senior Patterns   (Multi-tenancy, Audit, Testing)
```

---

## PHASE 1 — Foundation

### Chapter 1.1 — What Is a Migration (The Mental Model)

**Concept first:**

A migration is a **versioned, reversible change to your database schema**, stored as code in your repository.

Think of it like `git` but for your database structure:

```
git commit  →  alembic revision
git log     →  alembic history
git checkout →  alembic downgrade
git push    →  alembic upgrade head
```

Without migrations, you change your DB manually. Two problems:
- Your teammate's DB is now different from yours
- Production is different from both

Migrations solve this by making schema changes **reproducible, trackable, and reversible**.

---

### Chapter 1.2 — Project Setup from Zero

**Build this project structure:**

```
migrations-masterclass/
├── app/
│   ├── __init__.py
│   ├── database.py       ← SQLAlchemy engine + session
│   ├── models.py         ← Your ORM models
│   └── main.py           ← FastAPI app
├── alembic/
│   ├── env.py            ← Migration environment (brain of Alembic)
│   └── versions/         ← All your migration files live here
├── alembic.ini           ← Alembic config
├── .env
└── requirements.txt
```

**Install:**
```bash
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-dotenv
```

**`app/database.py`:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/migrations_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Initialize Alembic:**
```bash
alembic init alembic
```

This creates `alembic.ini` and the `alembic/` folder.

---

### Chapter 1.3 — Connecting Alembic to Your Models

This is where 90% of beginners get confused. Open `alembic/env.py` and make these changes:

```python
# alembic/env.py  — the two critical changes

from app.database import Base          # ← import your Base
from app import models                 # ← import models so Base.metadata knows about them

# Find this line and replace it:
# target_metadata = None
target_metadata = Base.metadata        # ← point Alembic at your models
```

In `alembic.ini`, set your DB URL:
```ini
sqlalchemy.url = postgresql://user:pass@localhost/migrations_db
```

Or better, use env variable (covered in Phase 4).

---

### Chapter 1.4 — Your First Migration

**Define a model:**
```python
# app/models.py
from app.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
```

**Generate migration (autogenerate):**
```bash
alembic revision --autogenerate -m "create_users_table"
```

Open the generated file in `alembic/versions/`. You'll see:

```python
def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('users')   # ← THIS is what makes it reversible
```

**Apply it:**
```bash
alembic upgrade head
```

**✅ Practice Task:** Create this, run it, then check your DB. Table exists. Now run `alembic downgrade -1`. Table gone. Run `alembic upgrade head` again. This is the core loop.

---

## PHASE 2 — Core Schema Operations

### Chapter 2.1 — The 6 Operations You'll Use Daily

```python
# Adding a column
op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))

# Dropping a column
op.drop_column('users', 'age')

# Renaming a column
op.alter_column('users', 'name', new_column_name='full_name')

# Adding an index
op.create_index('ix_users_email', 'users', ['email'], unique=True)

# Adding a foreign key
op.add_column('posts', sa.Column('user_id', sa.Integer(), 
              sa.ForeignKey('users.id'), nullable=False))

# Changing column type
op.alter_column('users', 'age', 
                existing_type=sa.Integer(),
                type_=sa.String())
```

**✅ Practice Task:** Build a blog schema incrementally with one migration per change:
1. `create_users_table`
2. `add_bio_to_users`
3. `create_posts_table` (with FK to users)
4. `add_published_at_to_posts`
5. `create_tags_table` + `create_post_tags_association`

Run `alembic history` after each. See the version chain.

---

### Chapter 2.2 — Data Migrations (The Dangerous One)

Schema migrations change structure. **Data migrations change actual data.** This is where bugs become irreversible.

**Scenario:** You have `name` (single field). You're splitting it to `first_name` + `last_name`.

```python
def upgrade() -> None:
    # Step 1: Add new columns as NULLABLE first
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    
    # Step 2: Migrate the data
    op.execute("""
        UPDATE users 
        SET 
            first_name = SPLIT_PART(name, ' ', 1),
            last_name = NULLIF(SPLIT_PART(name, ' ', 2), '')
        WHERE name IS NOT NULL
    """)
    
    # Step 3: Now make them NOT NULL (data is already there)
    op.alter_column('users', 'first_name', nullable=False)
    
    # Step 4: Drop old column
    op.drop_column('users', 'name')

def downgrade() -> None:
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    op.execute("""
        UPDATE users 
        SET name = CONCAT(first_name, ' ', COALESCE(last_name, ''))
    """)
    op.alter_column('users', 'name', nullable=False)
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

**⚠️ Rule:** Never use your ORM models inside migration files. At migration time, your model might be different from what the migration expects. Use raw SQL or `op.get_bind()`.

---

### Chapter 2.3 — Autogenerate vs Manual (Know the Difference)

Autogenerate (`--autogenerate`) **cannot** detect:
- Changes inside stored procedures
- Server defaults
- Custom types in some databases
- Index changes on expressions
- Data in the tables (obviously)

Always **read the generated file before running it**. It's not always right.

**✅ Practice Task:** Intentionally make a change Alembic can't autogenerate (e.g., add a `CHECK` constraint), write it manually, verify it applies correctly.

---

## PHASE 3 — Team Workflows

### Chapter 3.1 — The Version Chain

Every migration file has:
```python
revision = 'a1b2c3d4'       # this migration's ID
down_revision = 'z9y8x7w6'  # previous migration's ID (parent)
```

Alembic tracks a **linear chain**. Your DB stores the current revision in a table called `alembic_version`.

```bash
alembic current        # what revision is my DB at?
alembic history        # show the full chain
alembic history --verbose  # with details
alembic show <rev_id>  # show a specific migration
```

---

### Chapter 3.2 — Merge Conflicts (The Real Senior Skill)

**The scenario:** You and your teammate both branch from revision `abc123`.
- You create migration `def456` (add `posts` table)
- They create migration `ghi789` (add `settings` table)
- Both have `down_revision = 'abc123'`
- Now you merge — **Alembic has two heads**

```bash
alembic heads   # shows BOTH heads — this is the problem
```

**Fix it:**
```bash
alembic merge -m "merge_posts_and_settings" def456 ghi789
```

This creates a new migration:
```python
revision = 'jkl012'
down_revision = ('def456', 'ghi789')   # ← has TWO parents
```

```bash
alembic upgrade head  # now works
```

**✅ Practice Task:** Simulate this with two branches. Cause the conflict. Resolve with merge. This is something you WILL face in every team project.

---

### Chapter 3.3 — Stamping (Emergency Ops)

Sometimes your DB is in a state Alembic doesn't know about (e.g., you ran raw SQL in prod).

```bash
# Tell Alembic "the DB is at this revision" without running anything
alembic stamp <revision_id>

# Tell Alembic "DB is fully up to date"
alembic stamp head
```

Use `stamp` carefully — it lies to Alembic about the DB state. Only use when you know what you're doing.

---

## PHASE 4 — Production Grade

### Chapter 4.1 — Zero-Downtime Migrations

This is where junior vs senior thinking diverges. In production, you can't just `ALTER TABLE` — it can lock the table for minutes and take your app down.

**The 3-Phase Expand/Contract Pattern:**

```
Phase 1 — EXPAND   : Add new column (nullable). Deploy app that writes to BOTH.
Phase 2 — MIGRATE  : Backfill data. Verify.
Phase 3 — CONTRACT : Drop old column. Deploy app that only uses new column.
```

**Example — renaming `username` to `handle`:**

**Migration 1 (deploy with app v1.1):**
```python
def upgrade():
    op.add_column('users', sa.Column('handle', sa.String(), nullable=True))
    # App now writes to BOTH username and handle
```

**Migration 2 (backfill, run as a job):**
```python
def upgrade():
    op.execute("UPDATE users SET handle = username WHERE handle IS NULL")
    op.alter_column('users', 'handle', nullable=False)
```

**Migration 3 (deploy with app v1.2 that only uses handle):**
```python
def upgrade():
    op.drop_column('users', 'username')
```

---

### Chapter 4.2 — ENV-Based Config (Proper Production Setup)

Never hardcode DB URLs. Update `env.py`:

```python
# alembic/env.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_url():
    return os.getenv("DATABASE_URL")

# In both run_migrations_offline() and run_migrations_online():
url = get_url()
```

And in `alembic.ini`, comment out the URL:
```ini
# sqlalchemy.url =    ← leave blank, driven by env
```

---

### Chapter 4.3 — Running Migrations Programmatically (on App Startup)

```python
# app/main.py
from alembic.config import Config
from alembic import command

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

app = FastAPI()

@app.on_event("startup")
async def startup():
    run_migrations()  # auto-migrate on every deploy
```

This is the pattern used in Docker/Kubernetes deployments.

---

### Chapter 4.4 — CI/CD Integration

```yaml
# .github/workflows/deploy.yml (concept)
steps:
  - name: Run Migrations
    run: alembic upgrade head
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
  
  - name: Deploy App
    run: # your deploy command
```

**Rule:** Migrations run **before** the new app code deploys. Never after.

---

## PHASE 5 — Senior Patterns

### Chapter 5.1 — Testing Migrations

```python
# tests/test_migrations.py
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect

TEST_DB_URL = "postgresql://user:pass@localhost/test_migrations_db"

@pytest.fixture(scope="session")
def migrated_db():
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")  # clean up

def test_users_table_exists(migrated_db):
    engine = create_engine(TEST_DB_URL)
    inspector = inspect(engine)
    assert "users" in inspector.get_table_names()

def test_users_has_email_column(migrated_db):
    engine = create_engine(TEST_DB_URL)
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('users')]
    assert 'email' in columns

def test_full_upgrade_downgrade_cycle():
    """Every migration must be reversible."""
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")   # must not crash
    command.upgrade(cfg, "head")     # must not crash
```

---

### Chapter 5.2 — Multi-Tenant Migrations (Schema-per-Tenant)

For SaaS products where each client has their own Postgres schema:

```python
# alembic/env.py — multi-tenant pattern
from sqlalchemy import text

TENANT_SCHEMAS = ["tenant_a", "tenant_b", "tenant_c"]

def run_migrations_for_tenant(schema_name: str, connection):
    connection.execute(text(f"SET search_path TO {schema_name}"))
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=schema_name,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()

with engine.connect() as connection:
    for schema in TENANT_SCHEMAS:
        run_migrations_for_tenant(schema, connection)
```

---

### Chapter 5.3 — Audit Table Pattern via Migration

```python
def upgrade():
    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('table_name', sa.String(50), nullable=False),
        sa.Column('operation', sa.String(10), nullable=False),  # INSERT/UPDATE/DELETE
        sa.Column('row_id', sa.Integer(), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('changed_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('changed_at', sa.DateTime(), server_default=sa.func.now()),
    )
    
    # Postgres trigger via migration
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_trigger_func()
        RETURNS trigger AS $$
        BEGIN
            INSERT INTO audit_log (table_name, operation, row_id, old_values, new_values)
            VALUES (
                TG_TABLE_NAME,
                TG_OP,
                COALESCE(NEW.id, OLD.id),
                row_to_json(OLD),
                row_to_json(NEW)
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER users_audit
        AFTER INSERT OR UPDATE OR DELETE ON users
        FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
    """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS users_audit ON users")
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_func")
    op.drop_table('audit_log')
```

---

## 📋 Complete Practice Sequence

| # | Task | Phase | Concept |
|---|------|-------|---------|
| 1 | Setup project, init Alembic, connect to models | 1 | Setup |
| 2 | Create users table, upgrade/downgrade 5 times | 1 | Core loop |
| 3 | Build full blog schema in 6 separate migrations | 2 | Schema ops |
| 4 | Split `name` → `first_name`+`last_name` with data | 2 | Data migration |
| 5 | Simulate merge conflict with a partner (or two branches) | 3 | Branching |
| 6 | Break prod and use `alembic stamp` to recover | 3 | Stamping |
| 7 | Implement rename column with zero-downtime pattern | 4 | Prod patterns |
| 8 | Write migration tests with upgrade/downgrade cycle | 5 | Testing |
| 9 | Add audit log table with Postgres trigger | 5 | Senior pattern |
| 10 | Implement schema-per-tenant loop in `env.py` | 5 | Multi-tenancy |

---

## ⚡ Golden Rules (Internalize These)

```
1. Never edit a migration that has been run in production
2. Always write downgrade() — even if it's a no-op with a comment explaining why
3. Never import ORM models in migration files — use raw SQL or op.get_bind()
4. Migrations before deploy, never after
5. Test upgrade AND downgrade in CI
6. Nullable first, constraints later (for zero-downtime)
7. One logical change per migration — small, focused, named clearly
```

