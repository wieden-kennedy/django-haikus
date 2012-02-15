import sys
import cPickle
from elementtree import ElementTree as ET

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from harvest.models import Video, Comment
import redis

class Command(BaseCommand):
    args = '<video_id>'
    help = 'Add a youtube video to the app'

    def handle(self, *args, **options):
        r = redis.Redis()
        while True:
            q, msg = r.blpop(settings.REDIS_CALCULATE_QUEUE)
            pk, evaluators, result_queue = cPickle.loads(msg)
            c = Comment.objects.get(pk=pk)
            calc_q = c.calculate_quality(evaluators=evaluators)
            rating = c.average_human_rating()
            distance = rating - calc_q
            r.lpush(result_queue, abs(distance))