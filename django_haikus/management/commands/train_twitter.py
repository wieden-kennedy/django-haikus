"""
A management command for training our markov model for haiku line quality
"""
import re
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from haikus import HaikuText
from markov.markov import Markov
from twitter_easy_streamer.streamer import Rule, RuleListener

data = Markov(prefix=getattr(settings, "MARKOV_DATA_PREFIX", "goodlines"),  **getattr(settings, 'REDIS', {}))

def strip_tweets(tweets):
    """
    Pull offending hashtags, URLs and handles from tweets
    """
    stripped_tweets = []
    for tweet in tweets:
        stripped = re.sub(r'RT(:|\s)?|@([A-Za-z0-9_:]+)|#([A-Za-z0-9_]+)|(http.*?://([^\s)\"](?!ttp:))+)',"", tweet.text).strip()
        stripped_tweets.append(stripped)
    return stripped_tweets

def handle_tweets(tweets):
    """
    Handle tweets by stripping out hashtags, handles, URLs and other offending items
    """
    tweet_text = strip_tweets(tweets)
    for tweet in tweet_text:
        #add the split tweet (a list of words) to our markov model
        data.add_line_to_index(HaikuText(tweet).filtered_text().lower().split())
        
class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Get tweets and place them in our database of markov chains
        """
        listener = RuleListener()
        auth = getattr(settings, "TWITTER_AUTH", None)

        if auth is None:
            print "please add TWITTER_AUTH to your settings"
        else:
            # a very inclusive twitter stream to get lots of single lines
            rules = [Rule(track=["be", "the", "to", "and"], on_status=[handle_tweets])]
            listener.listen(rules=rules, **auth)
