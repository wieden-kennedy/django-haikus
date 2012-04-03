import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from haikus import HaikuText
from markov.markov import Markov
from twitter_easy_streamer.streamer import Rule, RuleListener


def add_to_markov(tweets):
    """
    Look through the 
    """
    markov_data = Markov(prefix=getattr(settings, "MARKOV_DATA_PREFIX", "goodlines"))
    pattern = re.compile('(@[a-zA-Z0-9_]|#[a-zA-Z0-9]|RT\s{1}|http:\/\/)')
    for tweet in tweets:
        if re.search(pattern, tweet.text) is None:
            line = HaikuText(tweet.text.lower()).filtered_text().split()
            markov_data.add_line_to_index(line)

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Seed our markov model with phrases from the nps_chat corpus
        """
        listener = RuleListener()

        AUTH = {
            'consumer_key': '9ejfkiCu8dTMNDzF29cg',
            'consumer_secret': 'SicnRgAMXu31xvJnpJtqtGOZEZazhDynb7sXLPTnNo',
            'access_token': '14112449-ZDgvgw5Hgj1hf1sZFWP0VSBnJBMOiVhbhgpNDWd5n',
            'access_token_secret': 'ZMtTEXGZ5aNnGrMF03l0lSkqCaouo0CjJbEiN41QlO4'
           }

        rules = [Rule(track=["the"], historical=True, on_status=[print_message])]
        listener.listen(rules=rules, **AUTH)
