import json
import httplib, urllib
import itertools

from collections import defaultdict
try:
    import numpy as np
    from scikits.learn.cluster import KMeans, AffinityPropagation
except ImportError, e:
    pass

from django.conf import settings

from geotagging.models import PointGeoTag

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

    #if isinstance(waypoints[0], PointGeoTag):
    if not isinstance(waypoints[0], basestring):
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


def cluster_objects(objects, optimize_within_clusters=False):
    """
    Return a list of objects clustered by geographical position.

    :param objects: The list of objects or a queryset. The objects
    must be an instance of PointGeoTag or implement
    `get_point_coordinates(self, as_string=False, inverted=False)` to
    obtain the coordinates

    :param optimize_within_clusters: a boolean specifying if the
    clusters should be ordered based on the (near-)optimal route.

    :returns: A list of clusters. Example: [[<p1>, <p2>], [<p3>, <p4>, <p5>]]
    """
    X = np.array([list(i.get_point_coordinates(as_string=False, inverted=True))
                  for i in objects])

    # Afinity propagation. 
    # This way we can determine the number of clusters automatically
    # X_norms = np.sum(X*X, axis=1)
    # S = - X_norms[:,np.newaxis] - X_norms[np.newaxis,:] + 2 * np.dot(X, X.T)
    # p = 10*np.median(S)
    # af = AffinityPropagation()
    # af.fit(S, p)
    # n_clusters_ = len(af.cluster_centers_indices_)

    n_items = len(X)
    max_items = getattr(settings, 'ITEMS_PER_BUCKET', 10)
    n_clusters = n_items / max_items
    n_clusters += n_items % max_items == 0 and 0 or 1

    # KMeans. 
    # If we want a pre-specified number of clusters this is the way to go 
    km = KMeans(k=n_clusters, init='k-means++')
    km.fit(X)

    cluster_dict = defaultdict(list)
    for i, cluster_id in enumerate(km.labels_):
        cluster_dict[cluster_id].append(objects[i])

    clusters = cluster_dict.values()
    if optimize_within_clusters:
        new_clusters = []
        for cluster in clusters:
            if len(cluster) > 3:
                new_clusters.append(google_TSP(cluster))
            else:
                new_clusters.append(cluster)
        return new_clusters

    return clusters
