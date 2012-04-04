"""
Models for django_haikus
"""
import pickle
from django.db import models
from django.db.models import Count
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from django.dispatch import receiver
from picklefield.fields import PickledObjectField

from haikus import HaikuText, Haiku
from haikus.evaluators import DEFAULT_HAIKU_EVALUATORS


class HaikuManager(models.Manager):
    """
    Manager with method for getting rated/un-rated comments
    """
    def rated(self):
        return self.get_query_set().annotate(ratings_count=Count('ratings')).exclude(ratings_count=0)

    def unrated(self):
        return self.get_query_set().annotate(ratings_count=Count('ratings')).filter(ratings_count=0)

    def composite(self):
        return self.get_query_set().filter(is_composite=True)

    def all_from_text(self, text):
        """
        Create HaikuModel objects for each haiku in the given text
        """
        haikus = []
        for haiku in text.get_haikus():       
            haiku_model = self._model_from_haiku(haiku, text)
            haikus.append(haiku_model)
        return haikus

    def one_from_text(self, text):
        """
        Create a HaikuModel for the first occurence of a haiku in the text
        """
        haiku_model = self._model_from_haiku(text.get_haiku(), text)
        return haiku_model

    def _model_from_haiku(self, haiku, text):
        """
        Method for construction a single HaikuModel instance
        """
        haiku_model = HaikuModel.objects.create(text=text)
        i = 0
        for line in haiku.get_lines():
            haiku_line = HaikuLine.objects.create(text=line, line_number=i, source=haiku_model)
            haiku_model.lines.add(haiku_line)
            i += 1
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
            child = SimpleHaiku
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
    source = generic.GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    @property
    def source_text(self):
        if hasattr(self.source, 'text'):
            return self.source.text
        else:
            return None
    
class HaikuModel(models.Model, Haiku):
    """
    A model wrapper for the Haiku object
    """
    lines = models.ManyToManyField(HaikuLine)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="haikus")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    text = generic.GenericForeignKey('content_type','object_id')
    quality = models.IntegerField(default=0)
    ratings = generic.GenericRelation(HaikuRating,
                                content_type_field='content_type',
                                object_id_field='object_id')
    up_votes = models.PositiveIntegerField(default=0)
    down_votes = models.PositiveIntegerField(default=0)
    is_composite = models.BooleanField(default=False)
    objects = HaikuManager()

    def get_lines(self):
        return [line.text for line in self.lines.all()]
    
    def set_quality(self):
        """
        Set the Haiku's quality field
        """
        quality = 0
        evaluators = getattr(settings, "HAIKU_EVALUATORS", DEFAULT_HAIKU_EVALUATORS)
        quality = self.calculate_quality(evaluators)
        self.quality = quality
    
    def average_human_rating(self):
        ratings = self.ratings.all()
        if ratings.count() > 0:
            return sum([rating.rating for rating in ratings]) / len(ratings)
        else:
            return None

    def save(self, *args, **kwargs):
        if self.text is not None and not isinstance(self.text, BaseHaikuText):
            raise TypeError("Text model must descend from BaseHaikuText")
        return super(HaikuModel, self).save(*args, **kwargs)
        
class SimpleText(BaseHaikuText):
    """
    A simple descendant of BaseText
    """
    pass


