"""
Haiku evaluators, callables that give a quality score (out of 100)
to a haiku based on some criteria.
"""
import re, math
import redis
import nltk
import nltk.collocations
from nltk.classify import NaiveBayesClassifier

from django.db.models import get_model
from django.conf import settings

from tagging.models import Tag, TaggedItem
from haikus.evaluators import HaikuEvaluator
from django_haikus.models import BaseHaiku

class SentimentEvaluator(HaikuEvaluator):
    """
    Evaluate a comment by some sentiment (i.e. humorous, not humorous)
    """
    def __init__(self, pos_tagname, neg_tagname, weight=1):
        """
        Create and train a NaiveBayesClassifier for this instance that will
        attempt to classify comments by out positive/negative tags
        """
        self.pos_tag, created = Tag.objects.get_or_create(name=pos_tagname)
        self.neg_tag, created = Tag.objects.get_or_create(name=neg_tagname)

        pos_comments = TaggedItem.objects.get_union_by_model(BaseHaiku.get_concrete_child(), self.pos_tag)
        neg_comments = TaggedItem.objects.get_union_by_model(BaseHaiku.get_concrete_child(), self.neg_tag)

        pos_feats = [(self.word_feats(pos.filtered_text().split()), pos_tagname) for pos in pos_comments]
        neg_feats = [(self.word_feats(neg.filtered_text().split()), neg_tagname) for neg in neg_comments]

        try:
            self.classifier = NaiveBayesClassifier.train(pos_feats + neg_feats)
        except ValueError:
            # looks like there were no features
            self.classifier = None
        super(SentimentEvaluator, self).__init__(weight=weight)
        
    def evaluate(self, comment):
        """
        Classify the given comment and boost its score if it matches our positive
        tag
        """
        score = 0
        if self.classifier is not None:
            tag = self.classifier.classify(self.word_feats(comment.filtered_text().split()))
            if tag == self.pos_tag.name:
                score = 100
        return score

    def word_feats(self, words):
        """
        Create an nltk-friendly featstruct from the given list of words
        """
        return dict([(word, True) for word in words])

class IsFunnyEvaluator(SentimentEvaluator):
    """
    Use sentiment analysis to determine if a comment is humorous
    and boost its score accordingly.
    """
    def __init__(self, weight=1):
        super(IsFunnyEvaluator, self).__init__("funny", "not_funny", weight=weight)

class BigramSplitEvaluator(HaikuEvaluator):
    """
    If the haiku splits a common bigram across lines, penalize it

    @todo: attempt to adjust score with respect to the score for the bigram
    being split (since most any combination of two words is techincally a bigram)
    """
    def evaluate(self, comment):
        score = 100
        bigrams = comment.line_end_bigrams()
        r = redis.Redis()
        for bigram in bigrams:
            try:
                bigram_score = r.hget(settings.BIGRAM_HASH_KEY, str(bigram))
                if (bigram_score > 0):
                    score -= 50
            except KeyError:
                pass
        return score
