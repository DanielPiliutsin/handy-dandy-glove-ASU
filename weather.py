#!/usr/bin/env python3
"""
weather_speak_ip_geo_fallbacks.py

Flow:
- get public IP
- try geolocation providers in order: ipwhois.app -> ip-api.com -> DbIpCity (optional)
- call Open-Meteo for current weather in Fahrenheit
- build speakable message and speak with espeak

This script intentionally avoids Nominatim/OpenStreetMap.
"""

import json
import subprocess
import sys
from typing import Optional, Tuple

import requests

# Optional fallback import (only used if ipwhois/ip-api fail)
try:
    from ip2geotools.databases.noncommercial import DbIpCity
    HAVE_DBIPCITY = True
except Exception:
    HAVE_DBIPCITY = False


def get_public_ip() -> str:
    r = requests.get("https://api64.ipify.org?format=json", timeout=6)
    r.raise_for_status()
    return r.json()["ip"]


def geolocate_ipwhois(ip: str) -> Optional[Tuple[float, float]]:
    """
    Try ipwhois.app (HTTPS).
    Example: https://ipwhois.app/json/8.8.8.8
    Returns (lat, lon) or None
    """
    url = f"https://ipwhois.app/json/{ip}"
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        data = r.json()
        # ipwhois returns keys "latitude" and "longitude"
        lat = data.get("latitude")
        lon = data.get("longitude")
        if lat is None or lon is None:
            print("ipwhois.app returned no coordinates.", file=sys.stderr)
            return None
        return float(lat), float(lon)
    except requests.HTTPError as e:
        print("ipwhois.app HTTP error:", e, file=sys.stderr)
    except Exception as e:
        print("ipwhois.app failed:", e, file=sys.stderr)
    return None


def geolocate_ipapi_com(ip: str) -> Optional[Tuple[float, float]]:
    """
    Try ip-api.com (HTTP/HTTPS). ip-api returns {"lat": ..., "lon": ...}
    Note: public free endpoint has rate limits but is usually generous.
    """
    # ip-api supports both http and https for json: https://ip-api.com/docs/api:json
    url = f"http://ip-api.com/json/{ip}?fields=status,message,lat,lon"
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            print("ip-api.com failure:", data.get("message"), file=sys.stderr)
            return None
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)
    except requests.HTTPError as e:
        print("ip-api.com HTTP error:", e, file=sys.stderr)
    except Exception as e:
        print("ip-api.com failed:", e, file=sys.stderr)
    return None


def geolocate_dbipcity(ip: str) -> Optional[Tuple[float, float]]:
    """Fallback to ip2geotools.DbIpCity if installed"""
    if not HAVE_DBIPCITY:
        print("DbIpCity not installed; skip.", file=sys.stderr)
        return None
    try:
        res = DbIpCity.get(ip, api_key="free")
        lat = res.latitude
        lon = res.longitude
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)
    except Exception as e:
        print("DbIpCity lookup failed:", e, file=sys.stderr)
        return None


def get_coords_for_ip(ip: str) -> Optional[Tuple[float, float]]:
    print("Trying ipwhois.app...")
    coords = geolocate_ipwhois(ip)
    if coords:
        print("ipwhois.app ->", coords)
        return coords

    print("Trying ip-api.com...")
    coords = geolocate_ipapi_com(ip)
    if coords:
        print("ip-api.com ->", coords)
        return coords

    print("Falling back to DbIpCity (if available)...")
    coords = geolocate_dbipcity(ip)
    if coords:
        print("DbIpCity ->", coords)
        return coords

    return None


def fetch_open_meteo(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "temperature_unit": "fahrenheit",
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def build_message(weather_json: dict) -> str:
    cur = weather_json.get("current_weather") or {}
    temp = cur.get("temperature")
    wind = cur.get("windspeed")
    wind_dir = cur.get("winddirection")
    parts = []
    if temp is not None:
        parts.append(f"The temperature outside is {temp:.1f} degrees Fahrenheit")
    if wind is not None:
        parts.append(f"with a wind speed of {wind:.1f} kilometers per hour")
        if wind_dir is not None:
            parts[-1] = parts[-1] + f", from {int(wind_dir)} degrees"
    if not parts:
        return "I couldn't retrieve the current weather details."
    return ". ".join(parts) + "."


def speak_espeak(text: str) -> None:
    subprocess.run(["espeak", text], check=True)


def main():
    try:
        ip = get_public_ip()
        print("Public IP:", ip)

        coords = get_coords_for_ip(ip)
        if not coords:
            print("No coordinates found from providers. Exiting.", file=sys.stderr)
            sys.exit(2)
        lat, lon = coords
        print(f"Using coordinates: lat={lat}, lon={lon}")

        weather = fetch_open_meteo(lat, lon)
        print("Open-Meteo current_weather:", json.dumps(weather.get("current_weather", {}), indent=2))

        message = build_message(weather)
        print("Speakable message:", message)
        speak_espeak(message)

    except requests.HTTPError as e:
        print("HTTP error:", e, file=sys.stderr)
        sys.exit(3)
    except subprocess.CalledProcessError as e:
        print("espeak failed:", e, file=sys.stderr)
        sys.exit(4)
    except Exception as e:
        print("Unexpected error:", e, file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    main()
