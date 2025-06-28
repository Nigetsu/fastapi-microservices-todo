import asyncio

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api import router
from src.rabbitmq import task_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Starting task-service lifespan")
    worker_task = asyncio.create_task(task_worker())

    try:
        yield
    finally:
        print("🛑 Stopping task-service lifespan")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            print("🧹 Worker task cancelled cleanly")


app = FastAPI(title='FastAPI Onion Architecture', lifespan=lifespan)

app.include_router(router, prefix='/api')


@app.get("/")
async def root():
    return {
        "message": "Task Service is running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
