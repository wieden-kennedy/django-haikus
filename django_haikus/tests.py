"""
Tests for django_haikus app
"""
from django.test import TestCase
from django_haikus.models import HaikuRating, BaseHaiku, SimpleHaiku
from django.contrib.auth.models import User

class HaikuRatingTest(TestCase):
    """
    Test the HaikuRating model
    """
    def test_rate_non_haiku(self):
        self.haiku = SimpleHaiku.objects.create(text="Some text")
        rating = HaikuRating(haiku=self.haiku, rating=50, user="grant")
        rating.save()
        self.assertEqual(HaikuRating.objects.count(), 1)

        #user is not an instance of BaseHaiku
        self.user = User.objects.create_user('test', 'test@wk.com', 'password')
        rating = HaikuRating(haiku=self.user, rating=50, user="grant")
        self.assertRaises(TypeError, rating.save)
        self.assertEqual(HaikuRating.objects.count(), 1)

class HaikuManagerTest(TestCase):
    """
    Test that the HaikuManager gets the correct haikus via
    is rated/unrated methods
    """
    def setUp(self):
        self.rated = SimpleHaiku.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        rating = HaikuRating.objects.create(haiku=self.rated, rating=10, user="grant")
        self.unrated = SimpleHaiku.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence sometime.")

    def test_rated(self):
        rated_haikus = SimpleHaiku.objects.rated()
        self.assertTrue(self.rated in rated_haikus)
        self.assertFalse(self.unrated in rated_haikus)

    def test_unrated(self):
        unrated_haikus = SimpleHaiku.objects.unrated()
        self.assertTrue(self.unrated in unrated_haikus)
        self.assertFalse(self.rated in unrated_haikus)
        
class BaseHaikuTest(TestCase):
    """
    Simple tests for the BaseHaiku model
    """
    def test_set_syllable_count(self):
        haiku = SimpleHaiku(text="here's some words")

        self.assertEqual(haiku.syllables, 0)
        haiku.set_syllable_count()
        self.assertEqual(haiku.syllables, haiku.syllable_count())
        self.assertFalse(haiku.is_haiku)
