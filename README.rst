==============
 Installation
==============

TODO: complete this after packaging
pip install.. etc, etc...

 * add `geottagging` to settings.INSTALLED_APPS 


=======
 Usage
=======

Models
======

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

    from istorbyen.apps.geotagging import admin
    from istorbyen.apps.attractions.models import Attraction

    admin.site.register(Attraction, admin.GeoTaggedModelAdmin)


    
======
 ToDo
======

 * add tests
