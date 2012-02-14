"""
Models for django_haikus
"""
from django.db import models
from django.db.models import Count
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from haikus import HaikuText
from haikus.evaluators import DEFAULT_HAIKU_EVALUATORS


class HaikuManager(models.Manager):
    """
    Manager with method for getting rated/un-rated comments
    """
    def rated(self):
        return self.get_query_set().annotate(ratings_count=Count('ratings')).filter(is_haiku=True).exclude(ratings_count=0)

    def unrated(self):
        return self.get_query_set().annotate(ratings_count=Count('ratings')).filter(is_haiku=True, ratings_count=0)
        
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
        if not isinstance(self.haiku, BaseHaiku):
            raise TypeError("Rated model must descend from HaikuBase")
        super(HaikuRating, self).save(*args, **kwargs)
        
class BaseHaiku(models.Model, HaikuText):
    """
    Abstract base model for haiku text sources
    """
    text = models.TextField(unique=True)
    syllables = models.IntegerField(default=0)
    quality = models.IntegerField(default=0)
    is_haiku = models.BooleanField(default=False)                                
    ratings = generic.GenericRelation(HaikuRating,
                                content_type_field='content_type',
                                object_id_field='object_id')

    objects = HaikuManager()
    
    def __unicode__(self):
        return self.text

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def set_syllable_count(self, save=False):
        self.syllables = self.syllable_count()
        self.is_haiku = bool(self.haiku())
        if save:
            self.save()

    def set_quality(self, save=False):
        """
        Set the Comment's quality field
        """
        quality = 0
        if self.is_haiku:
            evaluators = getattr(settings, "HAIKU_EVALUATORS", DEFAULT_HAIKU_EVALUATORS)
            quality = self.calculate_quality(evaluators)
        self.quality = quality
        if save:
            self.save()
    
    def average_human_rating(self):
        ratings = self.ratings.all()
        if ratings.count() > 0:
            return sum([rating.rating for rating in ratings]) / len(ratings)
        else:
            return None

    def save(self, *args, **kwargs):
        self.set_syllable_count()
        self.set_quality()
        super(BaseHaiku, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class SimpleHaiku(BaseHaiku):
    """
    A very simple descendant of BaseHaiku
    """
    pass
