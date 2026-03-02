from fastapi import FastAPI, HTTPException, status

from app.schemas import  Blogdb
from database.db import cursor,mydb

import mysql.connector

app = FastAPI()


@app.get("/blogs", status_code=status.HTTP_200_OK)
def select_users():
    select_query = "SELECT blog_id, title, author, content FROM Blogs"
    try:
      
        cursor.execute(select_query)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.post("/blogs", status_code=status.HTTP_201_CREATED)
def insert_user(blog: Blogdb):
    insert_query = """
    INSERT INTO Blogs (blog_id, title, author, content)
    VALUES (%s, %s, %s, %s)
    """
    values = (blog.blog_id, blog.title, blog.author, blog.Content)
    
    try:
        cursor.execute(insert_query, values)
        mydb.commit()
    except mysql.connector.Error as err:
       
        raise HTTPException(status_code=400, detail=f"Database error: {err}")
        
    return {"message": "User inserted successfully"}







@app.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(blog_id: int):
    select_query = "SELECT * FROM Blogs WHERE blog_id = %s"
    cursor.execute(select_query, (blog_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="User not found")
    



# 


@app.put("/blogs/{user_id}", status_code=status.HTTP_200_OK)
def update_user(blog_id: int, blog: Blogdb):
    # Hash the password using SHA-256
    

    update_query = """
    UPDATE Blogs
    SET title = %s, author = %s, content = %s
    WHERE blog_id = %s
    """
    values = (blog.title,blog.author, blog.Content, blog_id )

    cursor.execute(update_query, values)
    mydb.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}



@app.delete("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def delete_user(blog_id: int):
    delete_query = "DELETE FROM Blogs WHERE blog_id = %s"
    cursor.execute(delete_query, (blog_id,))
    mydb.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted successfully"}
