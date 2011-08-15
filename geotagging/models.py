"""
This app should eventually be stripped off from the project and be
packaged as a reusable app.
"""

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.db import connection
from django.conf import settings

HAS_GEOGRAPHY = False
try:
    # You need Django 1.2 and PostGIS > 1.5
    # http://code.djangoproject.com/wiki/GeoDjango1.2#PostGISGeographySupport 
    if connection.ops.geography:
        HAS_GEOGRAPHY = True
except AttributeError:
    pass
    
def field_kwargs(verbose_name):
    """
    Build kwargs for field based on the availability of geography fields
    """
    kwargs = {
        'blank': True,
        'null': True,
        'verbose_name': _(verbose_name),
    }
    if HAS_GEOGRAPHY and getattr(settings, 'USE_GEOGRAPHY', True):
        kwargs['geography'] = True
    return kwargs

class GeoTag(models.Model):
    objects = models.Manager()
    geo_objects = models.GeoManager()

    class Meta:
        abstract = True

class PointGeoTag(GeoTag):
    geotagging_point = models.PointField(**field_kwargs('point'))

    def get_point_coordinates(self, as_string=False, inverted=False):
        if not self.geotagging_point:
            return None
        if inverted:
            xy = (self.geotagging_point.y, self.geotagging_point.x)
        else:
            xy = (self.geotagging_point.x, self.geotagging_point.y)
        if as_string:
            return '%s,%s' % xy
        return xy

    def get_map_display(self):
        return unicode(self)

    def get_marker_image(self):
        raise NotImplementedError('Implement get_marker_image to change '
                                  'the default marker')

    def get_map_style(self):
        style = {}
        try:
            style['external_graphic'] = self.get_marker_image()
        except:
            pass
        return style
        
    class Meta:
        abstract = True
