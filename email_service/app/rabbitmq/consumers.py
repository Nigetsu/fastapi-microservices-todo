import aio_pika
import json

from aio_pika import ExchangeType
from app.config import get_rb_url

RABBITMQ_URL = get_rb_url()


async def email_worker():
    print("🚀 Email worker started and listening")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "notifications",
            ExchangeType.TOPIC,
            durable=True
        )
        queue = await channel.declare_queue(
            "email_worker_queue",
            durable=True
        )
        binding = await queue.bind(
            exchange,
            routing_key="email.notifications"
        )
        print(f"✅ Binding established: {binding}")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        event = json.loads(message.body)
                        email = event["data"]["email"]
                        user_id = event["data"]["user_id"]
                        print(f"❎ Sending welcome email to {email} (user_id={user_id})")
                    except (KeyError, json.JSONDecodeError) as e:
                        print(f"❌ Malformed message: {e}")
                        await message.nack(requeue=False)
