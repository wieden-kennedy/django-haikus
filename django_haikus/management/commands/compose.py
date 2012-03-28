import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_haikus.bigrams import BigramHistogram
from django_haikus.composer import compose_haikus

class Command(BaseCommand):
    args = '<>'
    help = 'Manage bigram histogram/database'
    option_list = BaseCommand.option_list + (
        make_option('--pattern',
            action='store',
            dest='pattern',
            default='1,1,2',
            help='Haiku line pattern, e.g.: 1,2,2'),

        make_option('--count',
            action='store',
            dest='count',
            default=1,
            help='Number of haikus to compose'),

        make_option('--quality_threshold',
            action='store',
            dest='quality_threshold',
            default=80,
            help='Quality of haikus'),

        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Whether to show debug'),
    )

    def handle(self, *args, **options):
        print compose_haikus(**options)