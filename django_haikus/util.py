"""
Utility methods for django_haikus
"""
import json
import requests

TWITTER_URL = "http://urls.api.twitter.com/1/urls/count.json?url=%s"
FB_URL = "https://graph.facebook.com/%s"

def twitter_shares_for_url(url):
    """
    Get the total number of twitter shares for the given URL
    """
    response = requests.get(TWITTER_URL % url)
    response_dict = json.loads(response.text)
    try: 
        return int(response_dict['count'])
    except KeyError:
        return 0

def facebook_shares_for_url(url):
    """
    Get the total number of facebook shares/likes/comments for the given URL
    """
    response = requests.get(FB_URL % url)
    response_dict = json.loads(response.text)
    try:
        return int(response_dict['shares'])
    except KeyError:
        return 0


def get_shares_for_url(url):
    """
    Get the total number of twitter and facebook shares for the given URL
    """
    return twitter_shares_for_url(url) + facebook_shares_for_url(url)
