import aio_pika
import uuid
from uuid import UUID
import asyncio
import json

from fastapi import HTTPException
from users.crud import UserDAO
from core.config import settings

RABBITMQ_URL = settings.RABBITMQ_URL


async def get_task_stats(user_id: UUID, timeout: float = 5.0) -> dict:
    print("getting task stats")
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
        )


async def publish_user_registered_event(user_id: str, email: str):
    print("Publishing user registered event")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()

        message = {
            "type": "user_registered",
            "data": {
                "user_id": user_id,
                "email": email
            }
        }

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="email.notifications"
        )


async def user_info_worker():
    print("Starting user info worker")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("auth_service_user_info", durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        user_id = data["user_id"]

                        user = await UserDAO.find_one_or_none(id=user_id)
                        if not user:
                            response = {"error": "User not found"}
                        else:
                            response = {
                                "user_id": str(user.id),
                                "username": user.username,
                                "email": user.email,
                            }

                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(response).encode(),
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                correlation_id=message.correlation_id
                            ),
                            routing_key=message.reply_to
                        )

                    except Exception as e:
                        print(f"Error processing user info: {e}")
