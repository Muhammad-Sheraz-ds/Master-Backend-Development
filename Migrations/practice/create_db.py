import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("❌ DATABASE_URL is not set in .env")
    exit(1)

# Extract host, user, password to connect to the default 'postgres' database first
# so we can execute the 'CREATE DATABASE' command.
try:
    base_url, db_name = db_url.rsplit("/", 1)
    admin_url = f"{base_url}/postgres"
except Exception:
    print("❌ DATABASE_URL format is invalid. Ensure it is formatted like: postgresql://postgres:password@localhost:5432/migrations_practice")
    exit(1)

print(f"Connecting to PostgreSQL server at: {admin_url.split('@')[-1]}...")
try:
    # PostgreSQL DDL (like CREATE DATABASE) cannot be executed inside a transaction block,
    # so we must connect with autocommit = True.
    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database already exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (db_name,))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Creating database '{db_name}'...")
        cursor.execute(f'CREATE DATABASE "{db_name}";')
        print(f"🎉 Database '{db_name}' created successfully!")
    else:
        print(f"ℹ️ Database '{db_name}' already exists.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Failed to create database: {e}")
    print("\n👉 Don't worry, you can also create the database manually using pgAdmin, DBeaver, or another SQL client.")
