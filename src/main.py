import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from api import main_api_router as api_router
from config import settings


app = FastAPI(
    title="Vocabulary App",
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"details": exc.errors()}),
    )


app.include_router(router=api_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
