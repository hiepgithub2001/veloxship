"""FastAPI application entrypoint."""

import uuid

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, bills, service_tiers
from app.core.exceptions import register_exception_handlers

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

app = FastAPI(
    title="VeloxShip API",
    description="Logistics Delivery Bill Management — Backend",
    version="0.1.0",
)

# CORS — allow the Vite dev server in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers (Vietnamese error messages)
register_exception_handlers(app)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next) -> Response:
    """Add a unique request-ID and log each request."""
    request_id = str(uuid.uuid4())[:8]
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    logger.info("request.start", method=request.method, path=request.url.path)
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info("request.end", status_code=response.status_code)
    return response


# API v1 routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(bills.router, prefix="/api/v1")
app.include_router(service_tiers.router, prefix="/api/v1")
