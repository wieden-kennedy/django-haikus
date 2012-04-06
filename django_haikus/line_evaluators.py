"""
Evaluators for individual haiku lines
"""
from django.conf import settings

from markov.markov import Markov

class LineEvaluator(object):
    def __init__(self, weight=1):
        self.weight = weight
        self.pre_evaluate()

    def __call__(self, line):
        return self.weight * self.evaluate(line)

    def pre_evaluate(self):
        pass
    
    def evaluate(self, line):
        """
        Evaluate a line
        """
        return 100

class MarkovLineEvaluator(LineEvaluator):
    """
    Evaluate a haiku line based on it's fit with our markov model
    """
    def __init__(self, weight=1, prefix=None):
        self.prefix = prefix or getattr(settings, "MARKOV_DATA_PREFIX", "goodlines")
        self.markov_data = Markov(prefix=prefix, **getattr(settings, 'REDIS', {}))
        super(MarkovLineEvaluator, self).__init__(weight=weight)
        
    def evaluate(self, line):
       return self.markov_data.score_for_line(line.split())


DEFAULT_LINE_EVALUATORS = [
    (MarkovLineEvaluator, 1),
]
