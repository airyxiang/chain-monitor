from redis import Redis
from chain_monitor.configurations.configuration import REDIS_URL

redis_client = None


def setup_redis():
    global redis_client
    redis_client = Redis(host=REDIS_URL, port=6379, db=0)


def get_redis_connection():
    if redis_client is None:
        setup_redis()
    return redis_client
