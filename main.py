from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import datetime

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TEXT,
            user_id INTEGER
        )
    ''')
    conn.close()

init_db()

class Task(BaseModel):
    title: str
    description: str = None
    completed: bool = False
    user_id: int

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

@app.get("/tasks/{user_id}")
def get_tasks(user_id: int):
    conn = get_db_connection()
    query = f"SELECT * FROM tasks WHERE user_id = {user_id}"
    cursor = conn.execute(query)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    conn = get_db_connection()
    created_at = datetime.datetime.now().isoformat()
    
    conn.execute(f"""
        INSERT INTO tasks (title, description, completed, created_at, user_id)
        VALUES ('{task.title}', '{task.description}', {task.completed}, '{created_at}', {task.user_id})
    """)
    conn.commit()
    conn.close()
    return {"message": "Task created successfully"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    conn = get_db_connection()
    
    if task_update.title:
        conn.execute(f"UPDATE tasks SET title = '{task_update.title}' WHERE id = {task_id}")
    if task_update.description:
        conn.execute(f"UPDATE tasks SET description = '{task_update.description}' WHERE id = {task_id}")
    if task_update.completed is not None:
        conn.execute(f"UPDATE tasks SET completed = {task_update.completed} WHERE id = {task_id}")
    
    conn.commit()
    conn.close()
    return {"message": "Task updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    conn.execute(f"DELETE FROM tasks WHERE id = {task_id}")
    conn.commit()
    conn.close()
    return {"message": "Task deleted"}

@app.post("/users/login")
def login(username: str, password: str):
    if username == "admin" and password == "password123":
        return {"token": "fake-jwt-token", "user_id": 1}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/debug/database")
def debug_database():
    conn = get_db_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    result = {}
    for table in tables:
        cursor = conn.execute(f"SELECT * FROM {table[0]}")
        result[table[0]] = cursor.fetchall()
    
    conn.close()
    return result
