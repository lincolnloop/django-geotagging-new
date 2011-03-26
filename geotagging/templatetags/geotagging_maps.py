from django import template
from django.template.loader import render_to_string
from django.db.models.query import QuerySet

from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag

from geotagging.models import PointGeoTag

register = template.Library()

class Javascript(InclusionTag):
    name = 'geotagging_maps_api'
    template = 'geotagging/map_scripts.html'

register.tag(Javascript)


"""
Loosly based on dajngo-easy-maps: https://bitbucket.org/kmike/django-easy-maps/overview
"""
class MapObjects(InclusionTag):
    name = 'geotagging_map'
    template = 'geotagging/map.html'
    options = Options(
        Argument('objects'),
        Argument('width', default='300', required=False),
        Argument('height', default='400', required=False),
        Argument('zoom', default='16', required=False)
    )

    def get_context(self, context, objects, width, height, zoom):
        import ipdb; ipdb.set_trace()
        self.geotagging_map_counter = getattr(self, 'geotagging_map_counter', 0) + 1
        id = context['geotagging_map_counter']
        if isinstance(objects, PointGeoTag):
            latlng = objects.get_point_coordinates(as_string=True, inverted=True)
            markers = [{'latlng':latlng, 'object': objects}]
        elif isinstance(objects, basestring):
            latlng = objects
            markers = [{'latlng':latlng}]
        elif isinstance(objects, QuerySet) or isinstance(objects, list):
            latlng = objects[0].get_point_coordinates(as_string=True, inverted=True)
            markers = [{'latlng': i.get_point_coordinates(as_string=True, inverted=True),
                        'object': i} for i in objects]
        else:
            raise template.TemplateSyntaxError(
                'The first parameter must be either a PointGeoTag subclass, '
                'a queryset of PointGeoTag subclasses, '
                'a list of PointGeoTag subclases or a LatLong string. '
                'A %s was given' % type(objects))

        return {'map_id': id,
                'width': width,
                'height': height,
                'latlng': latlng,
                'markers': markers,
                'zoom': zoom,
                }

register.tag(MapObjects)


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
