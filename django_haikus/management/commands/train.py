import sys
from elementtree import ElementTree as ET

import redis
import cPickle
import string, random

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.conf import settings

import pyevolve
from pyevolve import G1DList, G2DList
from pyevolve import GSimpleGA
from pyevolve import Selectors
from pyevolve import Statistics
from pyevolve import DBAdapters

from haikus.evaluators import HAIKU_EVALUATORS

class Command(BaseCommand):
    args = '<video_id>'
    help = 'Add a youtube video to the app'

    def handle(self, *args, **options):
        # This function is the evaluation function, we want
        # to give high score to more zero'ed chromosomes
        r = redis.Redis()

        EVALUATORS = []
        evaluator_set = getattr(settings, 'HAIKU_EVALUATORS', HAIKU_EVALUATORS)
        def eval_func(chromosome):
            closeness = []

            i = 0
            for eval_cls in evaluator_set:
                EVALUATORS.append((eval_cls, float(chromosome[i])/100))
            try:
                rated_comments = BaseHaiku.get_concrete_child().objects().rated()
            except AttributeError:
                raise CommandError("BaseHaiku child-classes' manager must implement rated/unrated (see django_haikus.models.HaikuManager)"
                                   
            result_queue = "haiku:results_" + ''.join([random.choice(string.ascii_uppercase) for i in range(5)])
            for c in rated_comments:
                data = (c.pk, EVALUATORS, result_queue)
                r.lpush(settings.REDIS_CALCULATE_QUEUE, cPickle.dumps(data))

            results = []
            while True:
                results.append(float(r.blpop(result_queue)[1]))
                if(len(results) == len(rated_comments)):
                    break

            # `results` contains the *distance* from the target score
            #   i.e. a lower average score is better.
            # results = [100, 91, 80, 100, ...,]
            print results
            average_fitness = sum(results) / len(results)
            print "Average fitness: %s, scaled: %s" % (average_fitness, 100 - average_fitness)
            return 100 - average_fitness

        pyevolve.logEnable()

        genome = G1DList.G1DList(len(EVALUATORS))

        # Sets the range max and min of the 1D List
        genome.setParams(rangemin=0, rangemax=100)

        # The evaluator function (evaluation function)
        genome.evaluator.set(eval_func)

        # Genetic Algorithm Instance
        ga = GSimpleGA.GSimpleGA(genome)

        # Set the Roulette Wheel selector method, the number of generations and
        # the termination criteria
        #ga.selector.set(Selectors.GRouletteWheel)
        ga.setGenerations(5)
        # ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)

        # Sets the DB Adapter, the resetDB flag will make the Adapter recreate
        # the database and erase all data every run, you should use this flag
        # just in the first time, after the pyevolve.db was created, you can
        # omit it.
        sqlite_adapter = DBAdapters.DBSQLite(identify="ex1", resetDB=True)
        ga.setDBAdapter(sqlite_adapter)

        # Do the evolution, with stats dump
        # frequency of 20 generations
        ga.evolve(freq_stats=1)

        # Best individual
        print ga.bestIndividual()
