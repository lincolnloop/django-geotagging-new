import ttag

from django.db import models
from django import template
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib.gis.geos import Point

from geotagging.models import PointGeoTag

register = template.Library()
from olwidget.widgets import InfoMap


class Javascript(ttag.Tag):

    class Meta:
        block = False
        name = 'geotagging_maps_api'

    def render(self, context):
        t = template.loader.get_template('geotagging/map_scripts.html')
        return t.render(template.Context({}))

register.tag(Javascript)

class NSInfoMap(InfoMap):
    def render(self, name, value, attrs=None):
        attrs = getattr(self, 'attrs', None)
        return super(NSInfoMap, self).render(name, value, attrs)


class MapObjects(ttag.Tag):
    class Meta:
        name = 'geotagging_map'
    
    objects = ttag.Arg()
    width = ttag.Arg(required=False, keyword=True)
    height = ttag.Arg(required=False, keyword=True)
    zoom = ttag.Arg(required=False, keyword=True)
    static = ttag.Arg(required=False, keyword=True)
    extra = ttag.Arg(required=False, keyword=True)
            
    def render(self, context):
        data = self.resolve(context)
        objects = data.get('objects', None)
        width = data.get('width', None)
        height = data.get('height', None)
        # zoom = data.get('zoom', None)
        static = data.get('static', None) == "true"
        # extra = data.get('extra', None)
        
        context['request'].session['geotagging_map_counter'] = (
            context['request'].session.get('geotagging_map_counter', 0) + 1)
        count = context['request'].session['geotagging_map_counter']

        if isinstance(objects, PointGeoTag):
            latlng = Point(*map(float,
                                objects.get_point_coordinates(as_string=True).split(',')))
            markers = latlng and [{'latlng':latlng, 'object': objects}] or []
        elif isinstance(objects, models.Model):
            latlng = Point(*map(float,
                                objects.get_point_coordinates(as_string=True).split(',')))
            markers = latlng and [{'latlng':latlng}] or []
        elif isinstance(objects, basestring):
            latlng = Point(*map(float, objects.split(',')))
            markers = [{'latlng':latlng}]
        elif isinstance(objects, QuerySet) or isinstance(objects, list):
            markers = [{'latlng': i.geotagging_point,
                        'object': i} for i in objects if i.geotagging_point]

        else:
            raise template.TemplateSyntaxError(
                'The first parameter must be either a PointGeoTag subclass, '
                'a queryset of PointGeoTag subclasses, '
                'a list of PointGeoTag subclases, implement get_point_coordinates '
                'or be a LatLong string. '
                'A %s was given' % type(objects))

        template_name = static and 'geotagging/staticmap.html' or 'geotagging/map.html'

        show_map = bool(markers)
        for marker in markers:
            marker['latlng'].srid = 4326

            # {'html':i['display'],
            #  'style':i['style']}

        mappable = [
            [i['latlng'], ""] for i in markers
        ]
        
        options = {
            'layers': ['google.streets'],
            'cluster': True,
            'cluster_display': 'list',
            'map_div_style': {'width': '%spx'%width, 'height': '%spx'%height},
        }

        olmap = NSInfoMap(mappable, options)
        olmap.attrs = {'id': count}
        t = template.loader.get_template(template_name)
        return t.render(template.Context({'olmap':olmap, 'map_count':count,
                                          'show_map':show_map}))

register.tag(MapObjects)


"""
To-Do:
 * static
 * docs
 * integrate styling (custom marker colors, etc)


"""
