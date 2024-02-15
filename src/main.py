import uvicorn
from fastapi import FastAPI, Request, status
from pydantic import ValidationError

from config import settings
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from auth.router import router as users_router


app = FastAPI(
    title="Vocabulary App",
)


# Благодаря этой функции клиент видит ошибки, происходящие на сервере, вместо "Internal server error"
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"details": exc.errors()}),
    )


app.include_router(router=users_router, prefix=settings.api_v1_prefix)
# app.include_router(router=test_users_router, prefix=settings.api_v1_prefix)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
