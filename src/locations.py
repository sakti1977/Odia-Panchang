"""
Location data for Odisha peetha cities, major Indian cities, and international hubs.
Each location includes coordinates and timezone for sunrise/sunset.

Tradition defaults (spec.md):
  jagannath → puri
  biraja    → jajpur
  common    → bhubaneswar
"""

# Tradition → default city key (used by API resolver)
TRADITION_DEFAULT_CITY = {
    "jagannath": "puri",
    "biraja": "jajpur",
    "common": "bhubaneswar",
    "all": "bhubaneswar",
    "lingaraj": "bhubaneswar",
}

ODISHA_CITIES = {
    # ── Odisha (peetha + major) ───────────────────────────────────────────
    "bhubaneswar": {
        "name": "Bhubaneswar",
        "name_or": "ଭୁବନେଶ୍ୱର",
        "lat": 20.2961,
        "lon": 85.8245,
        "tz": 5.5,
        "description": "Capital of Odisha; Lingaraj / Ekamra",
        "region": "odisha",
    },
    "puri": {
        "name": "Puri",
        "name_or": "ପୁରୀ",
        "lat": 19.8135,
        "lon": 85.8312,
        "tz": 5.5,
        "description": "Sri Jagannath Dham; coastal panji heartland",
        "region": "odisha",
    },
    "jajpur": {
        "name": "Jajpur",
        "name_or": "ଯାଜପୁର",
        "lat": 20.8480,
        "lon": 86.3350,
        "tz": 5.5,
        "description": "Maa Biraja peetha; north Odisha panji heartland",
        "region": "odisha",
    },
    "cuttack": {
        "name": "Cuttack",
        "name_or": "କଟକ",
        "lat": 20.4625,
        "lon": 85.8830,
        "tz": 5.5,
        "description": "Millennium City; cultural capital of Odisha",
        "region": "odisha",
    },
    "berhampur": {
        "name": "Berhampur",
        "name_or": "ବ୍ରହ୍ମପୁର",
        "lat": 19.3149,
        "lon": 84.7941,
        "tz": 5.5,
        "description": "Silk city of southern Odisha",
        "region": "odisha",
    },
    "sambalpur": {
        "name": "Sambalpur",
        "name_or": "ସମ୍ବଲପୁର",
        "lat": 21.4669,
        "lon": 83.9756,
        "tz": 5.5,
        "description": "Western Odisha; Samaleswari / Nuakhai region",
        "region": "odisha",
    },
    "rourkela": {
        "name": "Rourkela",
        "name_or": "ରାଉରକେଲା",
        "lat": 22.2604,
        "lon": 84.8536,
        "tz": 5.5,
        "description": "Steel city of northern Odisha",
        "region": "odisha",
    },
    "balasore": {
        "name": "Balasore",
        "name_or": "ବାଲେଶ୍ୱର",
        "lat": 21.4942,
        "lon": 86.9336,
        "tz": 5.5,
        "description": "Northern coastal Odisha",
        "region": "odisha",
    },
    "konark": {
        "name": "Konark",
        "name_or": "କୋଣାର୍କ",
        "lat": 19.8876,
        "lon": 86.0945,
        "tz": 5.5,
        "description": "Sun Temple; coastal pilgrimage",
        "region": "odisha",
    },
    "baripada": {
        "name": "Baripada",
        "name_or": "ବାରିପଦା",
        "lat": 21.9347,
        "lon": 86.7337,
        "tz": 5.5,
        "description": "Mayurbhanj; Rath Yatra tradition of Baripada",
        "region": "odisha",
    },
    "bhadrak": {
        "name": "Bhadrak",
        "name_or": "ଭଦ୍ରକ",
        "lat": 21.0583,
        "lon": 86.4958,
        "tz": 5.5,
        "description": "North Odisha; Biraja panji region",
        "region": "odisha",
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


def get_city_info(city_key: str) -> dict | None:
    """
    Get location information for a city.
    Returns None if city not found.
    """
    if not city_key:
        return None
    info = ODISHA_CITIES.get(city_key.lower())
    if not info:
        return None
    return {"key": city_key.lower(), **info}


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


def resolve_city(
    city: str | None = None,
    tradition: str | None = None,
) -> dict:
    """
    Resolve place for a request.

    Priority:
      1. Explicit city key if valid
      2. Tradition default city (spec.md)
      3. Bhubaneswar

    Raises ValueError for unknown city / tradition when provided.
    """
    trad = (tradition or "common").lower().strip()
    if tradition is not None and trad not in TRADITION_DEFAULT_CITY:
        raise ValueError(
            f"Unknown tradition '{tradition}'. "
            f"Use one of: {', '.join(sorted(TRADITION_DEFAULT_CITY))}."
        )

    if city:
        info = get_city_info(city)
        if not info:
            raise ValueError(
                f"Unknown city '{city}'. Use /api/cities for valid keys."
            )
        return info

    key = TRADITION_DEFAULT_CITY.get(trad, "bhubaneswar")
    info = get_city_info(key)
    assert info is not None
    return info


def detect_city_from_ip(ip_address: str) -> str:
    """
    Detect the nearest *Odisha* city based on IP geolocation.
    Falls back to Bhubaneswar if detection fails, private IP, or far outside Odisha.

    Uses HTTPS geolocation (ipapi.co). Only compares against ODISHA_CITIES keys
    (no London/NY “nearest hub” surprise for global IPs — those still fall back
    if distance is huge).
    """
    import httpx
    import math

    if (
        not ip_address
        or ip_address in ("127.0.0.1", "::1")
        or ip_address.startswith("192.168.")
        or ip_address.startswith("10.")
    ):
        return "bhubaneswar"

    try:
        # HTTPS-only free lookup (no client IP stored server-side by us)
        response = httpx.get(f"https://ipapi.co/{ip_address}/json/", timeout=2.5)
        if response.status_code != 200:
            return "bhubaneswar"
        data = response.json()
        if data.get("error"):
            return "bhubaneswar"
        user_lat = data.get("latitude")
        user_lon = data.get("longitude")
        if user_lat is None or user_lon is None:
            return "bhubaneswar"

        # Odisha approx bbox — outside → Bhubaneswar (do not pick global outliers)
        if not (17.5 <= float(user_lat) <= 22.6 and 81.3 <= float(user_lon) <= 87.6):
            return "bhubaneswar"

        nearest_city = "bhubaneswar"
        min_distance = float("inf")
        for city_key, city_info in ODISHA_CITIES.items():
            lat_diff = float(user_lat) - city_info["lat"]
            lon_diff = float(user_lon) - city_info["lon"]
            distance = math.sqrt(lat_diff**2 + lon_diff**2)
            if distance < min_distance:
                min_distance = distance
                nearest_city = city_key
        return nearest_city
    except Exception as e:
        print(f"[Geolocation] Failed IP lookup (falling back to bhubaneswar): {e}")

    return "bhubaneswar"
