"""
Template Context Processors
"""

def map_counter_reset(request):
    """
    This context processor resets the counter
    """
    request.session['geotagging_map_counter'] = 0
    return {}
