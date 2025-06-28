import aio_pika
import json
from uuid import UUID

from src.api.v1.services import TaskService

from src.utils.unit_of_work import UnitOfWork

from src.config import get_rb_url

RABBITMQ_URL = get_rb_url()


async def task_worker():
    print("🚀 task_worker started and listening")
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
                        watcher_tasks = await service.get_watcher_tasks_count(user_id)

                        response = {
                            "executor_tasks": executor_tasks,
                            "watcher_tasks": watcher_tasks,
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
