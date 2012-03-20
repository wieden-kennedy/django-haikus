from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_haikus.bigrams import BigramHistogram
import redis

class Command(BaseCommand):
    args = '<>'
    help = 'Manage bigram histogram/database'
    option_list = BaseCommand.option_list + (
        make_option('--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Reset the histogram hash for this project'),
        make_option('--load',
            action='store_true',
            dest='load',
            default=False,
            help='Load / create the histogram hash for this project'),
        make_option('--info',
            action='store_true',
            dest='info',
            default=False,
            help='Show histogram info'),
        make_option('--inspect',
            action='store',
            dest='inspect',
            default=None,
            help='Inspect a specific bigram'),
    )


    def handle(self, *args, **options):
        b = BigramHistogram()
        if options['reset']:
            b.flush()

        if options['load']:
            b.load()

        if options['info']:
            print "Histogram stored under key %s. Total bigram count: %s, and __max: %s (%s)" % (b.key, b.count(), b.max(), b.max_bigram())

        if options['inspect']:
            i = options['inspect']
            print "Normalized score for %s: " % i, b.get(i)
            print "Non-normalized score for %s: " % i, b.get(i, normalize=False)

