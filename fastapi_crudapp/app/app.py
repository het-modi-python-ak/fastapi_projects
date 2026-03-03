from fastapi import FastAPI, HTTPException, status
from database.queries import select_query,post_query,select_by_id,update_query,delete_query
from app.schemas import  Blogdb
from database.db import cursor,mydb

import mysql.connector

app = FastAPI()


@app.get("/blogs", status_code=status.HTTP_200_OK)
def select_users():
    select_quer = select_query
    try:
      
        cursor.execute(select_quer)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

from fastapi import HTTPException, status
import mysql.connector




@app.post("/blogs", status_code=status.HTTP_201_CREATED)
def insert_user(blog: Blogdb):
    insert_qu = post_query
    values = (blog.blog_id, blog.title, blog.author, blog.Content)
    
    try:
        cursor.execute(insert_qu, values)
        mydb.commit()
    except mysql.connector.Error as err:
        
        if err.errno == 1062:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Blog with ID {blog.blog_id} already exists."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {err}"
        )
        
    return {"message": f"blog with id {blog.blog_id} inserted successfully"}







@app.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(blog_id: int):
    select_blog_id = select_by_id
    cursor.execute(select_blog_id, (blog_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="blog not found")
    






@app.put("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def update_user(blog_id: int, blog: Blogdb):
    

    update_qu =update_query
    values = (blog.title,blog.author, blog.Content, blog_id )

    cursor.execute(update_qu, values)
    mydb.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="blog not found")
    return {"message": f"blog with id {blog.blog_id} updated successfully"}



@app.delete("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def delete_user(blog_id: int):
    delete_qu = delete_query
    cursor.execute(delete_qu, (blog_id,))
    mydb.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="blog not found")
    return {"message": f"blog with id {blog_id} deleted successfully"}
