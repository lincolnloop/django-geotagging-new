==============
 Installation
==============

TODO: complete this after packaging
pip install.. etc, etc...

Via ``pip``::
    
    pip install -e git+git://github.com:lincolnloop/django-geotagging.git#egg=django-geotagging

The old fashioned way:

1. Download repo http://github.com/lincolnloop/django-geotagging-new/tarball/master
2. Unpack and ``cd django_geotagging-new``
3. ``python setup.py install``


Configuration
=============

 * add `geottagging` to settings.INSTALLED_APPS 

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
