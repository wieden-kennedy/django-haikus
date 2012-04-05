from django import forms
from django.db import IntegrityError
from django_haikus.models import HaikuModel

def compose_haikus(pattern, count=1, quality_threshold=80, debug='0', *args, **kwargs):
    pattern = pattern.split(",")

    h = []
    for i in range(0, int(count)):
        haikus = {}
        for i in set(pattern):
            haikus[i] = HaikuModel.objects.filter(quality__gte=quality_threshold).order_by('?')[0]

        composed = HaikuModel.objects.create(is_composite=True)
        line = 0
        lines = []
        
        for source_haiku in pattern:
            lines.append(haikus[source_haiku].lines.all()[line])
            line += 1
        try:    
            composed.lines.add(*lines)
            h.append(composed)
        except IntegrityError:
            composed.delete()
    return h

class ComposerForm(forms.Form):
    pattern = forms.CharField()
    count = forms.CharField()
    quality_threshold = forms.CharField()
    debug = forms.CharField()
