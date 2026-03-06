from fastapi import FastAPI, HTTPException, status, Request
from database.queries import select_query,post_query,select_by_id,update_query,delete_query
from app.schemas import  Blogdb
from database.db import cursor,mydb
from  mysql.connector import errorcode
import logging
import time
import mysql.connector

# middleware

logging.basicConfig(
    filename="blog1.log",
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    filemode='a',
    force=True
)
logger = logging.getLogger(__name__)
app = FastAPI(title="Example API")

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    response_time = time.perf_counter() - start_time
    logger.info(f"{request.method} {request.url.path} {response.status_code} {response_time:.3f}s")
    return response












def db_operation(query, params=None, fetch_results=False):
    """
    Executes a database query and handles common MySQL errors.
    """
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_results:
            return cursor.fetchall()
        
        mydb.commit() # Commit changes for POST/PUT/DELETE
        return {"message": "Operation successful"}

    except mysql.connector.Error as err:
        # Handle specific MySQL errors
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database access denied: Check credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database does not exist.")
        elif err.errno == errorcode.ER_NO_SUCH_TABLE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found.")
        elif err.errno == errorcode.ER_DUP_ENTRY:
             # Handle duplicate entry 
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate entry detected.")
        else:
            # General database error
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {err}")
    
    except Exception as e:
        # Catch any other unexpected exceptions
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")






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
   
    values = (blog.blog_id, blog.title, blog.author, blog.Content)
    
    try:
        cursor.execute(post_query, values)
        mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
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
    
    cursor.execute(select_by_id, (blog_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="blog not found")
    





@app.put("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def update_user(blog_id: int, blog: Blogdb):
    

    update_query
    values = (blog.title,blog.author, blog.Content, blog_id )

    cursor.execute(update_query, values)
    mydb.commit()
    if cursor.rowcount == 0:
        mydb.rollback()
        raise HTTPException(status_code=404, detail="blog not found")
    return {"message": f"blog with id {blog.blog_id} updated successfully"}



@app.delete("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
def delete_blog(blog_id: int):
    delete_qu = delete_query
    cursor.execute(delete_query, (blog_id,))
    mydb.commit()
    if cursor.rowcount == 0:
        mydb.rollback()
        raise HTTPException(status_code=404, detail="blog not found")
    return {"message": f"blog with id {blog_id} deleted successfully"}


@app.delete("/blogs",status_code=status.HTTP_200_OK)
def delete_all():
    delete_all_blog = "truncate table Blogs"
    cursor.execute(delete_all_blog)
    mydb.commit()
    if cursor.rowcount>0:
        raise HTTPException(status_code=404 , detail="some issue while deleting ")
    return {"message":f"all blogs deleted"}