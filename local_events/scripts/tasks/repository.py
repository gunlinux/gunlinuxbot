from sqlmodel import SQLModel, Session, create_engine, select

from sqlalchemy import not_
from sqlalchemy.sql.expression import column
from .models import Task


# 📁 Step 2: Set up the SQLite database and create tables
engine = create_engine('sqlite:///./test.db')  # ,isolation_level="")
SQLModel.metadata.create_all(engine)  # Creates the 'task' table


# 🧰 Step 3: Define the TaskRepository class (Repository Pattern)
class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task):
        """Add a new task to the database."""
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_all(self):
        """Retrieve all tasks from the database."""
        return self.session.query(Task).all()

    def get_active_by_name(self, title):
        """Retrieve all tasks from the database."""
        statement = select(Task).where(not_(column('completed')), Task.title == title)
        return self.session.exec(statement).first()

    def get_all_active_by_name(self, title: str):
        """Retrieve all tasks from the database."""
        statement = select(Task).where(not_(column('completed')), Task.title == title)
        return self.session.exec(statement).all()

    def get_by_id(self, task_id: int):
        """Retrieve a task by its ID."""
        return self.session.get(Task, task_id)

    def update(self, task: Task):
        """Update an existing task."""
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task_id: int):
        """Delete a task by its ID."""
        task = self.session.get(Task, task_id)
        if task:
            self.session.delete(task)
            self.session.commit()
        return task
