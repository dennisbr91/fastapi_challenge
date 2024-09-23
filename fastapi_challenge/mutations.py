from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi_challenge.models import User, Task
from fastapi_challenge.schema import TaskCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_task(db: Session, task: TaskCreate):
    db_task = Task(name=task.name, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: str):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Task).offset(skip).limit(limit).all()


def delete_task(db: Session, task_id: str):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return task
    return None


def update_task(db: Session, task_id: str, task_update: TaskCreate):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.name = task_update.name
        task.description = task_update.description
        task.status = task_update.status
        db.commit()
        db.refresh(task)
        return task
    return None
