import json
import httplib, urllib
import itertools

from django.db import models

class GoogleApiException(Exception):
    error_map = {'NOT_FOUND': "indicates at least one of the locations specified in the requests's origin, destination, or waypoints could not be geocoded.",
                 'ZERO_RESULTS': "indicates no route could be found between the origin and destination.",
                 'MAX_WAYPOINTS_EXCEEDED': "indicates that too many waypointss were provided in the request The maximum allowed waypoints is 8, plus the origin, and destination. ( Google Maps Premier customers may contain requests with up to 23 waypoints.)",
                 'INVALID_REQUEST': "indicates that the provided request was invalid.",
                 'OVER_QUERY_LIMIT': "indicates the service has received too many requests from your application within the allowed time period.",
                 'REQUEST_DENIED': "indicates that the service denied use of the directions service by your application.",
                 'UNKNOWN_ERROR': "indicates a directions request could not be processed due to a server error. The request may succeed if you try again."
                 }
    def __init__(self, response):
        self.response = response
    def __str__(self):
        status = self.response.get('status', None)
        detail = self.error_map.get(status, False)
        if detail:
            return '%s. %s' % (status, detail)
        return repr(self.response)

def google_TSP_call(waypoints):
    """
    This is the function that does the calling. It expects the
    number of waypoints to always be within the allowed range.
    """
    origin = w_origin = waypoints.pop(0)
    destination = w_destination = waypoints.pop()
    coordinates = waypoints

    if isinstance(waypoints[0].__class__, models.base.ModelBase):
        coordinates = [i.get_point_coordinates(as_string=True, inverted=True) 
                       for i in waypoints]

        origin = w_origin.get_point_coordinates(as_string=True, inverted=True)
        destination = w_destination.get_point_coordinates(as_string=True, inverted=True)

    conn = httplib.HTTPConnection("maps.googleapis.com")
    params = urllib.urlencode({'origin':origin, 'destination':destination, 
                               'waypoints':'|'.join(['optimize:true']+coordinates), 
                               'sensor':'false'})
    conn.request("GET", '/maps/api/directions/json?%s' % params)
    response = conn.getresponse()

    routes = json.loads(response.read())

    if routes['status'] != 'OK':
        raise GoogleApiException(routes)

    sorted_points = ([w_origin] + 
                     [waypoints[i] for i in routes['routes'][0]['waypoint_order']] + 
                     [w_destination])

    return sorted_points

def split_num(k, l):
    nk=k
    while l%nk<2:
        nk-=1
    return nk

def google_TSP(waypoints=[], max_waypoints=8):
    """
    Queries google for a the optimal order in which the points should
    be visited.
    """
    n = len(waypoints)
    if n>max_waypoints+2:
        #use some sort of heuristic to order and split
        #for now the heuristic is: no heuristic
        k = split_num(max_waypoints+2, n)
        waypoint_iter = itertools.izip_longest(*[iter(waypoints)]*k)
    else:
        waypoint_iter = [waypoints]

    return list(itertools.chain.from_iterable(
            [google_TSP_call([i for i in waypoints if i]) 
             for waypoints in waypoint_iter]))

