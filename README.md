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
this purpose.

For example:
```python
class OprahTranscript(BaseHaikuText):
  # any fields you'd like to add
  guest = models.CharField(max_length=255)
```

Or you can use the included SimpleText model.

Now you can create HaikuModel objects like so:
```python
#create a text from which we can mine haikus
text = OprahTranscript.objects.create(text="That you thought would be particularly stimulating to your creative process. That’s why you wanted to come here? To finish?")

# now you can create HaikuModel objects, all_from_text saves them and returns a list
haikus = HaikuModel.objects.all_from_text(text=text)
```
now you've got a HaikuModel for each possible haiku in your source text.

##Composition

##Sources

##Evaluation

