from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


# 🔑 Step 1: Define the SQLModel for the Task entity
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    duration: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed: bool = False
