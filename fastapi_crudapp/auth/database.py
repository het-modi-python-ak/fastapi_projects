import sqlite3
from fastapi import HTTPException
from typing import Optional

DB_PATH = "users1.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users1 (
            username TEXT PRIMARY KEY,
            hashed_password TEXT NOT NULL,
            
        ); 
    """) 
    conn.commit()
    conn.close()


def get_user(username: str) -> Optional[dict]:  #geting user name and passwrd
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT username, hashed_password FROM users1 WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    if row:
        return {"username": row["username"], "hashed_password": row["hashed_password"]}
    return None

def create_user(username: str, hashed_password: str ):  #creating user 
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO users1 (username, hashed_password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username already taken")
    finally:
        conn.close()