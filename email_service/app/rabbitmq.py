import aio_pika
import json
from app.config import settings

RABBITMQ_URL = settings.RABBITMQ_URL

async def email_worker():
    print("🚀 Email worker started and listening")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("email.notifications", durable=True)

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