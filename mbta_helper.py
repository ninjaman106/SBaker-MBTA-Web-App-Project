import os
import json
import urllib.request

from dotenv import load_dotenv
from urllib import request, parse
# Load environment variables
load_dotenv()

# Get API keys from environment variables
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

# Optional: helpful error messages if keys are missing
if MAPBOX_TOKEN is None:
    raise RuntimeError("MAPBOX_TOKEN is not set. Check your .env file.")
if MBTA_API_KEY is None:
    raise RuntimeError("MBTA_API_KEY is not set. Check your .env file.")

def build_mbta_url(latitude: str, longitude: str) -> str:
    """
    Take latitude and longitude and build a URL for MBTA /stops endpoint
    sorted by distance.
    """
    params = {
        "api_key": MBTA_API_KEY,
        "sort": "distance",
        "filter[latitude]": latitude,
        "filter[longitude]": longitude,
    }
    query_string = parse.urlencode(params)
    return f"{MBTA_BASE_URL}?{query_string}"


# Useful base URLs (you need to add the appropriate parameters for each API request)
MAPBOX_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/forward"
MBTA_BASE_URL = "https://api-v3.mbta.com/"


# A little bit of scaffolding if you want to use it
def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request."""
    with request.urlopen(url) as resp:
        response_text = resp.read().decode("utf-8")
    return json.loads(response_text)

def build_mapbox_url(place_name: str) -> str:
    """
    Take an address or place name and return a properly encoded
    Mapbox forward-geocoding URL.
    """
    params = {
        "api_key": MBTA_API_KEY,
        "sort": "distance",
        "filter[latitude]": latitude,
        "filter[longitude]": longitude,
    }
    query_string = parse.urlencode(params)
    return f"{MAPBOX_BASE_URL}?{query_string}"


def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/search-box/#search-request for Mapbox Search API URL formatting requirements.
    """
    url = build_mapbox_url(place_name)
    data = get_json(url)

    # Navigate through the JSON: features[0].geometry.coordinates = [lng, lat]
    features = data.get("features", [])
    if not features:
        raise ValueError(f"No results found for {place_name!r}")

    first = features[0]
    # Mapbox Searchbox often nests coordinates under geometry or properties
    # Adapt this if your actual JSON looks slightly different.
    coords = first.get("geometry", {}).get("coordinates")
    if not coords or len(coords) < 2:
        raise ValueError("Could not find coordinates in response")

    lng, lat = coords[0], coords[1]
    return str(lat), str(lng)


def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates. wheelchair_accessible is True if the stop is marked as accessible, False otherwise.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    url = build_mbta_url(latitude, longitude)
    data = get_json(url)

    stops = data.get("data", [])
    if not stops:
        raise ValueError("No nearby MBTA stops found.")

    first = stops[0]
    attrs = first.get("attributes", {})
    name = attrs.get("name", "Unknown station")

    wheelchair_code = attrs.get("wheelchair_boarding")
    # MBTA docs: 0 = no info, 1 = accessible, 2 = inaccessible
    is_accessible = (wheelchair_code == 1)

    return name, is_accessible


def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    lat, lng = get_lat_lng(place_name)
    station_name, is_accessible = get_nearest_station(lat, lng)
    return station_name, is_accessible


def main():
    """
    You should test all the above functions here
    """
    pass


if __name__ == "__main__":
    main()
    print(get_lat_lng("Boston Common"))
    print(find_stop_near("Boston Common"))
