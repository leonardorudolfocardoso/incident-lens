import os

from redis import Redis
from rq import Queue

redis_conn = Redis.from_url(os.environ["REDIS_URL"])
queue = Queue("incidents", connection=redis_conn)
