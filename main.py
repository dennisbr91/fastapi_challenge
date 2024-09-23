from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import requests

import fastapi_challenge.schema
from fastapi_challenge.authentication import authenticate_user, create_access_token, get_current_user
from fastapi_challenge.db_config import get_db, database
from fastapi_challenge.models import User, Log, Task
from fastapi_challenge.schema import UserCreate, UserResponse, TaskCreate
from fastapi_challenge.settings import ACCESS_TOKEN_EXPIRE_MINUTES, WEATHER_API_KEY
from fastapi_challenge.mutations import create_user, get_task, get_tasks

app = FastAPI()


@app.middleware("http")
async def add_ip_country_weather(request: Request, call_next):
    if not database.is_connected:
        await database.connect()
    client_ip = request.client.host
    ip_response = requests.get(f"https://ipapi.co/{client_ip}/json/")
    country = ip_response.json().get("country_name", "Unknown")
    city = ip_response.json().get("city", "Unknown")
    weather_response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}")
    weather = weather_response.json().get("current", {})
    print("client_ip: ", client_ip)
    print("country: ", country)
    print("weather: ", weather)
    async with database.transaction():
        query = Log.__table__.insert().values(ip=client_ip, country=country, weather=weather)
        await database.execute(query)

    request.state.client_ip = client_ip
    request.state.country = country
    request.state.weather = weather
    response = await call_next(request)
    return response


@app.post("/users/add", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user.username, user.password)
    return db_user


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/tasks", response_model=List[fastapi_challenge.schema.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.get("/tasks/{task_id}", response_model=fastapi_challenge.schema.Task)
def read_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", response_model=fastapi_challenge.schema.Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_task(db=db, task=task)


@app.delete("/tasks/{taskId}", response_model=fastapi_challenge.schema.Task)
def delete_task(taskId: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = delete_task(db, taskId)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{taskId}", response_model=fastapi_challenge.schema.Task)
def update_task(taskId: str, task_update: TaskCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    task = update_task(db, taskId, task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# @app.get("/")
# async def read_root(request: Request):
#     return {
#         "ip": request.state.client_ip,
#         "country": request.state.country,
#         "weather": request.state.weather
#     }


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
