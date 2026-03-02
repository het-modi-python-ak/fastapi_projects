from pydantic import BaseModel

class Blogdb(BaseModel):
    blog_id : int
    title:str
    author:str
    Content:str