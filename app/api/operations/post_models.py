from fastapi import Request
from fastapi.responses import JSONResponse


async def create_model(config, request: Request) -> JSONResponse:  # FIXME: This should implement POST /models
    return JSONResponse(content=None, headers={}, status_code=201)
