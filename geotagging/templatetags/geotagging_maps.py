import ttag

from django.db import models
from django import template
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib.gis.geos import Point

from geotagging.models import PointGeoTag

register = template.Library()
from olwidget.widgets import InfoMap


class NSInfoMap(InfoMap):
    def render(self, name, value, attrs=None):
        attrs = getattr(self, 'attrs', None)
        return super(NSInfoMap, self).render(name, value, attrs)


def get_display(obj):
    return getattr(obj, 'get_map_display', lambda: '')()

def get_style(obj):
    return getattr(obj, 'get_map_style', lambda: {})()

        
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

        #options
        # no popup
        # static
        
        context['request'].session['geotagging_map_counter'] = (
            context['request'].session.get('geotagging_map_counter', 0) + 1)
        count = context['request'].session['geotagging_map_counter']

        if isinstance(objects, PointGeoTag):
            coords = objects.get_point_coordinates(as_string=True)
            if coords:
                latlng = Point(*map(float,
                                    coords.split(',')))
                markers = latlng and [{'latlng': latlng, 'object': objects,
                                       'display': get_display(objects),
                                       'style': objects.get_map_style()}] or []
            else:
                markers = []
        elif isinstance(objects, models.Model):
            latlng = Point(*map(float,
                                objects.get_point_coordinates(as_string=True).split(',')))
            markers = latlng and [{'latlng': latlng,
                                   'display': get_display(objects),
                                   'style': objects.get_map_style()}] or []
        elif isinstance(objects, basestring):
            latlng = Point(*map(float, objects.split(',')))
            markers = [{'latlng':latlng,
                        'display': get_display(latlng),
                        'style': get_style(latlng)}]
        elif isinstance(objects, QuerySet) or isinstance(objects, list):
            markers = [{'latlng': i.geotagging_point,
                        'object': i,
                        'display': get_display(i),
                        'style': get_style(i)} for i in objects if i.geotagging_point]

        else:
            raise template.TemplateSyntaxError(
                'The first parameter must be either a PointGeoTag subclass, '
                'a queryset of PointGeoTag subclasses, '
                'a list of PointGeoTag subclases, implement get_point_coordinates '
                'or be a LatLong string. '
                'A %s was given' % type(objects))

        controls = not static and ['Navigation', 'PanZoom',] or [] 
        template_name = 'geotagging/map.html'
            
        show_map = bool(markers)
        for marker in markers:
            marker['latlng'].srid = 4326

        mappable = [
            [i['latlng'], {'html': i['display'],
                           'style': i['style']}] for i in markers
        ]
        options = {
            'layers': ['google.streets'],
            'cluster': True,
            'cluster_display': 'list',
            'map_div_style': {'width': '%spx'%width, 'height': '%spx'%height},
            'map_options' : {
                'controls': controls,
            }
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
 * different markers
 * docs
"""
