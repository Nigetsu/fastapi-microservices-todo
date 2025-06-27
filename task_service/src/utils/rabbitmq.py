import asyncio
import uuid

import aio_pika
import json
from uuid import UUID

from fastapi import HTTPException
from src.api.v1.services import TaskService

from src.utils.unit_of_work import UnitOfWork

from src.config import get_rb_url

RABBITMQ_URL = get_rb_url()


async def task_worker():
    print("✅ task_worker started and listening")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(
            "task_service_queue", durable=True
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        request_data = json.loads(message.body)
                        try:
                            user_id = UUID(request_data["user_id"])
                        except (KeyError, ValueError) as e:
                            print(f"Invalid or missing user_id: {e}")

                        uow = UnitOfWork()
                        service = TaskService(uow=uow)

                        executor_tasks = await service.get_executor_tasks_count(user_id)
                        observer_tasks = await service.get_observer_tasks_count(user_id)

                        response = {
                            "executor_tasks": executor_tasks,
                            "observer_tasks": observer_tasks,
                        }

                        print(f"↩️ Replying to: {message.reply_to}")
                        print(f"🔗 Correlation ID: {message.correlation_id}")

                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(response).encode(),
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )

                    except Exception as e:
                        print(f"❌ Error processing task stats: {e}")


async def get_user_info(user_id: UUID, timeout: float = 5.0) -> dict | None:
    print("✅ get_user_info started")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()

        callback_queue = await channel.declare_queue(exclusive=True, auto_delete=True)

        correlation_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()

        async def on_response(message: aio_pika.IncomingMessage):
            if message.correlation_id == correlation_id:
                data = json.loads(message.body)
                if not future.done():
                    future.set_result(data)

        await callback_queue.consume(on_response)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"user_id": str(user_id)}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id,
                reply_to=callback_queue.name
            ),
            routing_key="auth_service_user_info"
        )

        try:
            response = await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="User service did not respond in time")

        if response.get("error"):
            return None

        return response
