import redis
from django.conf import settings

client = lambda: redis.Redis(db=settings.REDIS['db'], host=settings.REDIS['host'])
