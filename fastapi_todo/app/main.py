from fastapi import FastAPI
from database.database import Base, engine 
# Import the 'router' object from the 'auth', 'users', and 'tasks' modules
from routers import auth, users, tasks 
from middleware.logging import LoggingMiddleware
from  core.rate_limiter import RateLimiter


Base.metadata.create_all(bind=engine) 

app = FastAPI(title="FastAPI crud") 


# app.add_middleware(LoggingMiddleware) 
app.add_middleware(RateLimiter)


# Include the routers using the router object from each module
app.include_router(auth.router, tags=["Auth"], prefix="/auth") # Add prefixes for clarity
app.include_router(users.router, tags=["User"], prefix="/users") 
app.include_router(tasks.router, tags=["Tasks"], prefix="/tasks") 
