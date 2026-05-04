"""
Location data for major cities in India and internationally.
Each location includes coordinates and timezone for accurate sunrise/sunset calculations.
"""

ODISHA_CITIES = {
    # Odisha
    "bhubaneswar": {
        "name": "Bhubaneswar",
        "name_or": "ଭୁବନେଶ୍ୱର",
        "lat": 20.2961,
        "lon": 85.8245,
        "tz": 5.5,
        "description": "Capital of Odisha, Temple city of India"
    },

    # Major Indian Metro Cities
    "delhi": {
        "name": "Delhi",
        "name_or": "ଦିଲ୍ଲୀ",
        "lat": 28.7041,
        "lon": 77.1025,
        "tz": 5.5,
        "description": "Capital of India"
    },
    "mumbai": {
        "name": "Mumbai",
        "name_or": "ମୁମ୍ବାଇ",
        "lat": 19.0760,
        "lon": 72.8777,
        "tz": 5.5,
        "description": "Financial capital of India"
    },
    "kolkata": {
        "name": "Kolkata",
        "name_or": "କୋଲକାତା",
        "lat": 22.5726,
        "lon": 88.3639,
        "tz": 5.5,
        "description": "City of Joy"
    },
    "chennai": {
        "name": "Chennai",
        "name_or": "ଚେନ୍ନାଇ",
        "lat": 13.0827,
        "lon": 80.2707,
        "tz": 5.5,
        "description": "Gateway to South India"
    },
    "bangalore": {
        "name": "Bangalore",
        "name_or": "ବାଙ୍ଗାଲୋର",
        "lat": 12.9716,
        "lon": 77.5946,
        "tz": 5.5,
        "description": "Silicon Valley of India"
    },
    "hyderabad": {
        "name": "Hyderabad",
        "name_or": "ହାଇଦରାବାଦ",
        "lat": 17.3850,
        "lon": 78.4867,
        "tz": 5.5,
        "description": "City of Pearls"
    },
    "pune": {
        "name": "Pune",
        "name_or": "ପୁଣେ",
        "lat": 18.5204,
        "lon": 73.8567,
        "tz": 5.5,
        "description": "Oxford of the East"
    },
    "ahmedabad": {
        "name": "Ahmedabad",
        "name_or": "ଅହମଦାବାଦ",
        "lat": 23.0225,
        "lon": 72.5714,
        "tz": 5.5,
        "description": "Heritage city of Gujarat"
    },
    "jaipur": {
        "name": "Jaipur",
        "name_or": "ଜୟପୁର",
        "lat": 26.9124,
        "lon": 75.7873,
        "tz": 5.5,
        "description": "Pink City of India"
    },
    "lucknow": {
        "name": "Lucknow",
        "name_or": "ଲକ୍ଷ୍ନୌ",
        "lat": 26.8467,
        "lon": 80.9462,
        "tz": 5.5,
        "description": "City of Nawabs"
    },

    # International Cities
    "london": {
        "name": "London",
        "name_or": "ଲଣ୍ଡନ",
        "lat": 51.5074,
        "lon": -0.1278,
        "tz": 0.0,
        "description": "United Kingdom"
    },
    "new_york": {
        "name": "New York",
        "name_or": "ନ୍ୟୁୟର୍କ",
        "lat": 40.7128,
        "lon": -74.0060,
        "tz": -5.0,
        "description": "United States"
    },
    "dubai": {
        "name": "Dubai",
        "name_or": "ଦୁବାଇ",
        "lat": 25.2048,
        "lon": 55.2708,
        "tz": 4.0,
        "description": "United Arab Emirates"
    },
    "singapore": {
        "name": "Singapore",
        "name_or": "ସିଙ୍ଗାପୁର",
        "lat": 1.3521,
        "lon": 103.8198,
        "tz": 8.0,
        "description": "Singapore"
    },
    "sydney": {
        "name": "Sydney",
        "name_or": "ସିଡନୀ",
        "lat": -33.8688,
        "lon": 151.2093,
        "tz": 10.0,
        "description": "Australia"
    },
    "toronto": {
        "name": "Toronto",
        "name_or": "ଟରଣ୍ଟୋ",
        "lat": 43.6532,
        "lon": -79.3832,
        "tz": -5.0,
        "description": "Canada"
    }
}


def get_city_info(city_key: str) -> dict:
    """
    Get location information for a city.
    Returns None if city not found.
    """
    return ODISHA_CITIES.get(city_key.lower())


def list_all_cities() -> list:
    """
    Return list of all available cities with their info.
    """
    return [
        {
            "key": key,
            **info
        }
        for key, info in ODISHA_CITIES.items()
    ]


def detect_city_from_ip(ip_address: str) -> str:
    """
    Detect the nearest city based on IP address geolocation.
    Falls back to Bhubaneswar if detection fails.

    For simplicity, this uses a basic approach with httpx to call a free geolocation API.
    In production, you might want to use a local GeoIP database for better performance.
    """
    import httpx
    import math

    if not ip_address or ip_address == "127.0.0.1" or ip_address.startswith("192.168."):
        return "bhubaneswar"

    try:
        # Use ip-api.com free tier (no authentication required)
        response = httpx.get(f"http://ip-api.com/json/{ip_address}", timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                user_lat = data.get("lat")
                user_lon = data.get("lon")

                if user_lat is not None and user_lon is not None:
                    # Find nearest city using simple distance calculation
                    nearest_city = "bhubaneswar"
                    min_distance = float('inf')

                    for city_key, city_info in ODISHA_CITIES.items():
                        # Haversine distance approximation
                        lat_diff = user_lat - city_info["lat"]
                        lon_diff = user_lon - city_info["lon"]
                        distance = math.sqrt(lat_diff**2 + lon_diff**2)

                        if distance < min_distance:
                            min_distance = distance
                            nearest_city = city_key

                    return nearest_city
    except Exception as e:
        print(f"[Geolocation] Failed to detect location from IP {ip_address}: {e}")

    # Default fallback
    return "bhubaneswar"
