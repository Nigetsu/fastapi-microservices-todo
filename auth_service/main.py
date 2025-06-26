import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from users.rabbitmq import user_info_worker
from users.router import router as jwt_auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Starting auth-service lifespan")
    worker_task = asyncio.create_task(user_info_worker())

    try:
        yield
    finally:
        print("🛑 Stopping auth-service lifespan")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            print("🧹 Worker task cancelled cleanly")


app = FastAPI(title='FastAPI JWT Auth', lifespan=lifespan)

app.include_router(jwt_auth_router, prefix='/api')


@app.get("/")
async def root():
    return {
        "message": "Task Service is running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
