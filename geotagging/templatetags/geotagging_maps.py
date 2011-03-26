from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag
from django import template
from django.template.loader import render_to_string

from geotagging.models import PointGeoTag

register = template.Library()

class Javascript(InclusionTag):
    name = 'geotagging_maps_api'
    template = 'geotagging/map_scripts.html'

register.tag(Javascript)


"""
Loosly based on dajngo-easy-maps: https://bitbucket.org/kmike/django-easy-maps/overview
"""
class Map(InclusionTag):
    name = 'geotagging_map'
    template = 'geotagging/map.html'
    options = Options(
        Argument('latlng'),
        Argument('title', default='Map', required=False),
        Argument('width', default='300', required=False),
        Argument('height', default='400', required=False),
        Argument('zoom', default='16', required=False)
    )

    def get_context(self, context, latlng, title, width, height, zoom):
        context['geotagging_map_counter'] = context.get('geotagging_map_counter', 0) + 1
        id = context['geotagging_map_counter']
        if isinstance(latlng, PointGeoTag):
            latlng_str = latlng.get_point_coordinates(as_string=True, inverted=True)
        else:
            latlng_str = latlng
        return {'title': title,
                'map_id': id,
                'width': width,
                'height': height,
                'LatLng': latlng_str,
                #'LatLng':'55.6845043579,12.5735950447',
                'zoom': zoom,
                }

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
