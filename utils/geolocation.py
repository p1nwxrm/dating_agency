import math
from geopy.geocoders import Nominatim

# ---------------------------
# Повертає відстань між двома координатами (Haversine formula)
# ---------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # радіус Землі в км
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ---------------------------
# Повертає назву міста за координатами
# ---------------------------
def get_city(lat, lon, language: str):
    geolocator = Nominatim(user_agent = "rizzem_bot")  # Ініціалізуємо геокодер Nominatim (на базі OpenStreetMap)
    location = geolocator.reverse((lat, lon), language = language)  # Отримуємо адресу за координатами (reverse geocoding)

    city = None
    if location and "address" in location.raw:
        address = location.raw["address"]
        city = address.get("city") or address.get("town") or address.get("village")

    return city