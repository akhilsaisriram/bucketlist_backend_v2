import polyline
from feed.models import Feed
from feed.serializers import FeedSerializer
import logging

from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

def get_feeds_near_polyline(polyline_coords, radius):
    """
    Query feeds near a given polyline within a specified radius.

    Args:
        polyline_coords (list of tuples): List of (longitude, latitude) coordinates representing the polyline.
        radius (float): Radius in meters to consider feeds near the polyline.

    Returns:
        QuerySet: Feeds within the specified radius of the polyline.
    """

    # Create a LineString object from the polyline coordinates
    polyline = LineString(polyline_coords, srid=4326)

    # Transform to match the spatial reference system of the database
    polyline = polyline.transform(3857, clone=True)  # Transform to Web Mercator (or your database SRID)

    # Query feeds within the specified radius of the polyline
    feeds = Feed.objects.filter(
        ocord__distance_lte=(polyline, D(m=radius))  # Spatial query
    ).annotate(
        distance=Distance('ocord', polyline)  # Annotate with distance for sorting
    ).order_by('distance')  # Order by proximity to the polyline

    return feeds


logger = logging.getLogger(__name__)
def polylinedata(polylinetext):
     coordinates = polyline.decode(polylinetext)
     logger.info(f"Decoded polyline coordinates: {coordinates}")
     radius = 500  # 500 meters

     feeds = get_feeds_near_polyline(coordinates, radius)
     data=FeedSerializer(feeds,many=True).data
     print(data)
     return data


def near_bucket_people():
     # Define the coordinates of the polyline
     pass