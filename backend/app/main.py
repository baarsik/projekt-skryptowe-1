from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.core.database import init_db
from app.core.middleware import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


init_db()

app = FastAPI(lifespan=lifespan)
app.add_middleware(AuthMiddleware)
app.include_router(auth_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"msg": "Hello World"}