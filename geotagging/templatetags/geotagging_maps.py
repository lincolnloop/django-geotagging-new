import ttag

from django.db import models
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
    
    objects = ttag.Arg()
    width = ttag.Arg(required=False, keyword=True)
    height = ttag.Arg(required=False, keyword=True)
    zoom = ttag.Arg(required=False, keyword=True)
    static = ttag.Arg(required=False, keyword=True)
    extra = ttag.Arg(required=False, keyword=True)

    def get_zoom(self, objects, static):
        if len(objects) == 0 or static:
            return None
        if (not getattr(settings, 'USE_GEOGRAPHY', True)) and hasattr(objects, 'unionagg'):
            gz = GoogleZoom()
            zoom = gz.get_zoom(objects.unionagg())
            return zoom
        else:
            coords = [i.get_point_coordinates(as_string=False, inverted=True)
                      for i in objects]
            sw = min(i[0] for i in coords), min(i[1] for i in coords)
            ne = max(i[0] for i in coords), max(i[1] for i in coords)

            return {'bounds':True, 'sw':'%s,%s'%sw, 'ne':'%s,%s'%ne}

            #improve zoom calculation for geography case and
            #non-geodjango latlngs
            return None


    def get_centroid_lnglat(self, objects, static):
        if len(objects) == 0 or static:
            return None
        if (not getattr(settings, 'USE_GEOGRAPHY', True)) and hasattr(objects, 'collect'):
            centroid = objects.collect().envelope.centroid
        else:
            #this is not a real geographic calculation, but handles
            #the case of external latlng.  
            #In the future this should be split between geography and
            #non-geodjango latlngs
            coords = [i.get_point_coordinates(as_string=False, inverted=False)
                      for i in objects]
            n_objects = len(objects)
            x_avg = sum(i[0] for i in coords) / n_objects
            y_avg = sum(i[1] for i in coords) / n_objects
            centroid = (x_avg, y_avg)

        return '%s,%s' % (centroid[1], centroid[0])
            

    def render(self, context):
        data = self.resolve(context)
        objects = data.get('objects', None)
        width = data.get('width', None)
        height = data.get('height', None)
        zoom = data.get('zoom', None)
        static = data.get('static', None) == "true"
        extra = data.get('extra', None)

        context['request'].session['geotagging_map_counter'] = (
            context['request'].session.get('geotagging_map_counter', 0) + 1)
        id = context['request'].session['geotagging_map_counter']

        if isinstance(objects, PointGeoTag):
            latlng = objects.get_point_coordinates(as_string=True, inverted=True)
            markers = latlng and [{'latlng':latlng, 'object': objects}] or []
        elif isinstance(objects, models.Model):
            latlng = objects.get_point_coordinates(as_string=True, inverted=True)
            markers = latlng and [{'latlng':latlng}] or []
        elif isinstance(objects, basestring):
            latlng = objects
            markers = [{'latlng':latlng}]
        elif isinstance(objects, QuerySet) or isinstance(objects, list):
            if len(objects) > 0:
                if all([i.__class__==objects[0].__class__ for i in objects]):
                    #check for heterogeneous
                    not_null = (objects[0].__class__.objects.filter(
                            id__in=[i.id for i in objects if i.geotagging_point]))
                else:
                    not_null = objects
            else:
                not_null = []
            latlng = self.get_centroid_lnglat(not_null, static)
            markers = [{'latlng': i.get_point_coordinates(as_string=True, inverted=True),
                        'object': i} for i in not_null if i.geotagging_point]
            zoom = self.get_zoom(not_null, static)
        else:
            raise template.TemplateSyntaxError(
                'The first parameter must be either a PointGeoTag subclass, '
                'a queryset of PointGeoTag subclasses, '
                'a list of PointGeoTag subclases, implement get_point_coordinates '
                'or be a LatLong string. '
                'A %s was given' % type(objects))

        template_name = static and 'geotagging/staticmap.html' or 'geotagging/map.html'

        t = template.loader.get_template(template_name)
        return t.render(template.Context({
                    'map_id': id,
                    'width': width,
                    'height': height,
                    'latlng': latlng,
                    'markers': markers,
                    'extra': extra,
                    'zoom': zoom,
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
