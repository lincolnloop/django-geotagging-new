# from classytags.core import Options
# from classytags.arguments import Argument
# from classytags.helpers import InclusionTag
from django import template
from django.template.loader import render_to_string

register = template.Library()

# class Javascript(InclusionTag):
#     name = 'include_maps_js'
#     template = 'geotagging/map_scripts.html'

# register.tag(Javascript)


"""
Based on easy_maps: https://bitbucket.org/kmike/django-easy-maps/overview
"""

@register.tag
def geotagging_map(parser, token):
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
            address = self.address.resolve(context)
            template_name = self.template_name.resolve(context)

            context.update({
                    'title':'a map',
                    'map_id': '1',
                    'width': '300',
                    'height': '400',
                    'lat':'56.841071',
                    'long':'60.650832',
                    'zoom': self.zoom,
                    'template_name': self.template_name
                    })
            # map, _ = Address.objects.get_or_create(address=address or '')
            # context.update({
            #     'map': map,
            #     'width': self.width,
            #     'height': self.height,
            #     'zoom': self.zoom,
            #     'template_name': template_name
            # })
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
