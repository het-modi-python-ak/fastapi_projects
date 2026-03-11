from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import time

app = FastAPI()

@app.get("/")
def user():
    x = 9
    if x == 9:
        return {"yes"}
    if x == 0:
         raise HTTPException(status_code=401, detail="this is just return")

#  { "ip_address": [(t1), (t2), ...] }
request_counts = {}

RATE_LIMIT_WINDOW = 4
MAX_REQUESTS = 5



@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

   
    if client_ip in request_counts:
        # filter out timestamps older than the window
        request_counts[client_ip] = [
            t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_WINDOW
        ]

    # if the limit is exceeded
    if len(request_counts.get(client_ip, [])) >= MAX_REQUESTS:
        print("limit exceed ")
        raise HTTPException(
            status_code=429,
            detail="Too many requests, please try again later."
        )
      
    else:
        
        if client_ip not in request_counts:
            request_counts[client_ip] = []
        request_counts[client_ip].append(current_time)

   
    response = await call_next(request)
    
    response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(MAX_REQUESTS - len(request_counts[client_ip]))
    return response


@app.get("/user")
def limited_endpoint():
    return {"message": "This is the rate limitming example "}
