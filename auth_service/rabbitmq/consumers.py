import aio_pika
import json

from users.crud import UserDAO

from core.config import get_rb_url

RABBITMQ_URL = get_rb_url()


async def user_info_worker():
    print("🚀 Starting user info worker")
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
