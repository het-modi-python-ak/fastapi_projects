from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

app = FastAPI()

# { "ip_address": [t1, t2, ...] }
request_counts = {}
RATE_LIMIT_WINDOW = 4
MAX_REQUESTS = 5

class RateLimiter(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Initialize IP if not present
        if client_ip not in request_counts:
            request_counts[client_ip] = []

        # Filter out timestamps older than the window
        request_counts[client_ip] = [
            t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_WINDOW
        ]

        # Check if the limit is exceeded
        if len(request_counts[client_ip]) >= MAX_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Too many requests, please try again later."
            )

        # Record the current request time
        request_counts[client_ip].append(current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(MAX_REQUESTS - len(request_counts[client_ip]))
        
        return response

# Add the middleware to the app
app.add_middleware(RateLimiter)

@app.get("/")
async def root():
    return {"message": "Hello World"}
