#Django Haikus

A Django app that helps you use [haikus](https://github.com/wieden-kennedy/haikus) to find haikus in arbitrary text,
save them to a database model and evaluate their quality.

Use it to make haikus out of your favorite text (IRC logs, RFCs, Oprah transcripts, religious texts and more!)

##Installation
To install django-haikus, use pip:
    ```pip install -e https://github.com/wieden-kennedy/django-haikus#egg=django_haikus```

##Basic Usage
First, put django-haikus in your installed apps like so:
```
INSTALLED_APPS = {  
  # some other apps
  'django_haikus'
}
```

Next, get some text and find haikus in it. Django-haikus conveniently provides the abstract BaseHaikuText model for exactly
this purpose. You can use the packaged SimpleText model or create your own.

For example:
```python
class OprahTranscript(BaseHaikuText):
  # any fields you'd like to add
  episode = models.ForeignKey(OprahEpisode)
```

Then you can add the TEXT_MODEL settings to settings.py a'la:
```python
from oprah_transcript.models import OprahTranscript
TEXT_MODEL = OprahTranscript
```

Now you can create your BaseHaikuText implementation and HaikuModel objects like so:
```python
#create a text from which we can mine haikus
text = OprahTranscript.objects.create(text="That you thought would be particularly stimulating to your creative process. That’s why you wanted to come here? To finish?")

# now you can create HaikuModel objects, all_from_text saves them and returns a list
haikus = HaikuModel.objects.all_from_text(text=text)
```
now you've got a HaikuModel for each possible haiku in your source text.

##Quality + Evaluation

###By Machines
HaikuModels can be rated in two different ways. First of all, each HaikuModel is scored by a set of callable evaluator classes.
Django-haikus (and haikus) come with a few evaluators for you to use. You can use the default set of nltk-based evaluators (from ```haikus.evaluators.DEFAULT_HAIKU_EVALUATORS```)
or any combination of the packaged evaluators and those that you author on your own.

Your haiku evaluator classes should inherit from ```haikus.evaluators.HaikuEvaluator``` and implement an evaluate method that
returns a score between 0 and 100. You can find some example evaluators in ```django_haikus.evaluators```.

Each evaluator can be weighted to increase or decrease its influence on HaikuModel quality. You can define your set of evaluators in
settings.py like so:

```python
from haikus.evaluators import NounVerbAdjectiveLineEndingEvaluator
from django_haikus.evaluators import BigramSplitEvaluator, MarkovEvaluator
from oprah_transcript.evaluators import BeesEvaluator
HAIKU_EVALUATORS = [(BigramSplitEvaluator, 1), (MarkovEvaluator, 1), (NounVerbAdjectiveLineEndingEvaluator, 0.5), (BeesEvaluator, 1)]
```

Django-haikus also includes evaluators for individual HaikuLine models, which can be defined in the same way via the 
LINE_EVALUATORS setting:
```python
from django_haikus.line_evaluators import MarkovLineEvaluator
from oprah_transcript.line_evaluators import FreeCarsLineEvaluator
LINE_EVALUATORS = [(MarkovLineEvaluator, 1), (FreeCarsLineEvaluator, 1)]
```
Line evaluators can be created in the same fashion as Haiku evaluators, simply inherit from ```django_haikus.line_evaluators.LineEvaluator``` and define your evaluate() method.

###By People
Django-haikus also includes some simple methods for creating 'human' scores for HaikuModels.

First, you can use the packaged training UI to provide human scores for HaikuModels via the HaikuRating.
See ```django_haikus.views.train``` for details.  HaikuModel has an ```average_human_rating()``` function that 
will give you the mean average of all of your human ratings for the instance.

Second, HaikuModel has a ```score()``` function that calculates the total number of Facebook and Twitter shares for a 
particular instance and a ```get_heat()``` function that calculates a Reddit-esque "heat" for that poem.  In order to use
```score()``` and ```get_heat()```, your HaikuModels will need a relation to a HaikuSource as described below.

##Sources
HaikuModel has a generic relation called source that can be used to attach an arbitrary 'source' model to each instance.
If your source model inherits from HaikuSource and implements ```HaikuSource.get_url_for_haiku()``` you can use the 
```get_heat()``` and ```score()``` functions of HaikuModel to find a social-sharing derived score for your haikus.

For example, say your texts are pulled from Oprah transcripts, but you'd like to associate each HaikuModel with a source
episode, you could create an OprahEpisode model like so.

```python
from django_haikus.models import HaikuSource
class OprahEpisode(models.Model, HaikuSource):
    guests = ManyToManyField(Celebrity)
    def get_url_for_for_haiku(self, haiku):
        return haiku.get_absolute_url()
```

Now you can associate a specific episode with a HaikuModel, by passing the source argument to all_from_text:

```python
from oprah_transcript.models import OprahEpisode
from oprah_transcript.models import OprahTranscript
from django_haikus.models import HaikuModel

#get a transcript
transcript = OprahTranscript.objects.order_by('?')[0]
HaikuModel.objects.all_from_text(text=transcript, source=transcript.episode)
```

You can also filter HaikuModel by source:

```python
some_episode = OprahEpisode.objects.order_by('?')[0]
the_haikus_from_some_episode = HaikuModel.objects.by_source(source=some_episode)
```

##Composition
Django-haikus can compose new haikus for you via the compose() function in ```django_haikus.composer```. compose()
will find haikus with machine-rated quality above the provided threshold and mash them up into new poetic masterpieces.

If you want *only* your composite poems, call ```HaikuModel.objects.composite()```


