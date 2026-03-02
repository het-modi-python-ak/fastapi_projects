from pydantic import BaseModel


class PostCreate(BaseModel):
    title:str
    content:str
    


class PostResponse(BaseModel):
    title:str
    content:str
    

class Blogdb(BaseModel):
    blog_id : int
    title:str
    author:str
    description:str