from pydantic import BaseModel
import uuid


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    name: str
    description: str


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: uuid.UUID
    status: str

    class Config:
        from_attributes = True
