from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag
from django import template

register = template.Library()

class Javascript(InclusionTag):
    name = 'include_maps_js'
    template = 'geotagging/map_scripts.html'

register.tag(Javascript)

"""
Notes:

Static:
 {% include_map_js %} - Adds the necessary javascript for the maps to load
 {% map_objects queryset %} - Creates a map showing all objects in the queryset
Interactive:
 {% map_objects Model %} - Creates a map showing all Model objects within the map section
 {% map_objects Model filter %} - Same as above, but adds filtering based on a function

Queue:
 ???
 {% include_queue_js element_id %} - Inncludes the javascript for the element queue
 {% show_queue %}

"""
