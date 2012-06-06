import redis
from django.conf import settings

client = lambda: redis.Redis(**settings.REDIS)
