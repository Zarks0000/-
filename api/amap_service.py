import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def _amap_key() -> str:
    key = os.getenv("AMAP_WEB_API_KEY")
    if not key:
        raise RuntimeError("Missing AMAP_WEB_API_KEY in environment")
    return key


def _env_float(name: str, default: float) -> float:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def get_geocode(address: str) -> Optional[tuple[str, str]]:
    address = (address or "").strip()
    if not address:
        return None

    resp = requests.get(
        "https://restapi.amap.com/v3/geocode/geo",
        params={"address": address, "key": _amap_key()},
        timeout=_env_float("AMAP_GEOCODE_TIMEOUT", 4),
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "1":
        return None

    geocodes = data.get("geocodes") or []
    if not geocodes:
        return None

    loc = (geocodes[0].get("location") or "").strip()
    if not loc or "," not in loc:
        return None

    lng, lat = [s.strip() for s in loc.split(",", 1)]
    if not lng or not lat:
        return None
    return lng, lat


def get_driving_route(origin_lng: str, origin_lat: str, dest_lng: str, dest_lat: str, waypoints: Optional[str] = None) -> Optional[dict]:
    origin = f"{origin_lng},{origin_lat}"
    destination = f"{dest_lng},{dest_lat}"

    params = {
        "origin": origin,
        "destination": destination,
        "key": _amap_key(),
        "extensions": "all",
        "strategy": 0,
    }
    if waypoints:
        params["waypoints"] = waypoints

    resp = requests.get(
        "https://restapi.amap.com/v3/direction/driving",
        params=params,
        timeout=_env_float("AMAP_ROUTE_TIMEOUT", 6),
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "1":
        return None

    route = data.get("route") or {}
    paths = route.get("paths") or []
    if not paths:
        return None

    path0 = paths[0] or {}
    try:
        distance = int(float(path0.get("distance") or 0))
        duration = int(float(path0.get("duration") or 0))
    except Exception:
        return None

    if distance <= 0:
        return None
    polyline_parts = []
    steps = path0.get("steps") or []
    if isinstance(steps, list):
        for s in steps:
            if not isinstance(s, dict):
                continue
            pl = (s.get("polyline") or "").strip()
            if pl:
                polyline_parts.append(pl)
    polyline = ";".join(polyline_parts) if polyline_parts else None
    return {"distance": distance, "duration": duration, "polyline": polyline}
