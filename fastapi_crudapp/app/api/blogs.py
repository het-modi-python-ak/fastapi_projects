from fastapi import FastAPI, HTTPException, status, Request,Query,APIRouter
from database.queries import select_query,post_query,select_by_id,update_query,delete_query
from app.schemas import  Blogdb
from database.db import cursor,mydb
import logging
import time
import mysql.connector
from middleware.logging import LoggingMiddleware


# middleware




router = APIRouter(tags=["blogs"])










# router.add_middleware(LoggingMiddleware)




#get


@router.get("/blogs", status_code=status.HTTP_200_OK)
def select_blogs(
    limit: int = Query(default=10, ge=1), 
    offset: int = Query(default=0, ge=0)
):
    try:
        
        
        query = "SELECT * FROM Blogs ORDER BY blog_id ASC LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        
        results = cursor.fetchall()
        
        return {
            "data": results,
            "metadata": {
                "limit": limit,
                "offset": offset,
                "count": len(results)
            }
        }
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {err}"
        )
   





# @router.get("/blogs", status_code=status.HTTP_200_OK)
# def select_users():
    
#     try:
      
#         cursor.execute(select_query)
#         results = cursor.fetchall()
#         return results
#     except mysql.connector.Error as err:
#         raise HTTPException(status_code=500, detail=f"Database connection error: {err}")



@router.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(blog_id: int):
    
    cursor.execute(select_by_id, (blog_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="blog not found")
    



#search by author
@router.get("/get_by_author", status_code=status.HTTP_200_OK) # 1. Changed to 200 OK (201 is for creating)
def get_by_auth(author: str = None):
    try:
     
        search_term = f"%{author}"
        
        # 3. Ensure the SQL string and parameters are correctly formatted
        
        cursor.execute("SELECT * FROM Blogs WHERE author LIKE %s", (search_term,))
        
        result = cursor.fetchall()
        
        if result:
            return result
        else:
            # 4. Strings must be in quotes
            raise HTTPException(status_code=404, detail="No author found")
            
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection error: {err}")




#post

@router.post("/blogs", status_code=status.HTTP_201_CREATED)
def insert_user(blog: Blogdb):
   
    values = (blog.blog_id, blog.title, blog.author, blog.Content)
    
    try:
        cursor.execute(post_query, values)
        mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        if err.errno == 1062:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Blog with ID {blog.blog_id} already exists."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {err}"
        )
        
    return {"message": f"blog with id {blog.blog_id} inserted successfully"}











@router.put("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def update_user(blog_id: int, blog: Blogdb):
    

    update_query
    values = (blog.title,blog.author, blog.Content, blog_id )

    cursor.execute(update_query, values)
    mydb.commit()
    if cursor.rowcount == 0:
        mydb.rollback()
        raise HTTPException(status_code=404, detail="blog not found")
    return {"message": f"blog with id {blog.blog_id} updated successfully"}









#delet

@router.delete("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def delete_blog(blog_id: int):
    delete_qu = delete_query
    cursor.execute(delete_query, (blog_id,))
    mydb.commit()
    if cursor.rowcount == 0:
        mydb.rollback()
        raise HTTPException(status_code=404, detail="blog not found")
    return {"message": f"blog with id {blog_id} deleted successfully"}


@router.delete("/blogs",status_code=status.HTTP_200_OK)
def delete_all():
    delete_all_blog = "truncate table Blogs"
    cursor.execute(delete_all_blog)
    mydb.commit()
    if cursor.rowcount>0:
        raise HTTPException(status_code=404 , detail="some issue while deleting ")
    return {"message":f"all blogs deleted"}