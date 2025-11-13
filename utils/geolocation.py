from math import radians, sin, cos, sqrt, atan2
from models.models import ParkingLot

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two GPS coordinates using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert coordinates to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)

def find_nearby_lots(user_lat, user_lon, radius_km=10):
    """
    Find parking lots within a specified radius from user's location.
    
    Args:
        user_lat: User's latitude
        user_lon: User's longitude
        radius_km: Search radius in kilometers (default: 10km)
    
    Returns:
        List of parking lots with distances
    """
    all_lots = ParkingLot.query.all()
    nearby_lots = []
    
    for lot in all_lots:
        if lot.latitude and lot.longitude:
            distance = calculate_distance(user_lat, user_lon, lot.latitude, lot.longitude)
            if distance <= radius_km:
                nearby_lots.append({
                    'lot': lot,
                    'distance': distance
                })
    
    return nearby_lots

def sort_by_proximity(lots_with_distance):
    """
    Sort parking lots by distance from user.
    
    Args:
        lots_with_distance: List of dictionaries containing 'lot' and 'distance'
    
    Returns:
        Sorted list by distance (nearest first)
    """
    return sorted(lots_with_distance, key=lambda x: x['distance'])
