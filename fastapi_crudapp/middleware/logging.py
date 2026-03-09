import logging
import time
import json
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(
    filename="blog3.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="a",
    force=True
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Example API")


SENSITIVE_FIELDS = {"password", "token", "access_token", "refresh_token", "authorization", "secret"}


def mask_sensitive_data(data):
    """mask sensitive fields in JSON payload"""
    if isinstance(data, dict):
        return {
            key: ("******" if key.lower() in SENSITIVE_FIELDS else mask_sensitive_data(value))
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.perf_counter()

        body_bytes = await request.body()
        payload = None

        if body_bytes:
            try:
                body = json.loads(body_bytes)
                body = mask_sensitive_data(body)
                payload = json.dumps(body)
            except:
                payload = body_bytes.decode("utf-8")

        query_params = dict(request.query_params)

        logger.info(
            f"REQUEST | {request.client.host} | "
            f"{request.method} {request.url.path} | "
            f"Query: {query_params} | "
            f"Payload: {payload}"
        )

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        logger.info(
            f"RESPONSE | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.4f}s"
        )

        return response



