# 🐘 PostgreSQL DBA Master Roadmap 2026

> **Sequential · Comprehensive · Every Topic Covered · Based on [roadmap.sh/postgresql-dba](https://roadmap.sh/postgresql-dba)**
>
> *Follow the sequence — each phase builds directly on the previous one.*

<div align="center">

| 13 Phases | 50+ Topics | From Zero → Postgres Hacker |
|:---------:|:----------:|:---------------------------:|

</div>

---

## Table of Contents

- [Phase 01 — Basic RDBMS Terms & Concepts](#phase-01--learn-basic-rdbms-terms--concepts)
- [Phase 02 — Install & Run PostgreSQL](#phase-02--learn-how-to-install-and-run-postgresql)
- [Phase 03 — SQL Concepts](#phase-03--learn-sql-concepts)
- [Phase 04 — Configure PostgreSQL](#phase-04--learn-how-to-configure-postgres)
- [Phase 05 — PostgreSQL Security](#phase-05--learn-postgres-security-concepts)
- [Phase 06 — Infrastructure DBA Skills](#phase-06--develop-infrastructure-dba-skills)
- [Phase 07 — Automate Routines](#phase-07--learn-how-to-automate-routines)
- [Phase 08 — Application DBA Skills](#phase-08--develop-application-dba-skills)
- [Phase 09 — Advanced Topics](#phase-09--learn-postgres-advanced-topics)
- [Phase 10 — Troubleshooting Techniques](#phase-10--learn-postgres-troubleshooting-techniques)
- [Phase 11 — SQL Optimization](#phase-11--learn-sql-optimization-techniques)
- [Phase 12 — Architect Skills](#phase-12--develop-architect-skills)
- [Phase 13 — Postgres Hacker Skills](#phase-13--develop-postgres-hacker-skills)

---

## Phase 01 — Learn Basic RDBMS Terms & Concepts

> **Goal:** Get a solid understanding of Postgres key terms and core RDBMS concepts before touching anything practical.

### 🗂️ Object Model
- **Data types** — built-in types: integer, text, boolean, numeric, date, timestamp, JSON, UUID, etc.
- **Columns** — data type assignment, constraints, defaults
- **Rows** — tuples of data, how they are stored
- **Tables** — structure, heap storage
- **Schemas** — namespacing objects within a database
- **Databases** — isolation, connections, clusters
- **Queries** — how SQL is parsed and executed

### 🔗 Relational Model
- **Domains** — type definitions and constraints
- **Attributes** — named columns with a domain
- **Tuples** — single rows of a relation
- **Relations** — tables as sets of tuples
- **Constraints** — `NOT NULL`, `UNIQUE`, `CHECK`, `PRIMARY KEY`, `FOREIGN KEY`
- **NULL** — three-valued logic, how NULL propagates in comparisons and aggregations

### 🧠 Databases High-Level Concepts
- **ACID** — Atomicity, Consistency, Isolation, Durability
- **MVCC** — Multi-Version Concurrency Control, how Postgres avoids read locks
- **Transactions** — `BEGIN`, `COMMIT`, `ROLLBACK`, transaction isolation levels
- **Write-Ahead Log (WAL)** — durability guarantee, crash recovery, role in replication
- **Query processing** — parse → rewrite → plan → execute pipeline

---

## Phase 02 — Learn How to Install and Run PostgreSQL

> **Goal:** Get a fully working Postgres environment for all future learning.

### 📦 Installation Methods
- **Using package managers** — `apt install postgresql` (Debian/Ubuntu), `yum`/`dnf` (RHEL/CentOS)
- **Using Docker** — `docker run postgres`, official images, `docker-compose` setup
- **Cloud deployment** — AWS RDS, GCP Cloud SQL, Azure Database, Heroku, DigitalOcean Managed Postgres

### ⚙️ Service Management
- **systemd** — `systemctl start/stop/restart/reload/status postgresql`
- **pg_ctl** — `pg_ctl start`, `stop`, `restart`, `reload`, `status`, `initdb`
- **OS-specific tools** — `pg_ctlcluster` (Debian), `pg_lsclusters`

### 🔌 Connecting to Postgres
- **psql** — connect with `-U`, `-h`, `-p`, `-d` flags
- **psql meta-commands** — `\l`, `\c`, `\dt`, `\d tablename`, `\du`, `\timing`, `\i`, `\e`
- **Connection strings** — `postgresql://user:pass@host:port/dbname`
- **GUI clients** — pgAdmin, DBeaver, TablePlus for visual management

---

## Phase 03 — Learn SQL Concepts

> **Goal:** Gain practical skills to create, manipulate, and query database objects using `psql`.

### 🔢 Basic Data Types
- **Numeric** — `integer`, `bigint`, `smallint`, `numeric`, `real`, `double precision`, `serial`
- **Text** — `varchar(n)`, `char(n)`, `text`
- **Boolean** — `true`, `false`, `NULL`
- **Date & Time** — `date`, `time`, `timestamp`, `timestamptz`, `interval`
- **Special types** — `uuid`, `jsonb`, `json`, `array`, `hstore`, `inet`, `cidr`

### 📝 DML Queries (Data Manipulation)
- **SELECT** — `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`, column aliases
- **INSERT** — single row, multi-row, `INSERT ... SELECT`, `ON CONFLICT` (upsert)
- **UPDATE** — `SET`, `WHERE`, `UPDATE ... FROM`, `RETURNING`
- **DELETE** — `WHERE`, `DELETE ... USING`, `RETURNING`
- **Filtering** — `LIKE`, `ILIKE`, `IN`, `BETWEEN`, `IS NULL`, `IS NOT NULL`
- **Joining tables** — `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`, `CROSS JOIN`, self-joins
- **Advanced DML topics:**
  - **Transactions** — `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`
  - **CTE** — `WITH` clause, named subqueries, chained CTEs
  - **Subqueries** — correlated, uncorrelated, scalar subqueries
  - **LATERAL join** — referencing columns from preceding `FROM` items
  - **Grouping** — `GROUP BY`, `HAVING`, `ROLLUP`, `CUBE`, `GROUPING SETS`
  - **Set operations** — `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`

### 🏗️ DDL Queries (Data Definition)
- **Tables** — `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `TRUNCATE`
- **Schemas** — `CREATE SCHEMA`, `SET search_path`, `DROP SCHEMA`
- **Indexes** — `CREATE INDEX`, `CREATE UNIQUE INDEX`, `DROP INDEX`, `REINDEX`
- **Views** — `CREATE VIEW`, `CREATE OR REPLACE VIEW`, materialized views
- **Sequences** — `CREATE SEQUENCE`, `nextval()`, `currval()`, `setval()`
- **Constraints** — adding/dropping primary keys, foreign keys, unique, check constraints

### 📤 Import & Export
- **COPY** — `COPY table FROM 'file'`, `COPY table TO 'file'`, CSV format, delimiters
- **`\copy`** — client-side version of COPY via psql (no superuser needed)

---

## Phase 04 — Learn How to Configure Postgres

> **Goal:** Understand how `postgresql.conf` shapes Postgres behavior — memory, WAL, autovacuum, logging.

### 📄 postgresql.conf — Key Sections

#### Resource Usage
- `shared_buffers` — primary memory cache (start at 25% of RAM)
- `work_mem` — per sort/hash operation memory
- `maintenance_work_mem` — for VACUUM, CREATE INDEX, REINDEX
- `effective_cache_size` — planner hint about total available memory
- `max_connections` — total allowed client connections

#### Write-Ahead Log (WAL)
- `wal_level` — `minimal`, `replica`, `logical`
- `synchronous_commit` — durability vs. performance tradeoff
- `wal_buffers` — WAL write buffer size
- `min_wal_size` / `max_wal_size` — WAL file retention bounds
- `archive_mode` / `archive_command` — enable WAL archiving for PITR

#### Checkpoints & Background Writer
- `checkpoint_completion_target` — spread checkpoint I/O over time
- `checkpoint_timeout` — max time between automatic checkpoints
- `bgwriter_lru_maxpages` — background writer page write aggressiveness

#### Autovacuum
- `autovacuum` — enable/disable (never disable in production)
- `autovacuum_vacuum_threshold` / `autovacuum_vacuum_scale_factor`
- `autovacuum_analyze_threshold` / `autovacuum_analyze_scale_factor`
- `autovacuum_vacuum_cost_delay` — throttle autovacuum I/O impact

#### Replication Settings
- `max_wal_senders` — max concurrent replication connections
- `wal_keep_size` — WAL retained for standbys
- `hot_standby` — allow read queries on standby server

#### Query Planner
- `random_page_cost` — cost of non-sequential reads (lower for SSDs: `1.1`)
- `effective_io_concurrency` — parallel I/O concurrency hint
- `default_statistics_target` — statistics detail per column for planner

#### Logging & Statistics
- `log_min_duration_statement` — log slow queries above N ms
- `log_statement` — `none`, `ddl`, `mod`, `all`
- `log_line_prefix` — customize log line format (timestamp, PID, user, db)
- `track_activities` / `track_counts` — enable `pg_stat_*` views
- `pg_stat_statements` — extension for query-level performance aggregation

---

## Phase 05 — Learn Postgres Security Concepts

> **Goal:** Deploy and maintain secure Postgres configurations.

### 🔑 Authentication
- **pg_hba.conf** — host-based authentication file
  - Record format: `TYPE  DATABASE  USER  ADDRESS  METHOD`
  - Auth methods: `trust`, `peer`, `md5`, `scram-sha-256`, `ldap`, `cert`
  - Connection types: `local`, `host`, `hostssl`, `hostnossl`
- **Authentication models** — password auth, certificate auth, LDAP/Kerberos/RADIUS
- **SSL settings** — `ssl = on`, `ssl_cert_file`, `ssl_key_file`, `ssl_ca_file`, enforcing SSL

### 👥 Roles & Privileges
- **Roles** — `CREATE ROLE`, `CREATE USER`, `ALTER ROLE`, `DROP ROLE`
  - Role attributes: `LOGIN`, `SUPERUSER`, `CREATEDB`, `CREATEROLE`, `REPLICATION`, `BYPASSRLS`
  - Role inheritance: `GRANT role TO role`, `SET ROLE`, `RESET ROLE`
- **Object Privileges** — `GRANT privilege ON object TO role`
  - Privilege types: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, `EXECUTE`, `USAGE`
  - `REVOKE` — removing privileges
  - `ALTER DEFAULT PRIVILEGES` — apply grants to all future objects in a schema

### 🔒 Advanced Security Topics
- **Row-Level Security (RLS)** — `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`
  - `CREATE POLICY` with `USING` and `WITH CHECK` expressions
  - Policies per operation: `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- **Column-level privileges** — grant `SELECT` on specific columns only
- **SELinux integration** — `sepgsql` module, mandatory access control
- **pgaudit** extension — audit logging for all DDL and DML access

---

## Phase 06 — Develop Infrastructure DBA Skills

> **Goal:** Deploy, replicate, back up, monitor, and manage Postgres in production.

### 🔁 Replication
- **Streaming Replication** — WAL-based physical replication, primary/standby setup
  - `primary_conninfo`, `recovery.conf`, `standby.signal`
  - Synchronous vs. asynchronous replication
  - Monitoring replication lag via `pg_stat_replication`
- **Logical Replication** — row-level replication across major versions
  - `CREATE PUBLICATION`, `CREATE SUBSCRIPTION`
  - Partial replication (specific tables/rows/operations)
  - Replication slots — `pg_create_logical_replication_slot`

### 💾 Backup & Recovery Tools

#### Built-in Tools
- **pg_dump** — logical backup of one database, formats: plain, custom, directory, tar
- **pg_dumpall** — dump all databases + global objects (roles, tablespaces)
- **pg_restore** — restore from custom/directory/tar format dumps
- **pg_basebackup** — physical base backup for standbys and PITR

#### Third-Party Tools
- **barman** — backup and recovery manager, WAL archiving, PITR
- **pgbackrest** — parallel backup/restore, delta backups, S3/GCS/Azure support
- **pg_probackup** — full, incremental, PTRACK backups
- **WAL-G** — cloud-native WAL archiving to S3/GCS/Azure Blob

#### Backup Validation
- Regularly restore backups to a test environment
- Verify data integrity with spot-check queries
- Test PITR (Point-in-Time Recovery) runbooks quarterly

### ⬆️ Upgrading Procedures
- **Minor upgrades** — `apt upgrade postgresql-16`, in-place, no data change required
- **Major upgrades with pg_upgrade** — `pg_upgrade -b old_bin -B new_bin -d old_data -D new_data`
- **Zero-downtime upgrades** — logical replication between versions, then switchover

### 🔀 Connection Pooling
- **PgBouncer** — lightweight pooler, modes: `session`, `transaction`, `statement`
  - Config: `pgbouncer.ini`, `listen_port`, `max_client_conn`, `pool_mode`
- **Alternatives:**
  - **Pgpool-II** — pooling + load balancing + HA
  - **Odyssey** — multi-threaded pooler by Yandex
  - **Pgagroal** — ultra-fast OLTP-focused pooler

### 📊 Infrastructure Monitoring
- **Prometheus** — `postgres_exporter`, scrape `pg_stat_*` views, define alerting rules
- **Grafana** — dashboards for replication lag, query time, connection count, bloat
- **Zabbix** — enterprise monitoring with Postgres templates
- **pgBadger** — log parsing and HTML performance report generation

### 🏥 High Availability & Cluster Management
- **Patroni** — HA using DCS (etcd/Consul/ZooKeeper) for automatic leader election
- **Alternatives:**
  - **Repmgr** — replication manager with automatic failover
  - **Stolon** — cloud-native HA, Kubernetes-friendly
  - **pg_auto_failover** — simple two-node HA with a monitor
  - **PAF** — Pacemaker/Corosync-based HA

### ⚖️ Load Balancing & Service Discovery
- **HAProxy** — TCP load balancer, health-check-aware routing to primary vs. replicas
- **Keepalived** — virtual IP failover using VRRP
- **Consul** — service registry, health checks, DNS-based discovery
- **Etcd** — distributed key-value store used by Patroni for leader election

### ☸️ Postgres on Kubernetes
- **StatefulSet** — basic Postgres on K8s with persistent volumes and headless services
- **Helm charts** — Bitnami PostgreSQL chart, value overrides for prod config
- **Operators** — Zalando Postgres Operator, CloudNativePG, Crunchy Postgres Operator

### 📐 Resource & Capacity Planning
- Estimating storage growth from table/index bloat trends
- Connection count growth vs. pooler sizing decisions
- CPU/memory profiling under realistic production workloads

---

## Phase 07 — Learn How to Automate Routines

> **Goal:** Stop doing things manually. Automate every repeatable operational task.

### 🐚 Scripting Automation
- **Bash scripts** — cron jobs for backup, vacuum, log rotation, health checks
- **Python scripts** — `psycopg2`/`asyncpg` for complex automation, alerting, data pipelines
- **psql scripting** — `psql -c`, `psql -f script.sql`, `-v` variable substitution, `\gexec`

### ⚙️ Configuration Management
- **Ansible** — `community.postgresql` collection, playbooks for install/config/backup
- **Salt** — states for Postgres configuration, pillar for secrets
- **Chef** — `postgresql` cookbook, recipes for cluster setup
- **Puppet** — `puppetlabs-postgresql` module

---

## Phase 08 — Develop Application DBA Skills

> **Goal:** Understand how applications interact with Postgres: schema design, migrations, queues, partitioning.

### 🔄 Migrations
- **Practical patterns** — expand-and-contract, additive changes first, backfilling in batches
- **Anti-patterns** — `ALTER COLUMN TYPE` on large tables without rewrite strategy, adding `NOT NULL` without a default
- **Migration tools:**
  - **Liquibase** — XML/YAML/SQL changelogs, rollback support
  - **Sqitch** — plan-based migrations, pure SQL, VCS-friendly
  - **Alembic** (Python) — SQLAlchemy-based, autogenerate from models
  - **Flyway** — Java-centric, ordered SQL migration scripts

### 📤 Data Import / Export & Bulk Processing
- **Bulk loading** — `COPY FROM` for fastest inserts, disable triggers/indexes during load
- **Batch processing** — chunked `UPDATE`/`DELETE` to avoid long transactions and lock escalation
- **Foreign Data Wrappers (FDW)** — `postgres_fdw`, `file_fdw` — query external sources as tables
- **Logical replication** for streaming data between databases with zero downtime

### 📬 Queues in Postgres
- **Practical patterns** — `SELECT ... FOR UPDATE SKIP LOCKED` for job queues
- **Anti-patterns** — polling without `SKIP LOCKED`, holding locks during slow processing
- **Skytools PGQ** — robust queue with at-least-once delivery for high-throughput workloads
- **LISTEN / NOTIFY** — lightweight async pub/sub notification between sessions

### 🗂️ Data Partitioning & Sharding
- **Declarative partitioning** — `PARTITION BY RANGE`, `LIST`, `HASH`
  - `CREATE TABLE ... PARTITION OF` syntax
  - Partition pruning, constraint exclusion
  - Attaching/detaching partitions with zero downtime
- **Inheritance-based partitioning** — legacy approach, `ONLY` keyword
- **Sharding patterns** — application-level sharding, Citus extension, FDW-based sharding

### 📐 Database Normalization
- **1NF** — atomic values, no repeating groups
- **2NF** — no partial dependencies on a composite key
- **3NF** — no transitive dependencies
- **BCNF** — Boyce-Codd Normal Form, stricter than 3NF
- **Denormalization** — when and why to intentionally break normal forms for performance

---

## Phase 09 — Learn Postgres Advanced Topics

> **Goal:** Understand Postgres from the inside out — internals, fine-grained tuning, and advanced SQL.

### ⚙️ Low-Level Internals

#### Processes & Memory Architecture
- **Postmaster** — listener process, spawns one backend process per connection
- **Backend processes** — one per client, accesses shared memory
- **Background workers** — autovacuum, WAL writer, checkpointer, bgwriter, stats collector
- **Shared memory** — `shared_buffers`, WAL buffers, lock tables, process arrays

#### Vacuum Processing
- **VACUUM** — dead tuple removal, updates FSM (Free Space Map) and VM (Visibility Map)
- **VACUUM FULL** — full table rewrite, exclusive lock, reclaims space to OS
- **ANALYZE** — updates query planner statistics in `pg_statistic`
- **Autovacuum** — automated VACUUM/ANALYZE tuning per table and globally
- **Table bloat** — causes (dead tuples), detection with `pgstattuple`, remediation

#### Buffer Management
- **Shared buffer pool** — LRU-based 8KB page caching, `pg_buffercache` extension
- **OS page cache** — `effective_cache_size` as a planner hint for index decisions
- **Double-write protection** — WAL protects against partial page writes on crash

#### Lock Management
- **Table-level lock types** — `ACCESS SHARE`, `ROW EXCLUSIVE`, `SHARE UPDATE EXCLUSIVE`, `ACCESS EXCLUSIVE`
- **Row-level locks** — `SELECT FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`
- **Advisory locks** — `pg_advisory_lock()`, `pg_try_advisory_lock()` for app-level locking
- **Deadlocks** — detection cycle, `deadlock_timeout`, reading `pg_stat_activity`
- **Monitoring locks** — `pg_locks`, `pg_blocking_pids()`, lock waits in `pg_stat_activity`

#### Physical Storage & File Layout
- **Data directory** — `$PGDATA`, `base/`, `global/`, `pg_wal/`, `pg_tblspc/`
- **Relation files** — heap files, forks: main, FSM, VM, init
- **Pages** — 8KB page structure, page header, line pointers, tuples, item IDs
- **TOAST** — The Oversized Attribute Storage Technique for large column values
- **Tablespaces** — `CREATE TABLESPACE`, placing tables/indexes on different disks

#### System Catalog
- **Key catalog tables** — `pg_class`, `pg_attribute`, `pg_index`, `pg_constraint`, `pg_proc`, `pg_type`
- **System views** — `information_schema`, `pg_stat_user_tables`, `pg_stat_user_indexes`, `pg_stat_replication`

### 🎛️ Fine-Grained Tuning
- **Per-user settings** — `ALTER ROLE user SET parameter = value`
- **Per-database settings** — `ALTER DATABASE db SET parameter = value`
- **Storage parameters** — `FILLFACTOR`, per-table autovacuum thresholds
- **Workload-dependent tuning:**
  - **OLTP** — low latency, high concurrency, small short transactions
  - **OLAP** — high `work_mem`, parallel query, large sequential scans
  - **HTAP** — mixed workload, partitioning, separate read replicas, caching

### 🧩 Advanced SQL Topics
- **PL/pgSQL** — `CREATE FUNCTION`, `CREATE PROCEDURE`, control flow, cursors, exception blocks
- **Triggers** — `CREATE TRIGGER`, `BEFORE`/`AFTER`, row-level vs statement-level, `NEW`/`OLD`
- **Aggregate functions** — built-in aggregates, `CREATE AGGREGATE`, ordered-set and hypothetical aggregates
- **Window functions** — `OVER()`, `PARTITION BY`, `ORDER BY`, frame specs (`ROWS`, `RANGE`, `GROUPS`)
  - `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `NTILE()`, `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`
- **Recursive CTE** — `WITH RECURSIVE`, tree/graph traversal, hierarchical data queries

---

## Phase 10 — Learn Postgres Troubleshooting Techniques

> **Goal:** Detect, diagnose, and resolve Postgres performance and operational problems systematically.

### 🖥️ Operating System Tools
- **top / htop / atop** — CPU, memory, load average, per-process breakdown
- **sysstat** (`iostat`, `sar`, `mpstat`) — disk I/O throughput, CPU utilization history
- **iotop** — per-process disk I/O, identifying I/O-heavy Postgres backends
- **vmstat** — virtual memory, swap usage, context switches
- **netstat / ss** — active TCP connections, port states, connection counts
- **free / /proc/meminfo** — memory breakdown, swap monitoring

### 🗃️ Postgres System Views
- **pg_stat_activity** — current queries, states (`active`, `idle`, `idle in transaction`), wait events
- **pg_stat_statements** — aggregated query stats: calls, `total_exec_time`, `mean_exec_time`, rows
- **pg_stat_user_tables** — seq scans, index scans, `n_dead_tup`, `n_live_tup`, last vacuum/analyze
- **pg_stat_user_indexes** — index scan count, tuples read vs. fetched
- **pg_stat_bgwriter** — checkpoint stats, buffers written, max_written_clean hits
- **pg_stat_replication** — standby state, sent/write/flush/replay LSN, replication lag
- **pg_locks** — current lock holders and waiters, lock types

### 🛠️ Postgres Tools
- **pgcenter** — interactive `top`-like tool for all Postgres system views
- **pg_activity** — htop-style interface for monitoring active queries in real time
- **pgBadger** — log file parsing, generates HTML performance reports

### 🔍 Query Analyzing
- **EXPLAIN** — show execution plan with planner cost estimates
- **EXPLAIN ANALYZE** — execute query + show actual runtime stats, row counts, timing
- **EXPLAIN (ANALYZE, BUFFERS)** — add buffer cache hit/miss information
- **Online visualization tools:**
  - [explain.depesz.com](https://explain.depesz.com/) — color-coded plan viewer
  - [explain.tensor.ru](https://explain.tensor.ru/) — detailed plan analysis
  - [PEV2 — pev2.dalibo.com](https://pev2.dalibo.com/) — interactive plan explorer
- **Reading plans** — seq scan vs. index scan, hash join vs. nested loop, sort vs. index scan, cost vs. actual rows

### 📝 Log Analyzing
- **pgBadger** — parse `postgresql.log`, generate HTML reports on slow queries, lock waits, connections
- **Ad-hoc log analysis** — `grep`, `awk`, `sed`, `cut`, `sort`, `uniq -c` on log files
- **Useful log settings** — `log_min_duration_statement`, `log_lock_waits`, `log_checkpoints`, `log_autovacuum_min_duration`

### 🔬 External Tracing & Profiling Tools
- **gdb** — attach to a Postgres backend process, get stack traces for hangs or crashes
- **strace** — trace system calls of a Postgres process (`strace -p PID`)
- **perf** — Linux CPU profiling, flame graphs for hot functions
- **eBPF / bpftrace** — low-overhead kernel-level tracing without restarts
- **Core dumps** — `ulimit -c unlimited`, analyze Postgres crashes post-mortem

### 📐 Troubleshooting Methods
- **USE Method** — Utilization, Saturation, Errors — for every resource (CPU, memory, disk, network)
- **RED Method** — Rate, Errors, Duration — for every service/query
- **Golden Signals** — Latency, Traffic, Errors, Saturation (Google SRE)

---

## Phase 11 — Learn SQL Optimization Techniques

> **Goal:** Write fast queries and design schemas that stay fast as data scales.

### 📇 Indexes & Their Use Cases
- **B-tree** — default type, equality and range queries, `ORDER BY`, most general use cases
- **Hash** — equality only (`=`), faster than B-tree for pure equality on large keys
- **GiST** — geometric types, full-text search, ranges, nearest-neighbor (`<->`)
- **SP-GiST** — non-balanced structures: quadtrees, kd-trees, radix trees
- **GIN** — `jsonb`, `tsvector` (full-text), arrays — multi-value / inverted index
- **BRIN** — tiny footprint for naturally ordered large tables (timestamps, sequential IDs)
- **Partial indexes** — `CREATE INDEX ... WHERE condition` — index only relevant subset of rows
- **Covering indexes** — `INCLUDE (col)` — satisfy queries from index alone (index-only scans)
- **Composite indexes** — column order matters; leading column must appear in `WHERE` or `ORDER BY`
- **Functional indexes** — `CREATE INDEX ON t (LOWER(email))` — index on expression result

### ⚠️ SQL Query Patterns & Anti-Patterns

#### Good Patterns
- Index columns used in `JOIN`, `WHERE`, and `ORDER BY`
- `SELECT` only needed columns — avoid `SELECT *` in production code
- Run `EXPLAIN ANALYZE` before any query goes to production
- Use `EXISTS` instead of `COUNT(*)` when only checking for existence
- Use keyset / cursor pagination instead of `OFFSET` for deep pages

#### Anti-Patterns
- **Functions on indexed columns** — `WHERE LOWER(email) = ...` disables index (use functional index)
- **Leading wildcard LIKE** — `WHERE name LIKE '%value%'` cannot use B-tree; use `pg_trgm` + GIN
- **Implicit type casting** — `WHERE int_col = '123'` can cause index miss
- **`NOT IN` with NULLs** — always returns empty set; use `NOT EXISTS` instead
- **Deep `OFFSET` pagination** — O(n) scan; switch to keyset (`WHERE id > last_seen_id`)
- **Long-running transactions** — hold row locks, cause table bloat, increase replication lag

### 🏗️ Schema Design Patterns & Anti-Patterns

#### Good Patterns
- Use `bigint`/`bigserial` or `uuid` (with `gen_random_uuid()`) for primary keys
- Normalize to 3NF by default; denormalize only where measured to be necessary
- Partition large tables by range (date) or hash early — harder to add later
- Use `timestamptz` (not `timestamp`) — avoids silent timezone bugs
- Add `created_at` and `updated_at` columns by default to every table

#### Anti-Patterns
- **EAV (Entity-Attribute-Value)** model — terrible query performance and type safety
- **Polymorphic associations** without proper constraints or union tables
- **Comma-separated values** in a single column — use arrays or a junction table
- **`text` for everything** — use proper types; type checking is free
- **`SERIAL`** instead of `GENERATED ALWAYS AS IDENTITY` (use identity columns in modern Postgres)

---

## Phase 12 — Develop Architect Skills

> **Goal:** Understand the broader database landscape and where Postgres fits — and where it does not.

### 🏛️ RDBMS in General
- **Benefits** — ACID guarantees, rich SQL, foreign keys, mature tooling, extensions
- **Limitations** — vertical scaling limits, schema rigidity, write amplification at massive scale

### 🔀 Postgres vs Other Databases

| Database | Type | Key Difference vs Postgres |
|----------|------|---------------------------|
| MySQL / MariaDB | RDBMS | Less feature-rich SQL, different MVCC model |
| Oracle | RDBMS | Enterprise features, licensing cost, RAC clustering |
| MS SQL Server | RDBMS | Windows-first, T-SQL dialect, strong BI integration |
| SQLite | Embedded RDBMS | Single-file, serverless, limited concurrency |
| MongoDB | Document NoSQL | Schema-less, no JOINs, horizontal scale-out |
| Cassandra | Column NoSQL | Tunable consistency, wide-column model, no joins |
| Redis | Key-Value | In-memory, data structure server, ephemeral by default |
| Elasticsearch | Search Engine | Inverted index, full-text search, not a primary store |
| ClickHouse | Column OLAP | Analytical workloads, extreme compression, no transactions |

### 🌿 Postgres Forks & Extensions

- **Citus** — distributed Postgres, sharding across nodes, now part of Azure
- **TimescaleDB** — time-series data, continuous aggregates, compression, hypertables
- **Greenplum** — massively parallel processing (MPP) Postgres fork for OLAP
- **Postgres-XL** — multi-master Postgres for both OLTP and OLAP
- **PostGIS** — geospatial extension, geometry types, spatial indexes, GIS functions
- **pgvector** — vector similarity search for AI/ML embeddings
- **pg_partman** — automated partition management
- **pg_cron** — cron-style job scheduling inside Postgres
- **pg_trgm** — trigram-based fuzzy text search with GIN indexes

---

## Phase 13 — Develop Postgres Hacker Skills

> **Goal:** Give back to the community. Contribute to the Postgres project itself.

### 📬 Daily Mailing List Participation
- **pgsql-general** — general usage questions and community discussions
- **pgsql-admin** — DBA topics, operational questions
- **pgsql-performance** — query performance and tuning discussions
- **pgsql-hackers** — core development, new features, design proposals
- **pgsql-bugs** — bug reports and regression analysis
- Subscribe at [postgresql.org/list](https://www.postgresql.org/list/)

### 🔎 Reviewing Patches
- Check [commitfest.postgresql.org](https://commitfest.postgresql.org/) for patches needing review
- Test patch correctness, coverage, documentation quality, and coding style
- Submit feedback to the `pgsql-hackers` mailing list

### 🛠️ Writing Patches & Contributing
- Read the `HACKERS` and `DEVELOPERS` files in the Postgres source tree
- Set up a dev build: `./configure && make && make install`
- Follow Postgres C coding style (tabs for indentation)
- Submit patches via `git format-patch` to `pgsql-hackers`
- Participate in Commitfests — each major version has ~5 open Commitfests

---

## How to Use This Roadmap

1. **Follow the sequence** — never skip Phase 01 or 03. SQL and RDBMS fundamentals underpin everything.
2. **Practice on real data** — load `pgbench`, a TPC-H dataset, or your own data and experiment actively.
3. **Break things deliberately** — simulate failures, test restores, trigger autovacuum, watch `EXPLAIN` change.
4. **Read the official docs** — [postgresql.org/docs](https://www.postgresql.org/docs/current/) is the best database documentation in existence.
5. **Run `EXPLAIN ANALYZE` on everything** — make it a non-negotiable habit before any query reaches production.

### Milestone Projects

| After Phase | Practice This |
|:-----------:|:--------------|
| 03 | Build a normalized schema, write all CRUD queries and CTEs |
| 04 | Tune a default Postgres install — memory, logging, autovacuum |
| 05 | Set up roles, row-level security policies, and SSL connections |
| 06 | Streaming replication + PgBouncer + pgbackrest automated backups |
| 07 | Automate backup validation in Python with Ansible playbook |
| 08 | Migrate a schema with zero downtime using expand-contract pattern |
| 09 | Analyze a slow query with `EXPLAIN ANALYZE`, identify root cause, fix |
| 10 | Simulate a deadlock, detect it in `pg_locks`, resolve it |
| 11 | Benchmark query with/without each index type — measure the difference |
| 12 | Design a partitioned + sharded schema with Citus for high-write load |

---

## Essential Resources

| Resource | What It Covers |
|----------|---------------|
| [postgresql.org/docs](https://www.postgresql.org/docs/current/) | Official docs — the gold standard reference |
| [The Internals of PostgreSQL](http://www.interdb.jp/pg/) | Deep-dive: buffer manager, WAL, MVCC, vacuum |
| [Use the Index, Luke](https://use-the-index-luke.com/) | Index optimization with Postgres examples |
| [Postgresqlco.nf](https://postgresqlco.nf/) | Every `postgresql.conf` parameter explained |
| [explain.depesz.com](https://explain.depesz.com/) | Online EXPLAIN ANALYZE visualization |
| [pgBadger](https://pgbadger.darold.net/) | Log analysis and slow query HTML reports |
| The Art of PostgreSQL — Dimitri Fontaine | Advanced SQL from an application perspective |
| SQL Antipatterns — Bill Karwin | Common schema and query mistakes to avoid |

---

## Happy Learning! 🐘

Follow the sequence, practice on real data, break things and fix them — that's how you become a Postgres expert.

> *"The more you understand your database, the more it rewards you."*

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue?style=flat-square&logo=postgresql)](https://postgresql.org)
[![roadmap.sh](https://img.shields.io/badge/Based%20on-roadmap.sh%2Fpostgresql--dba-blue?style=flat-square)](https://roadmap.sh/postgresql-dba)
