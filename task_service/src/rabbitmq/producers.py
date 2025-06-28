import asyncio
import uuid

import aio_pika
import json
from uuid import UUID

from fastapi import HTTPException

from src.config import get_rb_url

RABBITMQ_URL = get_rb_url()


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
