from fastapi import FastAPI

app = FastAPI(title="Database Migrations Practice")

@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI is running!"}
