__all__ = [
    'get_user_info'
    'task_worker',
]

from src.rabbitmq.producers import get_user_info
from src.rabbitmq.consumers import task_worker