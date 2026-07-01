from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Real-Time Task Board"
    database_url: str = "sqlite:///./task_board.db"
    cors_origins: list[str] = ["*"]


settings = Settings()
