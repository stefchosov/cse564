# utils.py

import requests
from geopy.geocoders import Nominatim

##this method returns geoid to find walkdata for
##pass in street, city and state as string

def get_block_group_geoid(street, city, state):
    # Construct the full address internally
    address = f"{street}, {city}, {state}"

    geolocator = Nominatim(user_agent="walkdata sarsov@wisc.edu")
    location = geolocator.geocode(address)

    if not location:
        raise ValueError("Failed to geocode address.")

    lat, lon = location.latitude, location.longitude

    url = (
        f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        f"?x={lon}&y={lat}&benchmark=Public_AR_Current&vintage=Current_Current&format=json"
    )

    resp = requests.get(url).json()

    try:
        block_info = resp['result']['geographies']['2020 Census Blocks'][0]
        block_geoid = block_info['GEOID']
        block_group_geoid = block_geoid[:-3]  # Truncate to 12-digit block group
        return block_group_geoid
    except (KeyError, IndexError):
        raise ValueError("Census block not found for the given location.")

