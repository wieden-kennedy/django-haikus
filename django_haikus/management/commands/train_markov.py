"""
A basic management command for training our markov evaluator with some saved corpora
"""
import re
import redis
import nltk
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from haikus import HaikuText
from markov.markov import Markov

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Seed our markov model with phrases from the nps_chat corpus
        """
        client = redis.Redis()
        if client.exists("train_nps"):
            print "Already trained on nps data!"
        else:
            pattern = re.compile('([a-zA-Z0-9\-]*User\d+|ACTION)')
            markov_data = Markov(prefix=getattr(settings, "MARKOV_DATA_PREFIX", "goodlines"))
            for line in nltk.corpus.nps_chat.xml_posts():
                if line.text not in ['JOIN','PART','<empty>'] and len(line.text.split()) > 2:
                    if re.search(pattern, line.text) is None:
                        good_line = HaikuText(line.text.lower()).filtered_text().split()
                        if len(good_line) > 0:
                            markov_data.add_line_to_index(line)
            client.incr("train_nps")
        for line in nltk.corpus.movie_reviews.sents():
            print line
        
        
