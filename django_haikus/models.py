"""
Models for django_haikus
"""
import pickle
import hashlib
import logging

from datetime import datetime, timedelta
from math import log

from redis.exceptions import ResponseError

from django.db import models, IntegrityError
from django.db.models import Count
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from picklefield.fields import PickledObjectField

from haikus import HaikuText, Haiku
from haikus.evaluators import DEFAULT_HAIKU_EVALUATORS

from line_evaluators import DEFAULT_LINE_EVALUATORS
from util import get_shares_for_url
from redis_client import client as redis_client

epoch = datetime(1970, 1, 1)
constant_seconds = 45000
logger = logging.getLogger(__name__)

class HaikuManager(models.Manager):
    """
    Manager with method for getting rated/un-rated comments
    """
    def rated(self):
        return self.get_query_set().annotate(ratings_count=Count('ratings')).exclude(ratings_count=0)

    def unrated(self):
        return self.get_query_set().annotate(ratings_count=Count('ratings')).filter(ratings_count=0)

    def composite(self, source=None):
        if source is None:
            qs = self.get_query_set()
        else:
            qs = self.by_source(source)
        return qs.filter(is_composite=True)

    def by_source(self, source):
        return self.get_query_set().filter(content_type=ContentType.objects.get_for_model(source), object_id=source.id)

    def all_from_text(self, text, source=None):
        """
        Create HaikuModel objects for each haiku in the given text
        """
        haikus = []
        text_haikus = text.get_haikus()
        if len(text_haikus) > 0:
            text.is_haiku = True
            text.save()
            
        for haiku in text_haikus:         
            haiku_model = self._model_from_haiku(haiku, text, source)
            if haiku_model:
                haikus.append(haiku_model)
        return haikus

    def one_from_text(self, text, source=None):
        """
        Create a HaikuModel for the first occurence of a haiku in the text
        """
        haiku_model = self._model_from_haiku(text.get_haiku(), text, source)
        return haiku_model

    def _model_from_haiku(self, haiku, text, source=None):
        """
        Method for construction a single HaikuModel instance
        """
        if source:
            haiku_model = HaikuModel.objects.create(source=source)
        else:
            haiku_model = HaikuModel.objects.create()
        i = 0
        lines = []
        for line in haiku.get_lines():
            haiku_line = HaikuLine.objects.create(text=line, line_number=i, source_text=text)
            haiku_line.set_quality()
            haiku_line.save()
            lines.append(haiku_line)
            i += 1
        try:
            haiku_model.lines.add(*lines)
            haiku_model.set_quality()
            haiku_model.save()
        except IntegrityError:
            haiku_model.delete()
            haiku_model = None
        return haiku_model                                    
        
class HaikuRating(models.Model):
    """
    A generic rating object that can be attached to a child of
    BaseHaiku to track human ratings
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    haiku = generic.GenericForeignKey('content_type','object_id')
    rating = models.IntegerField(default=0)
    user = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not isinstance(self.haiku, HaikuModel):
            raise TypeError("Rated model must descend from HaikuModel")
        super(HaikuRating, self).save(*args, **kwargs)
        
class BaseHaikuText(models.Model, HaikuText):
    """
    Abstract base model for haiku text sources
    """
    text = models.TextField(unique=True)
    syllables = models.IntegerField(default=0)
    is_haiku = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.text

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def set_syllable_count(self, save=False):
        self.syllables = self.syllable_count()
        self.is_haiku = bool(self.get_haiku())
        if save:
            self.save()
        
    def save(self, *args, **kwargs):
        self.set_syllable_count()
        super(BaseHaikuText, self).save(*args, **kwargs)

    def create_haiku_models(self):
        """
        Create HaikuModels from this text's haikus
        """
        for haiku in self.get_haikus():
            model = HaikuModel.from_haiku(haiku, text=self)

    @classmethod
    def get_concrete_child(cls):
        subclasses = BaseHaikuText.__subclasses__()
        try:
            subclasses.remove(SimpleText)
        except:
            pass

        if len(subclasses) > 0:
            child = getattr(settings, "TEXT_MODEL", subclasses[0])
        else:
            child = SimpleText
        return child
            
    class Meta:
        abstract = True

class HaikuLine(models.Model):
    """
    A model wrapper for an individual line in a haiku
    """
    line_number = models.IntegerField()
    text = models.TextField()   
    quality = models.IntegerField(default=0)
    
    source_text = generic.GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    def calculate_quality(self, evaluators=[]):
        """
        Calculate this line's quality
        """
        score = 0
        for evaluator_class, weight in evaluators:
            evaluator = evaluator_class(weight=weight)
            score += evaluator(self.text)
        try:
            score /= sum([weight for evaluator, weight in evaluators])
        except ZeroDivisionError:
            pass
        return score

    def set_quality(self):
        """
        Set the Line's quality field
        """
        quality = 0
        evaluators = getattr(settings, "LINE_EVALUATORS", DEFAULT_LINE_EVALUATORS)
        quality = self.calculate_quality(evaluators)
        self.quality = quality
    
    def save(self, *args, **kwargs):
        if self.source_text is not None and not isinstance(self.source_text, BaseHaikuText):
            raise TypeError("Text model must descend from BaseHaikuText")
        self.set_quality()
        super(HaikuLine, self).save(*args, **kwargs)

    class Meta:
        ordering = ('line_number',)
    
class HaikuModel(models.Model, Haiku):
    """
    A model wrapper for the Haiku object
    """
    lines = models.ManyToManyField(HaikuLine)
    quality = models.IntegerField(default=0, db_index=True)
    featured = models.BooleanField(default=False)
    is_composite = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    full_text = models.TextField(unique=True, null=True)
    heat = models.FloatField(null=True, blank=True)
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="haiku_source")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    source = generic.GenericForeignKey('content_type', 'object_id')
    
    
    ratings = generic.GenericRelation(HaikuRating,
                                      content_type_field='content_type',
                                      object_id_field='object_id')
    
    objects = HaikuManager()

    def get_lines(self):
        return [line.text for line in self.lines.all()]

    def flat_lines(self, separator="/"):
        return separator.join(self.get_lines())

    def set_quality(self):
        """
        Set the Haiku's quality field
        """
        quality = 0
        evaluators = getattr(settings, "HAIKU_EVALUATORS", DEFAULT_HAIKU_EVALUATORS)
        quality = self.calculate_quality(evaluators)
        self.quality = quality

    def score(self, ttl=5*60):
        """
        Get the 'score' for this HaikuModel, specifically the number of times it's been shared
        via social media

        @raises NotImplemented if source doesn't have get_url_for_haiku
        """
        score = 0
        if self.source is not None:
            score = redis_client().get(self._score_key())
            if score is None:                
                score = get_shares_for_url(self.source.get_url_for_haiku(self))
                redis_client().setex(self._score_key(), score, ttl)
                self.get_heat(score=score)
        return score
            
    def get_heat(self, score=None, epoch=epoch, constant_seconds=constant_seconds):
        """
        This HaikuModel's heat based on the reddit ranking algorithm described here:
        http://amix.dk/blog/post/19588
        """
        heat = self.heat
        if score is None:
            score = self.score()
        try:
            heat = log(float(score), 10) + self._epoch_seconds()/constant_seconds
        except ValueError:
            pass
        if heat != self.heat:
            self.heat = heat
            self.save()
        return heat

    def _epoch_seconds(self, epoch=epoch):
        """
        Get the number of seconds between self.created_at and the epoch
        """
        delta = self.created_at - epoch
        return delta.days * 86400 + delta.seconds

    def _score_key(self):
        return "haikuscore:%s" % self.id
    
    def average_human_rating(self):
        ratings = self.ratings.all()
        if ratings.count() > 0:
            return sum([rating.rating for rating in ratings]) / len(ratings)
        else:
            return None

class HaikuSource(object):
    """
    A mix-in class for sources of haikus, provides get_url_for_haiku
    """
    def get_url_for_haiku(self, haiku):
        raise NotImplementedError("subclasses of HaikuSource should implement get_url_for_haiku")

        
class SimpleText(BaseHaikuText):
    """
    A simple descendant of BaseText
    """
    pass


def create_unique_haiku_lines_key(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        key = hashlib.sha1()
        key.update(' '.join([line.text for line in HaikuLine.objects.filter(pk__in=pk_set)]))
        instance.full_text = key.hexdigest()
        instance.save()
    
m2m_changed.connect(create_unique_haiku_lines_key, sender=HaikuModel.lines.through)

def load_haiku_bigrams_into_bigram_db(sender, instance, created, **kwargs):
    if created:
        try:
            from django_haikus.bigrams import BigramHistogram
            BigramHistogram().load(instances=[instance])
        except ResponseError as e:
            #redis is full!
            logger.error("Redis response error: %s" % e)

