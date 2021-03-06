"""
Tests for django_haikus app
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError, models

from django_haikus.models import HaikuRating, HaikuModel, HaikuLine, SimpleText, HaikuLine, HaikuSource
from django_haikus.evaluators import SentimentEvaluator, MarkovEvaluator, FullTextMarkovEvaluator
from django_haikus.line_evaluators import LineEvaluator, MarkovLineEvaluator
from django_haikus.bigrams import BigramHistogram
from django_haikus.composer import pick_random, compose_haikus
from django_haikus.util import twitter_shares_for_url, facebook_shares_for_url, get_shares_for_url
from django_haikus.redis_client import client as redis_client
from tagging.models import Tag
from django_haikus.management.commands.train_twitter import strip_tweets

class HaikuRatingTest(TestCase):
    """
    Test the HaikuRating model
    """
    def test_rate_non_haiku(self):   
        #user is not an instance of BaseHaiku
        self.user = User.objects.create_user('test', 'test@wk.com', 'password')
        rating = HaikuRating(haiku=self.user, rating=50, user="grant")
        self.assertRaises(TypeError, rating.save)
        self.assertEqual(HaikuRating.objects.count(), 0)

class HaikuManagerTest(TestCase):
    """
    Test that the HaikuManager gets the correct haikus via
    is rated/unrated methods
    """
    def setUp(self):
        self.text = SimpleText.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        self.text2 = SimpleText.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence once more.")
        self.rated = HaikuModel.objects.one_from_text(self.text)
        rated = HaikuModel.objects.get(pk=self.rated.pk)
        rating = HaikuRating.objects.create(haiku=self.rated, rating=10, user="grant")
        self.unrated = HaikuModel.objects.one_from_text(self.text2)
        self.unrated.save()

    def test_composite(self):
        """
        Test that the composite method returns only those haikus that are marked as composites
        """
        self.rated.is_composite=True
        self.rated.save()
        self.assertTrue(self.rated in HaikuModel.objects.composite())
        self.assertFalse(self.unrated in HaikuModel.objects.composite())

    def test_rated(self):
        rated_haikus = HaikuModel.objects.rated()
        self.assertTrue(self.rated in rated_haikus)
        self.assertFalse(self.unrated in rated_haikus)

    def test_unrated(self):
        unrated_haikus = HaikuModel.objects.unrated()
        self.assertTrue(self.unrated in unrated_haikus)
        self.assertFalse(self.rated in unrated_haikus)

    def test_all_from_text(self):
        text = SimpleText.objects.create(text="frak "*100)
        # we create no duplicates
        assert len(HaikuModel.objects.all_from_text(text)) == 1
        assert len(HaikuModel.objects.all_from_text(text)) == 0
        # the text should be marked as having a haiku
        assert text.is_haiku

        #there are 2 unique haikus here
        text = SimpleText.objects.create(text="frik frak "*100)
        assert len(HaikuModel.objects.all_from_text(text)) == 2
        # the text should be marked as having a haiku
        assert text.is_haiku

        

class HaikuModelTest(TestCase):
    def setUp(self):
        self.text = SimpleText.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        HaikuModel.objects.all_from_text(self.text)

    def test_get_lines(self):
        """
        Ensure that get_lines returns a list of unicode/strings
        """
        haiku = HaikuModel.objects.all()[0]
        self.assertEqual(type(HaikuLine.objects.all()), type(haiku.lines.all()))
        self.assertEqual(type(haiku.get_lines()), list)
        self.assertTrue(type(haiku.get_lines()[0]) in [unicode, str])

    def test_haiku_lines_uniqueness(self):
        """
        Ensure that a haiku cannot have the exact set of lines from another haiku
        """        
        haiku = HaikuModel.objects.all()[0]

        haiku1 = HaikuModel.objects.create()
        lines = [haiku.lines.all()[1], haiku.lines.all()[1], haiku.lines.all()[1]]
        haiku1.lines.add(*lines)

        #this is bad
        haiku2 = HaikuModel.objects.create()
        self.assertRaises(IntegrityError, haiku2.lines.add, *lines)

        #should get no haikus for another run across the text
        assert len(HaikuModel.objects.all_from_text(self.text)) == 0

    def test_heat(self):
        """
        Ensure the heat method works as expected
        """
        class DummySource(models.Model, HaikuSource):
            def get_url_for_haiku(self, haiku):
                return "http://www.google.com"
            
        class MoronSource(models.Model, HaikuSource):
            pass
    
        haiku = HaikuModel.objects.all()[0]
        assert haiku.score() == 0

        self.assertRaises(ValueError, haiku.heat)

        haiku.source = MoronSource()
        self.assertRaises(NotImplementedError, haiku.score)

        haiku.source = DummySource()
        assert haiku.score() > 0
        assert redis_client().get(haiku._score_key()) == haiku.score()
        assert redis_client().ttl(haiku._score_key()) == 5*60
        assert haiku.get_heat() > 0
        assert haiku.get_heat() == haiku.heat

        #ensure heat changes with score
        heat = haiku.get_heat()
        assert haiku.get_heat(score=3) != heat
        assert haiku.heat == haiku.get_heat(score=3) 

class HaikuLineTest(TestCase):
    """
    Tests for the HaikuLine model
    """
    def setUp(self):
        self.text = SimpleText.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")        
        self.haiku = HaikuModel.objects.one_from_text(self.text)
        
    def test_source_text(self):
        self.assertEqual(HaikuLine.objects.count(), 3)
        line = HaikuLine.objects.order_by('?')[0]
        self.assertEqual(line.source_text, self.text)

    def test_calculate_quality(self):
        line = HaikuLine.objects.order_by('?')[0]
        evaluators = [(LineEvaluator, 1),]
        self.assertEqual(line.calculate_quality(evaluators=evaluators), 100)
        
        
class BaseHaikuTextTest(TestCase):
    """
    Simple tests for the BaseHaiku model
    """
    def test_set_syllable_count(self):
        text = SimpleText(text="here's some words")
        self.assertEqual(text.syllables, 0)
        text.set_syllable_count()
        self.assertEqual(text.syllables, text.syllable_count())
        self.assertFalse(text.is_haiku)

class HaikuRatingUITest(TestCase):
    """
    Tests for the user-facing Haiku rating UI
    """
    def setUp(self):
        self.comment = SimpleText.objects.create(text="Dog in the floor at, one onto the home for it, jump into the pool")
        self.haiku = HaikuModel.objects.one_from_text(self.comment)
        self.haiku.save()
        
    def test_rating(self):
        assert HaikuRating.objects.all().count() is 0
        rsp = self.client.post(reverse('trainer-login'), { 'name': 'nilesh' })
        self.assertEquals(rsp.status_code, 302)

        url = reverse('set-rating', args=[self.haiku.pk, 30])
        rsp = self.client.get(url)
        self.assertEquals(rsp.status_code, 302)
        assert HaikuRating.objects.all().count() is 1


class SentimentEvaluatorsTest(TestCase):
    """
    Test that sentiment evaluators classify haikus by the given tags and boost scores of matching
    comments accordingly.
    """
    def setUp(self):
        self.life_affirming_comment = SimpleText.objects.create(text="live "*17)
        self.morbid_comment = SimpleText.objects.create(text="die "*17)
        self.life_haiku = HaikuModel.objects.one_from_text(self.life_affirming_comment)
        self.death_haiku = HaikuModel.objects.one_from_text(self.morbid_comment)

        Tag.objects.add_tag(self.life_haiku, "life")
        Tag.objects.add_tag(self.death_haiku, "death")
        
        self.sentiment_evaluator = SentimentEvaluator(pos_tagname="life", neg_tagname="death")

    def test_sentiment_evaluator(self):
        # life affirming comment is life affirming
        self.assertEqual(self.sentiment_evaluator(self.life_haiku), 100)
        # morbid comment is morbid
        self.assertEqual(self.sentiment_evaluator(self.death_haiku), 0)       

        #this comment contains "death" words
        comment = SimpleText.objects.create(text="An old silent die... A frog jumps into the die. Splash! Silence again.")    

        # 0 points!
        self.assertEqual(self.sentiment_evaluator(HaikuModel.objects.one_from_text(comment)), 0)

        #this comment contains "life" words
        comment = SimpleText.objects.create(text="An old silent life... A frog jumps into the life. Splash! Silence again.")
        self.assertEqual(self.sentiment_evaluator(HaikuModel.objects.one_from_text(comment)), 100)

class MarkovEvaluatorsTest(TestCase):
    """
    Test the markov evaluator scores haikus according to their fit with a model for 'good' haiku line
    """
    def setUp(self):
        settings.REDIS.update({'db': 1})
        self.markov_evaluator = MarkovEvaluator(prefix="testevaluators")
        self.full_evaluator = FullTextMarkovEvaluator(prefix="testevaluators")
        self.good_lines = [
            ["jumped", "into", "the", "pool"],
            ["i", "jumped", "into", "it"],
            ["i", "jumped", "into", "mud"],
            ["it", "made", "a", "big", "sloppy","mess"],
            ["why", "did", "i", "do", "that"],
            ["why", "did", "we", "do", "that"]
            ]

        self.data = self.markov_evaluator.line_evaluator.markov_data
        for line in self.good_lines:
            self.data.add_line_to_index(line)

    def test_markov_evaluator(self):
        # this haiku matches our model perfectly
        comment = SimpleText.objects.create(text="i jumped into it, it made a big sloppy mess, why did i do that?")
        haiku = HaikuModel.objects.all_from_text(comment)[0]
        self.assertEqual(self.markov_evaluator(haiku), 100)

        #two lines in this haiku are "perfect"
        comment = SimpleText.objects.create(text="i jumped into it, it made a big sloppy mess, why did i do it?")
        haiku = HaikuModel.objects.all_from_text(comment)[0]
        self.assertEqual(self.markov_evaluator(haiku), 250.0/3)

    def test_markov_line_evaluator(self):
        comment = SimpleText.objects.create(text="i jumped into it, it made a big sloppy mess, why did i do that?")
        haiku = HaikuModel.objects.all_from_text(comment)[0]
        assert self.markov_evaluator.line_evaluator(haiku.lines.all()[0].text) == 100

        comment = SimpleText.objects.create(text="i jumped into it, it made a big sloppy mess, why did i do it?")
        haiku = HaikuModel.objects.all_from_text(comment)[0]
        assert self.markov_evaluator.line_evaluator(haiku.lines.all()[2].text) == 50

    def test_full_text_markov_evaluator(self):
        comment = SimpleText.objects.create(text="i jumped into it, it made a big sloppy mess, why did i do that?")
        haiku = HaikuModel.objects.all_from_text(comment)[0]
        self.assertEqual(self.full_evaluator(haiku), 1000.0/14)

        
    def tearDown(self):
        self.data.client.flushdb()

class BigramHistogramConstructionTest(TestCase):
    """
    Test that (A) the bigram histogram is constructed correctly 
    """
    def setUp(self):
        settings.REDIS.update({'db': 1})
        settings.TEXT_MODEL = SimpleText
        self.histogram = BigramHistogram()
        self.histogram.flush()
        
    def test_histogram_values(self):
        test_histogram = {
            'A,can': 1,
            'can,of': 1,
            'of,cherry': 1,
            'cherry,coke': 1,
            'coke,makes': 1,
            'makes,the': 1,
            'the,thing': 1,
            'thing,awesome': 1,
            'watch,for': 1,
            'for,the': 1,
            'the,sunrise': 1,
            'sunrise,and': 1,
            'and,in': 1,
            'in,a': 2,
            'a,split': 1,
            'split,second': 1,
            'second,and': 1,
            'and,there': 1,
            'there,goes': 2,
            'goes,the': 1,
            'the,boat': 1,
            'boat,across': 1,
            'across,the': 1,
            'the,horizon': 1,
            'a,true': 1,
            'true,soul': 1,
            'soul,surfer': 1,
            'surfer,there': 1,
            'goes,an': 1,
            'an,absolute': 1,
            'absolute,legend': 1,
            'legend,in': 1,
            'a,second': 1,
        }

        self.comments = []
        SimpleText.objects.create(text="A can of cherry coke makes the thing awesome")
        SimpleText.objects.create(text="Watch for the sunrise, and in a split second and there goes the boat across the horizon")
        SimpleText.objects.create(text="a true soul surfer, there goes an absolute legend in a second")

        self.assertEquals(len(test_histogram.keys()), 33)

        self.assertEqual(self.histogram.key, "simpletext")
        self.assertEqual(self.histogram.count(), 33 + 2) # plus 2 for __max, on for __max_bigram
        self.assertEqual(self.histogram.max(), 2)

        self.assertEqual(self.histogram.max_bigram(), "there,goes")
        self.assertEqual(self.histogram.get('there,goes'), 100.0)
        self.assertEqual(self.histogram.get('a,true'), 50.0)
        self.assertEqual(self.histogram.get('nilesh,ashra'), False)

    def testAutoPopulationOnCommentCreation(self):
        comment = SimpleText.objects.create(text="i jumped into it, it made a big sloppy mess, why did i do that?")
        self.assertEqual(self.histogram.count(), 14 + 2) # plus 2 for __max, on for __max_bigram

    def tearDown(self):
        self.histogram.flush()


class ComposeHaikuTests(TestCase):

    def test_pick_random(self):
        t1 = SimpleText.objects.create(text="An old silent pond... A frog jumps into the pond. Splash! Silence again hello the world is on the word for the win in case there is a word with out the loss of the win")        
        HaikuModel.objects.all_from_text(t1, source=t1)

        t2 = SimpleText.objects.create(text="Watch for the sunrise, and in a split second and there goes the boat across the horizon")
        HaikuModel.objects.all_from_text(t2, source=t2)

        assert HaikuModel.objects.count() > 0

        h = pick_random(HaikuModel)
        assert h.pk is not None

        assert HaikuModel.objects.filter(is_composite=True).count() == 0

        compose_haikus('1,2,1', source=t1, quality_threshold=0, count=10)

        assert HaikuModel.objects.filter(is_composite=True).count() > 1

class TwitterTrainerTests(TestCase):
    def test_strip_tweets(self):
        class FakeTweet(object):
            def __init__(self, text):
                self.text = text
                
        tweets = [FakeTweet("@RealGrantThomas @Comcast Audio recording or it didn't happen."),
                  FakeTweet("This http://t.co/i4Fnc0or could be the closest thing to Wonderland #hastag when all is said and done."),
                  FakeTweet("RT @Isabelawaldorf: #imagine you're kissing Louis, he's squeezing your bum and you reach for his braces to take them off, they cut your")]

        expected = ["Audio recording or it didn't happen.",
                    'This  could be the closest thing to Wonderland  when all is said and done.',
                    "you're kissing Louis, he's squeezing your bum and you reach for his braces to take them off, they cut your"]

        assert strip_tweets(tweets) == expected

class TestUtilityMethods(TestCase):
    """
    Test that our utility methods behave as expected
    """
    def test_social_shares_for_url(self):
        url = "http://www.google.com"
        assert twitter_shares_for_url(url) > 0
        assert facebook_shares_for_url(url) > 0
        assert get_shares_for_url(url) == (twitter_shares_for_url(url) + facebook_shares_for_url(url))


        url = "http://someurlwhichwillneverbeshared.xxx"
        assert twitter_shares_for_url(url) == 0
        assert facebook_shares_for_url(url) == 0
        assert get_shares_for_url(url) == 0

        #Facebook will return false on this, now we can handle it
        url = "http://localhost:8000"
        assert facebook_shares_for_url(url) == 0
