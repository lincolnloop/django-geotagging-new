import ttag

from django import template
from django.template.loader import render_to_string
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.maps.google.zoom import GoogleZoom

from geotagging.models import PointGeoTag

register = template.Library()


class Javascript(ttag.Tag):

    class Meta:
        block = False
        name = 'geotagging_maps_api'

    def render(self, context):
        t = template.loader.get_template('geotagging/map_scripts.html')
        return t.render(template.Context({}))

register.tag(Javascript)


"""
Loosly based on dajngo-easy-maps: https://bitbucket.org/kmike/django-easy-maps/overview
"""
class MapObjects(ttag.Tag):
    class Meta:
        name = 'geotagging_map'
    
    objects = ttag.Arg(positional=True)
    width = ttag.Arg(required=False)
    height = ttag.Arg(required=False)
    zoom = ttag.Arg(required=False)
    static = ttag.Arg(required=False)
    extra = ttag.Arg(required=False)

    def render(self, context):
        data = self.resolve(context)
        objects = data.get('objects', None)
        width = data.get('width', None)
        height = data.get('height', None)
        zoom = data.get('zoom', None)
        static = data.get('static', None)
        extra = data.get('extra', None)

        context['request'].session['geotagging_map_counter'] = (
            context['request'].session.get('geotagging_map_counter', 0) + 1)
        id = context['request'].session['geotagging_map_counter']

        if isinstance(objects, PointGeoTag):
            latlng = objects.get_point_coordinates(as_string=True, inverted=True)
            markers = [{'latlng':latlng, 'object': objects}]
        elif isinstance(objects, basestring):
            latlng = objects
            markers = [{'latlng':latlng}]
        elif isinstance(objects, QuerySet) or isinstance(objects, list):
            if len(objects) == 0:
                centroid = (13.0043792701320360, 55.5996869012237553)
            elif not getattr(settings, 'USE_GEOGRAPHY', True):
                centroid = objects.collect().envelope.centroid
                gz = GoogleZoom()
                zoom = gz.get_zoom(objects.unionagg())
            else:
                centroid = objects[0].get_point_coordinates(as_string=False, 
                                                            inverted=True)
            latlng = '%s,%s' % (centroid[0], centroid[1])
            markers = [{'latlng': i.get_point_coordinates(as_string=True, inverted=True),
                        'object': i} for i in objects]
        else:
            raise template.TemplateSyntaxError(
                'The first parameter must be either a PointGeoTag subclass, '
                'a queryset of PointGeoTag subclasses, '
                'a list of PointGeoTag subclases or a LatLong string. '
                'A %s was given' % type(objects))

        if static=="true":
            t = template.loader.get_template('geotagging/staticmap.html')
            return t.render(template.Context({
                        'map_id': id,
                        'width': width,
                        'height': height,
                        'latlng': latlng,
                        'markers': markers,
                        'extra': extra,
                        'zoom': zoom or getattr(settings, 'DEFAULT_ZOOM', 16),
                        }))

        t = template.loader.get_template('geotagging/map.html')
        return t.render(template.Context({
                    'map_id': id,
                    'width': width,
                    'height': height,
                    'latlng': latlng,
                    'markers': markers,
                    'extra': extra,
                    'zoom': zoom or getattr(settings, 'DEFAULT_ZOOM', 16),
                    }))

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
