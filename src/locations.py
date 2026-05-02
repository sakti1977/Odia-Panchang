"""
Location data for major cities in Odisha.
Each location includes coordinates and timezone for accurate sunrise/sunset calculations.
"""

ODISHA_CITIES = {
    "puri": {
        "name": "Puri",
        "name_or": "ପୁରୀ",
        "lat": 19.8135,
        "lon": 85.8312,
        "tz": 5.5,
        "description": "Holy city of Lord Jagannath"
    },
    "bhubaneswar": {
        "name": "Bhubaneswar",
        "name_or": "ଭୁବନେଶ୍ୱର",
        "lat": 20.2961,
        "lon": 85.8245,
        "tz": 5.5,
        "description": "Capital city, Temple city of India"
    },
    "cuttack": {
        "name": "Cuttack",
        "name_or": "କଟକ",
        "lat": 20.5124,
        "lon": 85.8828,
        "tz": 5.5,
        "description": "Silver city, Cultural capital"
    },
    "jajpur": {
        "name": "Jajpur",
        "name_or": "ଯାଜପୁର",
        "lat": 20.8408,
        "lon": 86.3264,
        "tz": 5.5,
        "description": "Home of Maa Biraja Temple"
    },
    "berhampur": {
        "name": "Berhampur",
        "name_or": "ବ୍ରହ୍ମପୁର",
        "lat": 19.3150,
        "lon": 84.7941,
        "tz": 5.5,
        "description": "Silk city of Odisha"
    },
    "sambalpur": {
        "name": "Sambalpur",
        "name_or": "ସମ୍ବଲପୁର",
        "lat": 21.4669,
        "lon": 83.9812,
        "tz": 5.5,
        "description": "Western Odisha cultural hub"
    },
    "rourkela": {
        "name": "Rourkela",
        "name_or": "ରାଉରକେଲା",
        "lat": 22.2604,
        "lon": 84.8536,
        "tz": 5.5,
        "description": "Steel city of Odisha"
    },
    "balasore": {
        "name": "Balasore",
        "name_or": "ବାଲେଶ୍ୱର",
        "lat": 21.4934,
        "lon": 86.9336,
        "tz": 5.5,
        "description": "Northern coastal city"
    },
    "konark": {
        "name": "Konark",
        "name_or": "କୋଣାର୍କ",
        "lat": 19.8876,
        "lon": 86.0945,
        "tz": 5.5,
        "description": "Home of Sun Temple"
    },
    "rayagada": {
        "name": "Rayagada",
        "name_or": "ରାୟଗଡ",
        "lat": 19.1659,
        "lon": 83.4156,
        "tz": 5.5,
        "description": "Southern Odisha district headquarters"
    },
    "kendrapara": {
        "name": "Kendrapara",
        "name_or": "କେନ୍ଦ୍ରାପଡ଼ା",
        "lat": 20.5021,
        "lon": 86.4211,
        "tz": 5.5,
        "description": "Land of rivers and temples"
    },
    "angul": {
        "name": "Angul",
        "name_or": "ଅନୁଗୁଳ",
        "lat": 20.8400,
        "lon": 85.1018,
        "tz": 5.5,
        "description": "Industrial city"
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
