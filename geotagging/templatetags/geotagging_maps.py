from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag
from django import template

register = template.Library()

class Javascript(InclusionTag):
    name = 'include_maps_js'
    template = 'geotagging/map_scripts.html'

register.tag(Javascript)


class Map(InclusionTag):
    name = 'map'
    template = 'geotagging/map.html'

    def get_context(self, context):
        context.update({
                'title':'a map',
                'map_id': '1',
                'width': '100',
                'height': '100',
                'lat':'-34.397',
                'long':'150.644',
                'zoom': '0',
                'template_name': template_name
                })
        return context
register.tag(Map)

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
