from django.db.models.loading import get_model

from utils import google_TSP
from json_utils import JsonResponse

"""
Notes:

We need views for:
 * Getting display information about a geotagged point.
 * Sorting (TSP)
 * Save queue
"""

def optimize(request):
    """
    Parameters: 
    It could be either:
     * model: a string representing which geotagged model is being
       queried. i.e.: 'attractions.Attraction'
     * ids: a list of comma-separated ids of the waypoints to optimize

    or:
     * locations: a list of |-separated locations to be geocoded and
       optimized. You can also use LatLong pairs.
    """
    model = request.GET.get('model', None)
    if model:
        klass = get_model(*model.split('.'))
        ids = request.GET.get('ids', '').split(',')

        if len(ids) < 3:
            return JsonResponse({
                    'success': False, 
                    'message': 'At least three objects are needed for optimization'})

        #This is not explicitly taking initial and last point into account
        waypoints = klass.objects.filter(pk__in=ids)

        #if we want to take repeated objects into account:
        #object_dict = dict((i.pk, i) for i in klass.objects.filter(pk__in=ids))
        #waypoints = [object_dict[int(i)] for i in ids]
    else:
        waypoints = request.GET.get('locations', None)
        if not waypoints:
            return JsonResponse({'success':False, 'message':'Locations not provided'})

        waypoints = waypoints.split('|')

        if len(waypoints) < 3:
            return JsonResponse({
                    'success': False, 
                    'message': 'At least three objects are needed for optimization'})


    response = google_TSP(waypoints)
    json_response = map(repr, response)

    return JsonResponse({'success':True, 'optimal_order':json_response})
