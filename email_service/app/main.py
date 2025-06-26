from contextlib import asynccontextmanager

from fastapi import FastAPI
import asyncio
from app.rabbitmq import email_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Starting email-service lifespan")

    worker_task = asyncio.create_task(email_worker())

    try:
        yield
    finally:
        print("🛑 Stopping email-service lifespan")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            print("🧹 Email worker task cancelled cleanly")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "message": "Task Service is running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
