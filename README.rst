============
 Disclaimer
============

This is a WIP and is not to be used in production unless you know what you're doing.

The documentation also outdated. But it shouldn't be for long.

==============
 Requirements
==============

For the clustering:

 * scikit.learn

For the template tags:

 * django-ttags    

==============
 Installation
==============

Via ``pip``::
    
    pip install -e git+git://github.com:lincolnloop/django-geotagging.git#egg=django-geotagging

The old fashioned way:

1. Download repo http://github.com/lincolnloop/django-geotagging-new/tarball/master
2. Unpack and ``cd django_geotagging-new``
3. ``python setup.py install``


Configuration
=============

 * add `geottagging` to settings.INSTALLED_APPS 
 * If you want the maps to be displayed, include the necessary javascript::
   <!-- Map stuff -->
   <script src="{{ STATIC_URL }}js/vendor/underscore.js" type="text/javascript" charset="utf-8"></script>
   <script src="{{ STATIC_URL }}js/vendor/backbone.js" type="text/javascript" charset="utf-8"></script>
   <script src="{{ STATIC_URL }}js/vendor/jquery.tmpl.js" type="text/javascript" charset="utf-8"></script>
   <script src="http://openlayers.org/api/2.10/OpenLayers.js" type="text/javascript"></script>
   <script src="http://maps.google.com/maps?file=api&v=2&key=AIzaSyDfzk8s9rszmBTAJVsZ8aLDdaRVwPyVqc4" type="text/javascript"></script>
   <script src="http://maps.google.com/maps/api/js?sensor=false" type="text/javascript"></script>
   <script src="{{ STATIC_URL }}js/common/global.js" type="text/javascript"></script>
   <script src="{{ STATIC_URL }}js/app/Spot.js" type="text/javascript" charset="utf-8"></script>
   <script src="{{ STATIC_URL }}js/app/MapView.js" type="text/javascript" charset="utf-8"></script>

=======
 Usage
=======

Models
======

To use geotagging in your models you will need to have GeoDjango_
installed in your project.

.. _GeoDjango: http://geodjango.org/



To add geotagging to a model make it inherit from the GeoTag model
that you need to use. Currently the following GeoTagging types are
available::

    PointGeoTag

Example::

    from geottaging.models import PointGeoTag

    class Attraction(PointGeoTag):
        name = models.CharField(max_length=100)

The model should now have a field called `geotagging_point` that
stores the point information. Also, a new manager is added to the
model under `Model.geo_objects` so the geographical queries can be
made.

Example::

    >>> Attraction.objects.all()
    [<Attraction>, ...]
    >>> Attraction.geo_objects.all()
    [<Attraction>, ...]
    >>> Attraction.objects.filter(geotagging_point__intersects=an_area)
    ... error
    >>> Attraction.geo_objects.filter(geotagging_point__intersects=an_area)
    [<Attraction>, ...]

To add alias to the `geotagging_point` field, simply write a property
to access it. This will not allow the new name to be used in
querysets, but it will be available to the object::

    class Attraction(PointGeoTag):
        ...
        def _get_point(self):
            return self.geotagging_point
        location = property(_get_point)

Admin
=====

To add the geotagging to the admin, just use the admin provided at::

    geotagging.admin.GeoTaggedModelAdmin

example::

    from geotagging import admin
    from yourproject.apps.attractions.models import Attraction

    admin.site.register(Attraction, admin.GeoTaggedModelAdmin)

Utils
=====

Route optimization
------------------

The geotagging app provides a view for optimizing routes. The
optimization is done by calls to the google maps directions api.

This view takes a list of waypoints to be routed and returns the
optimal order. 

The list of waypoints can be provided in two ways:

 * A model and a list of ids:         
   In this case, the request will look something like this::
      http://localhost:8000/geotagging/optimize/?model=attractions.Attraction&ids=1,3,2
 * A list of locations separated by `|`:
   The locations can be either names or lat-long objects. The request will look like one of these::
       http://localhost:8000/geotagging/optimize/?locations=lund|kastrup|lomma|malmo|kopenhamn
       http://localhost:8000/geotagging/optimize/?locations=55.71002017356669,13.169603345421381|55.599056501542002,13.008327481804296|55.68450435788013,12.573595044746435

The result is always returned in terms of what was specified in the
request. This means that for the previous three requests the response
would be

1)::

    {
    optimal_order: [
    "<Attraction: My house>"
    "<Attraction: MalmÃ¶>"
    "<Attraction: kÃ¶penhamn>"
    ]
    success: true
    }


2)::

    {
    -optimal_order: [
    "u'lund'"
    "u'lomma'"
    "u'malmo'"
    "u'kastrup'"
    "u'kopenhamn'"
    ]
    success: true
    }
    
and 3)::

    {
    -optimal_order: [
    "u'55.71002017356669,13.169603345421381'"
    "u'55.599056501542002,13.008327481804296'"
    "u'55.68450435788013,12.573595044746435'"
    ]
    success: true
    }


respectively.

======
 ToDo
======

 * Add security for the model case on optimize view (register the
   models that can be queried) (maybe similar to django-filters)
 * Add tests
 * Markers are being added the lazy way. fix that. 
 * document settings.USE_GEOGRAPHY.
   - refer to
     http://docs.djangoproject.com/en/dev/ref/contrib/gis/model-api/#geography
     and http://postgis.refractions.net/documentation/manual-1.5/ch04.html#PostGIS_GeographyVSGeometry
     and http://workshops.opengeo.org/postgis-intro/geography.html
 * document: `objects = PointGeoTag.geo_objects`
 * Figure out how to ship with marker clusterer javascript

Maps
====

Need documentation for the maps feature. Some stuff to remember when documenting:

 * an object can implement `get_title(self) -> string` to assign the title to a marker
 * The first parameter must be either a PointGeoTag subclass, a
   queryset of PointGeoTag subclasses, a list of PointGeoTag subclases
   or a LatLong string.
 * Add the reset context processor to avoid map ids from increasing:
    'django.core.context_processors.request',
    'geotagging.context_processors.map_counter_reset',
 * Document what's available to the template
 * Missing stuff (make markers clickable, avoid markers from overlapping)

Including maps in templates
---------------------------

To start including maps you need to make sure the request and
map_counter_reset context processors are eneabled::

    TEMPLATE_CONTEXT_PROCESSORS += (
        'django.core.context_processors.request',
        'geotagging.context_processors.map_counter_reset',
    )

and that the views use RequestContext.

That should be enough for static maps.

For dynamic maps the views should include the required javascript::

    {% block extra_head %}
    {% geotagging_maps_api %}
    {% endblock %}


Settings
========

DEFAULT_ZOOM


Template
--------

Here's a basic template to include some maps::

    {% extends "base.html" %}
    {% load geotagging_maps %}
        
    {% block content %}
    <p>
    <div id="map">
       <div id="placeholder-map" style="height:400px"></div>
    </div>
    {% endblock %}

    {% block js %} {# at the end of the page #}
        {{ block.super }}
        {% maps_js "map" items_to_be_mapped %}
    {% endblock %}

