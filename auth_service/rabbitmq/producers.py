import aio_pika
import uuid
from uuid import UUID
import asyncio
import json

from aio_pika import ExchangeType
from fastapi import HTTPException

from core.config import get_rb_url

RABBITMQ_URL = get_rb_url()


async def publish_user_registered_event(user_id: str, email: str):
    print("🚀 Publishing user registered event")
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                "notifications",
                ExchangeType.TOPIC,
                durable=True
            )

            message = {
                "type": "user_registered",
                "data": {
                    "user_id": user_id,
                    "email": email
                }
            }

            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key="email.notifications"
            )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to publish user registration event: {str(e)}"
        ) from e


async def get_task_stats(user_id: UUID, timeout: float = 5.0) -> dict:
    print("🚀 Getting task stats")
    try:
        async with await aio_pika.connect_robust(RABBITMQ_URL) as connection:
            async with connection.channel() as channel:
                callback_queue = await channel.declare_queue(
                    exclusive=True,
                    auto_delete=True
                )

                correlation_id = str(uuid.uuid4())
                future = asyncio.get_event_loop().create_future()

                async def on_response(message: aio_pika.IncomingMessage):
                    async with message.process():
                        print("Response received:", message.body)
                        if message.correlation_id == correlation_id:
                            future.set_result(json.loads(message.body.decode()))

                await callback_queue.consume(on_response)

                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps({"user_id": str(user_id)}).encode(),
                        correlation_id=correlation_id,
                        reply_to=callback_queue.name,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key="task_service_queue"
                )

                try:
                    response = await asyncio.wait_for(future, timeout=timeout)
                    return response
                except asyncio.TimeoutError:
                    future.cancel()
                    raise HTTPException(
                        status_code=504,
                        detail="Task service response timeout"
                    )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"RabbitMQ connection error: {str(e)}"
        ) from e
