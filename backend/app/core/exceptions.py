"""Domain exceptions and FastAPI exception handlers."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.i18n import get_message


class AppError(Exception):
    """Base application error with Vietnamese error code."""

    def __init__(self, error_code: str, status_code: int = 400, details: dict | None = None):
        self.error_code = error_code
        self.status_code = status_code
        self.message = get_message(error_code)
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, error_code: str = "BILL_NOT_FOUND", details: dict | None = None):
        super().__init__(error_code, status_code=404, details=details)


class ConflictError(AppError):
    """Business rule violation (e.g. invalid status transition)."""

    def __init__(self, error_code: str, details: dict | None = None):
        super().__init__(error_code, status_code=409, details=details)


class ForbiddenError(AppError):
    """Insufficient permissions."""

    def __init__(self, error_code: str = "FORBIDDEN"):
        super().__init__(error_code, status_code=403)


def register_exception_handlers(app):
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        body = {"error_code": exc.error_code, "message": exc.message}
        if exc.details:
            body["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        for err in exc.errors():
            field = " → ".join(str(loc) for loc in err.get("loc", []))
            details.append({"field": field, "message": err.get("msg", "")})
        return JSONResponse(
            status_code=400,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": get_message("VALIDATION_ERROR"),
                "details": {"errors": details},
            },
        )
