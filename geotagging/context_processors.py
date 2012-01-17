"""
Template Context Processors
"""
from django.conf import settings


def map_counter_reset(request):
    """
    This context processor resets the counter
    """
    request.session['geotagging_map_counter'] = 0
    return {}


def google_key(request):
    return {'GOOGLE_API_KEY':getattr(settings, 'GOOGLE_API_KEY', None)}