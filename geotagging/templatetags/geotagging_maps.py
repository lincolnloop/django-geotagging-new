from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag
from django import template
from django.template.loader import render_to_string

register = template.Library()

# class Javascript(InclusionTag):
#     name = 'include_maps_js'
#     template = 'geotagging/map_scripts.html'

# register.tag(Javascript)


class Map(InclusionTag):
    name = 'maps'
    template = 'geotagging/map.html'
    # options = Options(
    #     Argument('id'),
    #     Argument('latlng', default='55.6845043579,12.5735950447'),
    #     Argument('width', default='300'),
    #     Argument('height', default='400'),
    #     Argument('zoom', default='16')
    # )

    def get_context(self, *args):
        import ipdb; ipdb.set_trace()
        return {'title':'a map',
                'map_id': id,
                'width': width,
                'height': height,
                'LatLng': latlng,
                #'LatLng':'55.6845043579,12.5735950447',
                'zoom': zoom,
                }
        
register.tag(Map)


"""
Based on easy_maps: https://bitbucket.org/kmike/django-easy-maps/overview
"""

@register.tag
def geotagging_map2(parser, token):
    """
    The syntax:
        {% geotagging_map <address> [<width> <height>] [<zoom>] [using <template_name>] %}
    """
    width, height, zoom, template_name = None, None, None, None
    params = token.split_contents()

    # pop the template name
    if params[-2] == 'using':
        template_name = params[-1]
        params = params[:-2]

    if len(params) < 2:
        raise template.TemplateSyntaxError('geotagging_map tag requires address argument')

    address = params[1]

    if len(params) == 4:
        width, height = params[2], params[3]
    elif len(params) == 5:
        width, height, zoom = params[2], params[3], params[4]
    elif len(params) == 3 or len(params) > 5:
        raise template.TemplateSyntaxError('geotagging_map tag has the following syntax: '
                   '{% geotagging_map <address> <width> <height> [zoom] [using <template_name>] %}')
    return GeotaggingMapNode(address, width, height, zoom, template_name)

class GeotaggingMapNode(template.Node):
    def __init__(self, address, width, height, zoom, template_name):
        self.address = template.Variable(address)
        self.width = width or ''
        self.height = height or ''
        self.zoom = zoom or 16
        self.template_name = template.Variable(template_name or '"geotagging/map.html"')

    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            context.update({
                    'title':'a map',
                    'map_id': '1',
                    'width': self.width,
                    'height': self.height,
                    'LatLng':'55.6845043579,12.5735950447',
                    #'LatLng':'55.6845043579,12.5735950447',
                    'zoom': self.zoom,
                    'template_name': self.template_name
                    })
            return render_to_string(template_name, context_instance=context)
        except template.VariableDoesNotExist:
            return ''

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
