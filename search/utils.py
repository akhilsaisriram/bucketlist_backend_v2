from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Q

def get_objects_within_radius(model, serializer, lat, lng, radius_km=10, coord_fields=['ocord', 'dcord']):
    """
    Utility to fetch and serialize objects of a model within a specified radius.
    Args:
        model: The model to query.
        serializer: Serializer for the model.
        lat: Latitude of the location.
        lng: Longitude of the location.
        radius_km: Radius in kilometers.
        coord_fields: List of coordinate fields to check distance against.
    Returns:
        Serialized data of objects within the radius.
    """
    try:
        user_location = Point(lat, lng, srid=4326)  # Create Point (lng, lat)
    except ValueError:
        raise ValueError("Invalid latitude or longitude format.")

    # Build a Q object for filtering based on multiple coordinate fields
    query = Q()
    for field in coord_fields:
        query |= Q(**{f"{field}__distance_lte": (user_location, Distance(km=radius_km))})

    # Fetch objects and serialize
    objects = model.objects.filter(query)
    return serializer(objects, many=True).data
