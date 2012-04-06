from django import forms
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django_haikus.models import HaikuModel

def compose_haikus(pattern, source=None, count=1, quality_threshold=80, debug='0', *args, **kwargs):
    pattern = pattern.split(",")
    h = []
    for i in range(0, int(count)):
        haikus = {}
        for i in set(pattern):          
            if source:                
                haikus[i] = HaikuModel.objects.filter(quality__gte=quality_threshold, content_type=ContentType.objects.get_for_model(source), object_id=source.id, is_composite=False).order_by('?')[0]
            else:
                haikus[i] = HaikuModel.objects.filter(quality__gte=quality_threshold, is_composite=False).order_by('?')[0]

        composed = HaikuModel.objects.create(is_composite=True, source=source)
        line = 0
        lines = []
        
        for source_haiku in pattern:
            lines.append(haikus[source_haiku].lines.all()[line])
            line += 1
        try:    
            composed.lines.add(*lines)
            composed.set_quality()
            composed.save()
            h.append(composed)
        except IntegrityError:
            composed.delete()
    return h

class ComposerForm(forms.Form):
    pattern = forms.CharField()
    count = forms.CharField()
    quality_threshold = forms.CharField()
    debug = forms.CharField()
