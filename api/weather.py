from flask_compat import APIRouter
import os
from datetime import date as dt_date
from typing import Any

import requests
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()


def _qweather_key() -> str | None:
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        return None
    return key.strip() or None

def _qweather_jwt() -> str | None:
    jwt = os.getenv("WEATHER_JWT")
    if not jwt:
        return None
    return jwt.strip() or None

def _qweather_host() -> str:
    host = os.getenv("WEATHER_API_HOST")
    if not host:
        return "api.qweather.com"  # Fallback to standard commercial API host
    return host.strip()

def _qweather_url(path: str) -> str:
    return f"https://{_qweather_host()}{path}"

def _get_qweather_headers() -> dict[str, str]:
    headers = {}
    jwt = _qweather_jwt()
    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"
    else:
        key = _qweather_key()
        if key:
            headers["X-QW-Api-Key"] = key
    return headers


def _lookup_location_id(location: str) -> str | None:
    headers = _get_qweather_headers()
    if not headers:
        return None
    
    # 根据官方文档，如果是 API KEY 方式，需要把 key 放在参数或者 X-QW-Api-Key 里
    # 我们这里也支持把 key 放在 params 里，以防 headers 认证某些情况下被拦截
    params = {"location": location, "number": 1}
    key = _qweather_key()
    if key and not _qweather_jwt():
        params["key"] = key

    resp = requests.get(
        _qweather_url("/geo/v2/city/lookup"),
        params=params,
        headers=headers,
        timeout=10,
    )
    if resp.status_code != 200:
        raise Exception(f"Lookup failed: {resp.status_code} {resp.text}")
    
    data = resp.json()
    if str((data or {}).get("code")) not in {"200", ""}:
        raise Exception((data or {}).get("message") or "城市查询失败")
    locs = (data or {}).get("location") or []
    if not locs:
        return None
    return (locs[0] or {}).get("id")


def _to_alert_item(item: dict[str, Any]) -> dict[str, Any]:
    severity = "medium"
    level = (item.get("level") or "").strip()
    if level in {"1", "2"}:
        severity = "high"
    elif level in {"3"}:
        severity = "medium"
    elif level:
        severity = "low"

    title = (item.get("title") or "").strip()
    text = (item.get("text") or "").strip()
    pub_time = (item.get("pubTime") or "").strip()

    return {
        "type": "weather",
        "severity": severity,
        "title": f"【天气预警】{title}" if title else "【天气预警】气象预警",
        "description": text,
        "source": "和风天气",
        "time": pub_time or "刚刚",
    }


def _normalize_query_date(value: str | None) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    return dt_date.fromisoformat(raw).isoformat()


def _fetch_daily_weather(loc_id: str, headers: dict[str, str], key: str | None) -> list[dict[str, Any]]:
    params = {"location": loc_id}
    if key and not _qweather_jwt():
        params["key"] = key

    last_error = None
    for path in ("/v7/weather/7d", "/v7/weather/3d"):
        resp = requests.get(
            f"https://{_qweather_host()}{path}",
            params=params,
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if str((data or {}).get("code")) not in {"200", ""}:
                last_error = (data or {}).get("message") or "天气预报查询失败"
                continue
            daily = (data or {}).get("daily") or []
            return [item for item in daily if isinstance(item, dict)]
        last_error = f"Daily weather fetch failed: {resp.status_code} {resp.text}"

    raise Exception(last_error or "Daily weather fetch failed")


def _to_daily_weather_item(item: dict[str, Any]) -> dict[str, Any]:
    text_day = item.get("textDay") or ""
    text_night = item.get("textNight") or ""
    text = text_day if text_day == text_night or not text_night else f"{text_day}转{text_night}"

    return {
        "type": "forecast",
        "date": item.get("fxDate"),
        "tempMax": item.get("tempMax"),
        "tempMin": item.get("tempMin"),
        "text": text,
        "textDay": text_day,
        "textNight": text_night,
        "windDir": item.get("windDirDay") or item.get("windDirNight"),
        "windScale": item.get("windScaleDay") or item.get("windScaleNight"),
        "humidity": item.get("humidity"),
        "vis": item.get("vis"),
        "precip": item.get("precip"),
        "uvIndex": item.get("uvIndex"),
    }


# 获取天气信息的路由
@router.get("/api/v1/weather/alerts")
def get_weather_alerts(location: str, date: str | None = None):
    """
    获取目的地的实时天气/指定日期天气预报和天气预警信息（和风天气）。
    """

    headers = _get_qweather_headers()
    if not headers:
        return {
            "status": "error",
            "message": "天气服务未配置，请在后端配置 WEATHER_API_KEY 或 WEATHER_JWT",
            "location": location,
            "weather": None,
            "alerts": [],
        }

    try:
        query_date = _normalize_query_date(date)
        loc_id = _lookup_location_id(location)
        if not loc_id:
            return {
                "status": "success",
                "location": location,
                "weather": None,
                "alerts": [],
                "message": f"未找到城市“{location}”，请换用城市名或区县名查询",
            }

        key = _qweather_key()

        weather_info = None
        message = None
        if query_date:
            daily = _fetch_daily_weather(loc_id, headers, key)
            matched = next((item for item in daily if item.get("fxDate") == query_date), None)
            if matched:
                weather_info = _to_daily_weather_item(matched)
            else:
                available = [item.get("fxDate") for item in daily if item.get("fxDate")]
                if available:
                    message = f"暂未查询到 {query_date} 的天气预报，可查询范围：{available[0]} 至 {available[-1]}"
                else:
                    message = f"暂未查询到 {query_date} 的天气预报"
        else:
            # 1. 获取实时天气
            weather_params = {"location": loc_id}
            if key and not _qweather_jwt():
                weather_params["key"] = key

            weather_resp = requests.get(
                f"https://{_qweather_host()}/v7/weather/now",
                params=weather_params,
                headers=headers,
                timeout=10,
            )
            if weather_resp.status_code != 200:
                raise Exception(f"Weather fetch failed: {weather_resp.status_code} {weather_resp.text}")
            weather_data = weather_resp.json()
            if str((weather_data or {}).get("code")) not in {"200", ""}:
                raise Exception((weather_data or {}).get("message") or "实时天气查询失败")
            now_weather = (weather_data or {}).get("now") or {}
            
            if now_weather:
                weather_info = {
                    "type": "now",
                    "temp": now_weather.get("temp"),
                    "feelsLike": now_weather.get("feelsLike"),
                    "text": now_weather.get("text"),
                    "windDir": now_weather.get("windDir"),
                    "windScale": now_weather.get("windScale"),
                    "humidity": now_weather.get("humidity"),
                    "vis": now_weather.get("vis"),
                }

        # 2. 获取天气预警
        warning_message = None
        warning_params = {"location": loc_id}
        if key and not _qweather_jwt():
            warning_params["key"] = key

        alerts = []
        try:
            warning_resp = requests.get(
                f"https://{_qweather_host()}/v7/warning/now",
                params=warning_params,
                headers=headers,
                timeout=10,
            )
            if warning_resp.status_code != 200:
                raise Exception(f"Warning fetch failed: {warning_resp.status_code} {warning_resp.text}")
            warning_data = warning_resp.json()
            if str((warning_data or {}).get("code")) not in {"200", ""}:
                raise Exception((warning_data or {}).get("message") or "天气预警查询失败")
            warnings = (warning_data or {}).get("warning") or []
            alerts = [_to_alert_item(w) for w in warnings if isinstance(w, dict)]
        except Exception as warning_error:
            warning_message = f"天气预警暂不可用：{warning_error}"
        
        return {
            "status": "success", 
            "location": location, 
            "date": query_date,
            "weather": weather_info,
            "alerts": alerts,
            "message": message or warning_message,
        }
    except ValueError:
        return {
            "status": "error",
            "message": "日期格式不正确，请输入 YYYY-MM-DD，例如 2026-05-01",
            "location": location,
            "weather": None,
            "alerts": [],
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "location": location, "weather": None, "alerts": []}
