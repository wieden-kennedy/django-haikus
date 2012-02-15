from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext as RC
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse

from django_haikus.models import HaikuRating, BaseHaiku
from tagging.models import Tag

def login(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        if username:
            request.session['training-user'] = username
            return HttpResponseRedirect(reverse("train"))

    return render_to_response("harvest/login.html", { }, context_instance=RC(request))

def logout(request):
    del request.session['training-user']
    return HttpResponseRedirect(reverse("trainer-login"))

# Create your views here.
def train(request, id=None, rating=None, tag=None):
    # If the user isn't logged in, bounce them.
    if request.session.get('training-user') is None:
        return HttpResponseRedirect(reverse("trainer-login"))

    # If the user is giving us a numerical rating, store it in HaikuRating
    if id and rating:
        haiku = BaseHaiku.get_concrete_child().objects.get(pk=id)
        HaikuRating.objects.create(haiku=haiku, rating=rating, user=request.session['training-user'])
        haiku.save()
        return HttpResponseRedirect(reverse('train'))
    
    # Othwerise, store the tag
    elif id and tag:
        haiku = Comment.objects.get(pk=id)
        # note: removes other tags. fine as long as we're using one pair of tags.
        Tag.objects.update_tags(haiku, tag)
    
    haikus = BaseHaiku.get_concrete_child().objects.unrated().order_by("-quality")
    training_user = request.session.get('training-user')
    return render_to_response("django_haikus/train.html", { 'haikus': haikus, 'training_user': training_user }, context_instance=RC(request))
