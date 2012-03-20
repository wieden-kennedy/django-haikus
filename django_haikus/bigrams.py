import redis
from django_haikus.models import BaseHaikuText

class BigramHistogram:

	def __init__(self, *args, **kwargs):
		self.model = BaseHaikuText.get_concrete_child()
		self.redis = redis.Redis()
		self.key = BaseHaikuText.get_concrete_child().__name__.lower()

	def load(self):
		instances = self.model.objects.all()
		for instance in instances:
			t = instance.filtered_text()
			words = t.split()
			for i in range(0, len(words)-1):
				w1, w2 = words[i:i+2]
				self.incr(w1, w2)

	def incr(self, w1, w2):
		count = self.redis.hincrby(self.key, self._build_field(w1, w2), 1)
		max = self.redis.hget(self.key, '__max')
		if max is None or int(count) > int(max):
			self.redis.hset(self.key, '__max_bigram', self._build_field(w1, w2))
			self.redis.hset(self.key, '__max', count)

	def _build_field(self, w1, w2):
		return "%s,%s" % (w1.lower(), w2.lower())

	def count(self):
		return self.redis.hlen(self.key)

	def max(self):
		try:
			return float(self.redis.hget(self.key, '__max'))
		except TypeError:
			return 0

	def get(self, key, normalize=True):
		score = self.redis.hget(self.key, key)
		if score is None:
			return False
			
		if normalize:
			scale = self.max() / 100.0
			return float(score) / scale
		else:
			return score

	def max_bigram(self):
		return self.get('__max_bigram', normalize=False)

	def lookup(self, bigram):
		return self.normalize(self.get(bigram))

	def flush(self):
		self.redis.delete(self.key)