# src/app/core/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

HEADER = "X-Request-ID"

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get(HEADER) or str(uuid.uuid4())
        # inyecta en scope para usarlo en logs si quieres
        request.state.request_id = rid
        response: Response = await call_next(request)
        response.headers[HEADER] = rid
        return response
